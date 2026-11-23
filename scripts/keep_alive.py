#!/usr/bin/env python3
"""
VN AI Ecosystem - Keep-Alive Sentinel
Pings the n8n cloud instance at regular intervals to prevent free-tier spin-down.
"""
import sys
import time
import requests
from datetime import datetime

def ping_instance(target_url):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📡 Pinging {target_url}...")
    try:
        resp = requests.get(target_url, timeout=15)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ HTTP {resp.status_code} - Instance Active.")
        return True
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️  Ping failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 keep_alive.py <TARGET_URL> [INTERVAL_MINUTES]")
        sys.exit(1)
        
    url = sys.argv[1]
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    print(f"🚀 Starting Keep-Alive Sentinel for {url} every {interval} minutes.")
    while True:
        ping_instance(url)
        time.sleep(interval * 60)
