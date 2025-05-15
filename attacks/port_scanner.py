import socket
import sys
import threading
import time

def port_scanner(target_host, start_port, end_port):
    """
    Simple multi-threaded port scanner.
    """
    print(f"[*] Starting port scan on {target_host} from port {start_port} to {end_port}")
    
    def scan_port(port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            
            result = s.connect_ex((target_host, port))
            if result == 0:
                print(f"[+] Port {port}: OPEN")
            s.close()
        except:
            pass
    
    threads = []
    for port in range(start_port, end_port + 1):
        thread = threading.Thread(target=scan_port, args=(port,))
        threads.append(thread)
        thread.start()
        
        if len(threads) >= 100:
            for thread in threads:
                thread.join()
            threads = []
            
    for thread in threads:
        thread.join()
    
    print("[*] Port scan completed.")

if __name__ == "__main__":
    print("=== PORT SCANNER SIMULATION ===")
    print("Usage: python port_scanner.py [target_host] [start_port] [end_port]")
    
    target = "127.0.0.1"  
    start_p = 1
    end_p = 100
    
    # Parse command line arguments if provided
    if len(sys.argv) >= 2:
        target = sys.argv[1]
    if len(sys.argv) >= 3:
        start_p = int(sys.argv[2])
    if len(sys.argv) >= 4:
        end_p = int(sys.argv[3])
        
    port_scanner(target, start_p, end_p)
