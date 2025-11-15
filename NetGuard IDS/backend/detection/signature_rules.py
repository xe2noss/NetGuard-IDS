from scapy.all import IP, TCP, ICMP, UDP
from datetime import datetime, timedelta
from collections import defaultdict, deque

class SignatureDetector:
    """
    Holds the logic for signature-based detection.
    This class is stateful to track attacks over time.
    """
    def __init__(self):
        # {src_ip: [timestamp, ...]}
        self.ssh_attempts = defaultdict(lambda: deque(maxlen=10))
        # {src_ip: {port_num, ...}}
        self.port_scans = defaultdict(set)
        # {src_ip: [timestamp, ...]}
        self.icmp_counts = defaultdict(lambda: deque(maxlen=200))

    def check_xmas_scan(self, packet):
        """
        Detects Nmap Xmas Scan (TCP flags FIN, PSH, URG set)
        """
        if packet.haslayer(TCP):
            flags = packet[TCP].flags
            # 0x29 = FIN (0x01) + PSH (0x08) + URG (0x20)
            if flags & 0x29 == 0x29:
                return {
                    "threat_type": "Nmap Xmas Scan",
                    "severity": "HIGH",
                    "description": "TCP packet with FIN, PSH, URG flags detected"
                }
        return None

    def check_ssh_brute_force(self, packet):
        """
        Detects > 5 SSH connection attempts in 60 seconds
        """
        if packet.haslayer(TCP) and packet[TCP].dport == 22:
            src_ip = packet[IP].src
            now = datetime.now()
            
            # Add current attempt
            self.ssh_attempts[src_ip].append(now)
            
            # Filter out old attempts
            while self.ssh_attempts[src_ip] and (now - self.ssh_attempts[src_ip][0] > timedelta(seconds=60)):
                self.ssh_attempts[src_ip].popleft()
                
            if len(self.ssh_attempts[src_ip]) >= 5:
                # Clear to avoid repeated alerts
                self.ssh_attempts[src_ip].clear()
                return {
                    "threat_type": "SSH Brute Force",
                    "severity": "CRITICAL",
                    "description": f"More than 5 SSH attempts in 60s from {src_ip}"
                }
        return None

    def check_port_scan(self, packet):
        """
        Detects scanning of 20+ ports from a single source
        """
        if packet.haslayer(TCP):
            src_ip = packet[IP].src
            dst_port = packet[TCP].dport
            
            self.port_scans[src_ip].add(dst_port)
            
            if len(self.port_scans[src_ip]) >= 20:
                # Clear to avoid repeated alerts
                self.port_scans[src_ip].clear()
                return {
                    "threat_type": "Port Scan",
                    "severity": "HIGH",
                    "description": f"Source {src_ip} scanned {len(self.port_scans[src_ip])}+ ports"
                }
        return None

    def check_icmp_flood(self, packet):
        """
        Detects > 100 ICMP requests in 10 seconds
        """
        if packet.haslayer(ICMP) and packet[ICMP].type == 8: # Echo Request
            src_ip = packet[IP].src
            now = datetime.now()
            
            self.icmp_counts[src_ip].append(now)
            
            while self.icmp_counts[src_ip] and (now - self.icmp_counts[src_ip][0] > timedelta(seconds=10)):
                self.icmp_counts[src_ip].popleft()
                
            if len(self.icmp_counts[src_ip]) >= 100:
                self.icmp_counts[src_ip].clear()
                return {
                    "threat_type": "ICMP Flood",
                    "severity": "MEDIUM",
                    "description": f"More than 100 ICMP requests in 10s from {src_ip}"
                }
        return None

    def detect(self, packet):
        """
        Run all detection methods against a packet.
        """
        if not packet.haslayer(IP):
            return None
        
        checks = [
            self.check_xmas_scan,
            self.check_ssh_brute_force,
            self.check_port_scan,
            self.check_icmp_flood
        ]
        
        for check in checks:
            result = check(packet)
            if result:
                return result
        
        return None