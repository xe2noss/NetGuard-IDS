from .signature_rules import SignatureDetector
from scapy.all import IP, TCP, UDP

class DetectionEngine:
    """
    The main engine that analyzes packets and formats alerts.
    """
    def __init__(self):
        self.signature_detector = SignatureDetector()
    
    def analyze_packet(self, packet):
        """
        Analyzes a single packet and returns alert data if a threat is found.
        """
        detection_result = self.signature_detector.detect(packet)
        
        if detection_result:
            alert_data = {
                "source_ip": packet[IP].src,
                "dest_ip": packet[IP].dst,
                "protocol": packet.sprintf("%IP.proto%"),
                "threat_type": detection_result["threat_type"],
                "severity": detection_result["severity"],
                "description": detection_result["description"],
                "raw_packet_summary": packet.summary()
            }
            
            if packet.haslayer(TCP):
                alert_data["source_port"] = packet[TCP].sport
                alert_data["dest_port"] = packet[TCP].dport
            elif packet.haslayer(UDP):
                alert_data["source_port"] = packet[UDP].sport
                alert_data["dest_port"] = packet[UDP].dport
            
            return alert_data
        
        return None