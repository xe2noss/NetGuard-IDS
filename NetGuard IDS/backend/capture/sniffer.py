from scapy.all import sniff
import logging

logger = logging.getLogger(__name__)

class PacketSniffer:
    def __init__(self, interface, callback):
        self.interface = interface
        self.callback = callback
        self.running = False
        logger.info(f"Sniffer initialized on interface: {self.interface}")

    def start(self):
        self.running = True
        logger.info("Starting packet sniffer...")
        try:
            # This is the Scapy function that listens to the network
            sniff(
                iface=self.interface,
                prn=self.callback,
                store=False,
                stop_filter=lambda p: not self.running
            )
        except Exception as e:
            logger.error(f"---!!! SNIFFER FAILED TO START !!!---")
            logger.error(f"Error: {e}")
            logger.error("This is likely a permissions issue or the wrong interface.")
            logger.error(f"Check that NETWORK_INTERFACE='{self.interface}' is correct.")
            logger.error("Ensure 'cap_add: [NET_ADMIN, NET_RAW]' is in docker-compose.yml")

    def stop(self):
        self.running = False
        logger.info("Stopping packet sniffer...")