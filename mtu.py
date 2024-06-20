#!/usr/bin/env python3

import sys
import subprocess

def get_mtu(target_ip):
    # Default IP, falls kein Parameter angegeben ist
    if not target_ip:
        target_ip = "1.1.1.1"

    try:
        # Versuche, ein Paket mit 1500 Bytes zu senden
        cmd = f"ping {target_ip} -l 1500 -f -n 1" if sys.platform.startswith("win") else f"ping {target_ip} -s 1500 -M do -c 1"
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            print(f"MTU for {target_ip}: 1500 bytes (default)")
            return

        # Reduziere schrittweise die Paketgröße, bis die maximale MTU gefunden ist
        for size in range(1499, 1400, -1):
            cmd = f"ping {target_ip} -l {size} -f -n 1" if sys.platform.startswith("win") else f"ping {target_ip} -s {size} -M do -c 1"
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                print(f"MTU for {target_ip}: {size} bytes")
                return

        print(f"Unable to determine MTU for {target_ip}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    target_ip = sys.argv[1] if len(sys.argv) > 1 else None
    get_mtu(target_ip)
