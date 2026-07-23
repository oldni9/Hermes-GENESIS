"""
===============================================================================
Hermes Runtime CLI Monitor
===============================================================================

Sprint 17A.5 Final Freeze:
- Added --no-color flag for CI environments.
===============================================================================
"""
import asyncio
import json
import sys
import os
import argparse
from collections import Counter

try:
    import websockets
except ImportError:
    print("Error: 'websockets' package is required. Install with: pip install websockets")
    sys.exit(1)

HERMES_WS_URL = os.getenv("HERMES_WS_URL", "ws://localhost:8000/ws/execution")

# ANSI Color Codes
COLORS = {
    "reset": "\033[0m",
    "blue": "\033[94m",
    "green": "\033[92m",
    "red": "\033[91m",
    "yellow": "\033[93m",
}

def get_color(event_type: str, trace_type: str = "") -> str:
    if event_type == "trace":
        if "finish" in trace_type or "completed" in trace_type:
            return COLORS["green"]
        elif "fail" in trace_type or "error" in trace_type:
            return COLORS["red"]
        elif "start" in trace_type:
            return COLORS["yellow"]
        return COLORS["blue"]
    elif "finished" in event_type:
        return COLORS["green"]
    elif "failed" in event_type or "gap" in event_type:
        return COLORS["red"]
    elif "cancelled" in event_type:
        return COLORS["yellow"]
    return COLORS["blue"]

async def monitor_execution(execution_id: str, output_json: bool, filter_type: str, show_stats: bool, use_color: bool):
    uri = f"{HERMES_WS_URL}/{execution_id}"
    if not output_json:
        print(f"Connecting to {uri}...\n")
    
    stats_counter = Counter()
    start_time = None
    end_time = None
    
    try:
        async with websockets.connect(uri) as websocket:
            if not output_json:
                print("Connected. Waiting for events...\n")
                print("-" * 80)
                
            while True:
                message = await websocket.recv()
                event = json.loads(message)
                
                event_type = event.get("event_type", "unknown")
                trace_type = event.get("trace_event_type", "")
                seq = event.get("sequence", 0)
                timestamp = event.get("timestamp", 0.0)
                
                if start_time is None:
                    start_time = timestamp
                end_time = timestamp
                
                # Stats tracking
                if event_type == "trace":
                    stats_counter[trace_type] += 1
                else:
                    stats_counter[event_type] += 1
                
                # Filtering
                if filter_type:
                    if filter_type not in event_type and filter_type not in trace_type:
                        continue
                
                # Output
                if output_json:
                    print(json.dumps(event))
                else:
                    payload = event.get("payload", {})
                    color = get_color(event_type, trace_type) if use_color else ""
                    reset = COLORS["reset"] if use_color else ""
                    
                    print(f"{color}[{timestamp:>10.2f}] Seq: {seq:<4} | {event_type:<25}{reset} | Payload: {json.dumps(payload)}")
                
                if event_type in ("execution_finished", "execution_failed", "execution_cancelled"):
                    if not output_json:
                        print("-" * 80)
                        print("Execution terminated. Closing connection.")
                    break
                    
    except websockets.exceptions.ConnectionClosed as e:
        if not output_json:
            print(f"\nConnection closed: {e}")
    except ConnectionRefusedError:
        if not output_json:
            print("\nError: Could not connect to Hermes Runtime API. Is the server running on http://localhost:8000?")
            
    if show_stats and start_time and end_time:
        duration = end_time - start_time
        print("\n" + "=" * 60)
        print("Execution Statistics")
        print("=" * 60)
        print(f"Duration: {duration:.2f} s")
        print("\nEvent Counts:")
        for event_type, count in stats_counter.most_common():
            print(f"  {event_type:<25} {count}")
        print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hermes Runtime CLI Monitor")
    parser.add_argument("execution_id", help="The ID of the execution to monitor")
    parser.add_argument("--json", action="store_true", help="Output raw JSON lines")
    parser.add_argument("--filter", type=str, help="Filter events by type (e.g., 'llm', 'tool', 'trace')")
    parser.add_argument("--stats", action="store_true", help="Print summary statistics at the end")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output for CI environments")
    
    args = parser.parse_args()
    asyncio.run(monitor_execution(args.execution_id, args.json, args.filter, args.stats, not args.no_color))

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture