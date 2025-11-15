🛡️ NetGuard IDS – Network Intrusion Detection System

NetGuard IDS is a lightweight, real-world-deployable Intrusion Detection System built using Python (FastAPI + Scapy), React, and Docker.
It monitors live network traffic, detects common cyberattacks, and displays alerts on a modern real-time dashboard.

This project is designed for students, beginners, and professionals who want to understand IDS architecture, packet sniffing, and signature-based threat detection.

🚀 Features
🔍 Real-Time Detection

Packet sniffing using Scapy

Monitors traffic on a specified network interface

🛑 Signature-Based Attack Detection

Port Scans

SSH Brute Force Attempts

Nmap Xmas Scans

ICMP Floods

📈 Stateful Traffic Analysis

Tracks activity over time (e.g., multiple SSH login attempts within seconds)

💻 Live Dashboard

Built with React + Vite

Real-time alerts pushed via WebSockets

Charts & analytics for:

Top attacking IPs

Most frequent alert types

🐳 Fully Containerized

One-command deployment using Docker Compose

Clean 3-tier architecture:

Frontend (React)

Backend (FastAPI)

Database (PostgreSQL)

🏗️ System Architecture

NetGuard consists of three Docker services:

1️⃣ Frontend (Nginx + React)

Displays alert dashboard

Communicates with backend via REST API & WebSockets

2️⃣ Backend (FastAPI, Python)

Handles:

Packet sniffing (Scapy) in a background thread

Detection engine

Logging alerts to database

/api REST endpoints

/api/ws WebSocket for real-time updates

3️⃣ Database (PostgreSQL)

Stores all alert logs

Provides persistent analytics data

⚙️ How to Run – Quick Start
Prerequisites

Docker

Docker Compose

📥 Installation
1. Clone the Repository
git clone https://github.com/your-username/netguard-ids.git
cd netguard-ids

2. Create Environment File
cp .env.example .env

3. Configure .env

Edit your .env and update:

DB_PASSWORD → set a secure password

NETWORK_INTERFACE → set your active network interface

Check interface using:

Linux/Mac: ifconfig or ip addr

Common names:

eth0, en0, wlan0

▶️ Start the Entire System
docker-compose build
docker-compose up -d

🌐 Access the Application
Component	URL
Frontend Dashboard	http://localhost:3000

Backend API Docs	http://localhost:8000/docs
🧪 How to Test Attacks

Run these commands to generate test alerts:

1. Port Scan
nmap -p 1-1000 localhost

2. Xmas Scan
nmap -sX localhost

3. SSH Brute Force Simulation

Run 5+ times:

ssh user@localhost

4. ICMP Flood

(Requires root)

sudo ping -f localhost -c 200

📌 Future Enhancements

Anomaly detection using ML

Advanced signature database

Threat severity scoring system

Email/SMS alerting

Container-level monitoring

🤝 Contributing

Contributions are welcome!
Feel free to open issues or submit PRs.
