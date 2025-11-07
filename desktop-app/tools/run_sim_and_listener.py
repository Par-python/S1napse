import threading
import time
import queue
import gzip
import json
import sys
from pathlib import Path

# Ensure desktop-app/ is in sys.path so we can import telemetry.*
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# --- Imports from your app ---
from telemetry.listener import TelemetryListener
from telemetry.simulator import TrackSimulator
from telemetry.storage import SessionWriter


def run(duration=10, host="127.0.0.1", port=9996, rate_hz=20):
    q = queue.Queue()

    # listener will put payload dicts into q
    listener = TelemetryListener(port=port, out_queue=q)
    listener_thread = threading.Thread(target=listener.start, daemon=True)
    listener_thread.start()

    # brief wait to ensure listener is bound
    time.sleep(0.2)

    # session writer
    Path("sessions").mkdir(exist_ok=True)
    fname = time.strftime("sessions/session_%Y%m%d_%H%M%S.jsonl.gz")
    writer = SessionWriter(fname)

    # simulator (sends UDP to listener)
    sim = TrackSimulator(target_host=host, target_port=port, rate_hz=rate_hz)
    sim.set_track("Monza")
    sim.set_car("Porsche GT3 RS")

    sim_thread = threading.Thread(target=sim.run, daemon=True)
    sim_thread.start()

    print(f"Running simulator -> listener for {duration}s, writing to {fname} ...")
    t0 = time.time()

    try:
        while time.time() - t0 < duration:
            try:
                payload = q.get(timeout=1.0)
                # payload may already be dict (listener parsed JSON)
                if isinstance(payload, dict):
                    writer.write(payload)
                else:
                    # if listener put raw bytes/text, try to parse
                    try:
                        obj = json.loads(payload)
                        writer.write(obj)
                    except Exception:
                        pass
            except queue.Empty:
                continue  # no samples yet; loop again
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        sim.stop()
        listener.stop()
        writer.close()
        print("Stopped. Session saved to:", fname)

if __name__ == "__main__":
    dur = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0
    run(duration=dur)
