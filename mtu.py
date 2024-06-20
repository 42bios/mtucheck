#!/usr/bin/env python3
import sys
import subprocess
import argparse
import socket
import struct
import random
import time

# ICMP Echo Request type and code
ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0

# Default payload size in bytes
DEFAULT_PAYLOAD_SIZE = 56

# Default maximum probe size in bytes
DEFAULT_MAX_PROBE_SIZE = 10000

# Default timeout in seconds
DEFAULT_TIMEOUT = 3

# Default number of retries
DEFAULT_RETRIES = 3

# Function to calculate checksum for ICMP packet
def checksum(data):
    if len(data) % 2 != 0:
        data += b'\x00'
    s = sum(struct.unpack('!H', data[i:i+2])[0] for i in range(0, len(data), 2))
    s = (s >> 16) + (s & 0xffff)
    s += s >> 16
    return ~s & 0xffff

# Function to send ICMP echo request and receive reply
def send_icmp_request(dest_addr, payload_size, timeout):
    # Create ICMP socket
    icmp = socket.getprotobyname('icmp')
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except socket.error:
        sys.exit("Socket could not be created. Run as root/Administrator.")

    # Generate a random payload
    payload = bytearray(random.getrandbits(8) for _ in range(payload_size))

    # ICMP header
    header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, 0, random.randint(0, 65535), 1)

    # Calculate ICMP checksum
    chksum = checksum(header + payload)

    # Complete ICMP packet with checksum
    packet = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, chksum, random.randint(0, 65535), 1) + payload

    # Send packet
    try:
        sock.sendto(packet, (dest_addr, 1))
        start_time = time.time()
        sock.settimeout(timeout)
        reply, addr = sock.recvfrom(1024)
        end_time = time.time()
        return len(reply), end_time - start_time
    except socket.timeout:
        return None, None
    except socket.error as e:
        print(f"Socket error: {e}")
        return None, None
    finally:
        sock.close()

# Function to perform MTU discovery
def perform_mtu_discovery(dest_addr, max_probe_size, timeout, retries, traceroute=False, fragment=False, verbose=False):
    print(f"Performing MTU discovery to {dest_addr}")

    probe_size = max_probe_size
    low = 0
    high = max_probe_size

    while low <= high:
        mid = (low + high) // 2
        success, response_time = send_icmp_request(dest_addr, mid, timeout)

        if success:
            if verbose:
                print(f"+ ICMP payload of {mid} bytes succeeded.")
            if mid == high:
                break
            low = mid
        else:
            if verbose:
                print(f"- ICMP payload of {mid} bytes failed.")

            high = mid - 1

        time.sleep(1)  # To avoid flooding the network

    print(f"Path MTU: {low} bytes")

# Main function to parse arguments and run MTU discovery
def main():
    parser = argparse.ArgumentParser(description="PathMTU: Tool for MTU discovery via ICMP echo requests")
    parser.add_argument("destination", help="Destination IP address or hostname")
    parser.add_argument("-m", "--max-probe-size", type=int, default=DEFAULT_MAX_PROBE_SIZE,
                        help="Maximum probe size in bytes (default: 10000)")
    parser.add_argument("-t", "--traceroute", action="store_true",
                        help="Perform MTU discovery for each hop along the path to destination")
    parser.add_argument("-f", "--fragmentation", action="store_true",
                        help="Enable fragmentation mode (allow ICMP packets to be fragmented)")
    parser.add_argument("-w", "--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help="Timeout in seconds for each probe (default: 3)")
    parser.add_argument("-r", "--retries", type=int, default=DEFAULT_RETRIES,
                        help="Number of retries in case of probe timeout (default: 3)")
    parser.add_argument("-d", "--verbose", action="store_true",
                        help="Enable verbose output for debugging")
    
    args = parser.parse_args()

    perform_mtu_discovery(args.destination, args.max_probe_size, args.timeout, args.retries,
                          traceroute=args.traceroute, fragment=args.fragmentation, verbose=args.verbose)

if __name__ == "__main__":
    main()
