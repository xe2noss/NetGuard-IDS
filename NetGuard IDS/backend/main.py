import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from threading import Thread

from api.routes import router, manager, SessionLocal
from detection.engine import DetectionEngine
from capture.sniffer import PacketSniffer
from database import crud
from config import settings

# --- Logging Setup ---
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# --- FastAPI App ---
app = FastAPI(title="NetGuard IDS API")

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global Objects ---
detection_engine = DetectionEngine()
sniffer = None
main_event_loop = None  # <-- ADDED THIS LINE: To store the main event loop

async def process_alert(alert_data):
    """
    Saves an alert to the DB and broadcasts it via WebSocket.
    """
    db = SessionLocal()
    try:
        alert = crud.create_alert(db, alert_data)
        await manager.broadcast({
            "type": "new_alert",
            "data": alert.to_dict()
        })
    except Exception as e:
        logger.error(f"Error processing alert: {e}")
    finally:
        db.close()

def packet_callback(packet):
    """
    This function is called by Scapy for each packet.
    It runs in the sniffer's thread.
    """
    try:
        alert_data = detection_engine.analyze_packet(packet)
        if alert_data:
            # --- THIS IS THE CRITICAL FIX ---
            # Instead of asyncio.run(), we safely schedule the
            # coroutine on the main event loop from our thread.
            if main_event_loop:
                asyncio.run_coroutine_threadsafe(
                    process_alert(alert_data), 
                    main_event_loop
                )
            # ------------------------------------
    except Exception as e:
        logger.error(f"Error in packet callback: {e}")

def start_sniffer():
    """
    Initializes and starts the packet sniffer.
    """
    global sniffer
    sniffer = PacketSniffer(settings.NETWORK_INTERFACE, packet_callback)
    sniffer.start()

@app.on_event("startup")
async def startup_event():
    """
    On app startup, start the sniffer in a separate thread.
    """
    global main_event_loop
    main_event_loop = asyncio.get_running_loop() # <-- ADDED THIS LINE: Get and save the main loop

    logger.info("Starting NetGuard IDS Backend...")
    sniffer_thread = Thread(target=start_sniffer, daemon=True)
    sniffer_thread.start()

@app.on_event("shutdown")
async def shutdown_event():
    """
    On app shutdown, stop the sniffer.
    """
    if sniffer:
        sniffer.stop()
    logger.info("NetGuard IDS Backend shutting down.")

# --- Include API Routes ---
app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"message": "NetGuard IDS API", "status": "running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)