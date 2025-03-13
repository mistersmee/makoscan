import os
import time
import pyshark
from gi.repository import GLib

def capture_packets(interface, filter_text, packet_limit, time_limit, stop_event, counter_callback, completion_callback):
    """
    Perform packet capture using PyShark with capture filters and time limits.

    Args:
        interface (str): Network interface to capture from
        filter_text (str): Filter expression for capturing packets
        packet_limit (int): Maximum number of packets to capture
        time_limit (int): Maximum time in seconds to run capture
        stop_event (threading.Event): Event to signal capture termination
        counter_callback (callable): Function to call with packet count updates
        completion_callback (callable): Function to call when capture completes
    """
    pcap_file = "capture.pcap"
    try:
        print(f"Starting capture on {interface} with filter '{filter_text}'...")
        # Use a capture filter if specified
        capture_filter = None if filter_text == "None" else filter_text.lower()

        # Create a PyShark LiveCapture object
        capture = pyshark.LiveCapture(interface=interface, output_file=pcap_file, bpf_filter=capture_filter)

        packet_count = 0
        start_time = time.time()  # Record the start time

        for packet in capture.sniff_continuously():
            # Check time limit
            elapsed_time = time.time() - start_time
            if stop_event.is_set() or (time_limit and elapsed_time >= time_limit) or (packet_limit and packet_count >= packet_limit):
                break

            packet_count += 1
            counter_callback(packet_count)

        capture.close()
        print(f"Capture complete. File saved as {pcap_file}.")

    except Exception as e:
        print(f"Error during capture: {e}")
    finally:
        completion_callback()
