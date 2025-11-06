# telemetry/simulator.py
import socket
import time
import json
import random
import threading

class Simulator:
    """
    A small UDP telemetry simulator. Set mode to "ACC" or "AC".
    Runs at ~20 Hz by default.
    """

    def __init__(self, target_host="127.0.0.1", target_port=9996, rate_hz=20):
        self.host = target_host
        self.port = target_port
        self.rate_hz = rate_hz
        self.running = False
        self.mode = "ACC"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def set_mode(self, mode: str):
        if mode.upper() in ("ACC", "AC"):
            self.mode = mode.upper()

    def run(self):
        self.running = True
        t0 = time.time()
        sim_time = 0.0
        while self.running:
            payload = self._make_payload(sim_time)
            data = json.dumps(payload).encode()
            try:
                self.sock.sendto(data, (self.host, self.port))
            except Exception:
                pass
            time.sleep(1.0 / self.rate_hz)
            sim_time = time.time() - t0

    def stop(self):
        self.running = False

    def _make_payload(self, sim_time: float):
        """
        Return a payload shaped like ACC or AC telemetry.
        We keep the fields simple: speed(kmh), rpm, throttle(%), gear, brake, steering (-1..1)
        """
        # base values that vary with sim_time
        base_speed = 60 + 40 * (0.5 + 0.5 * random.sin(sim_time)) if hasattr(random, "sin") else 60 + 40 * (0.5 + 0.5 * (random.random()-0.5))
        # simpler deterministic-ish osc if no sin: use noise
        base_speed = 80 * (0.5 + 0.5 * (random.random()))
        if self.mode == "ACC":
            # ACC-like: structured fields
            payload = {
                "source": "ACC",
                "ts": time.time(),
                "speed": round(base_speed + random.uniform(-3, 3), 2),
                "rpm": int(3000 + (payload_offset:=random.uniform(-200, 200)) + (payload_offset*0)),  # simple
                "throttle": round(max(0, min(100, random.gauss(40, 30))), 1),
                "gear": random.choice([3,4,5,6]),
                "brake": round(max(0, min(100, random.gauss(5, 10))), 1),
                "steer": round(random.uniform(-1, 1), 3)
            }
            # fix rpm more reasonably
            payload["rpm"] = int(1500 + payload["speed"] * 40 + random.randint(-200,200))
            return payload
        else:
            # AC-like: slightly different naming/units
            payload = {
                "source": "AC",
                "ts": time.time(),
                "speed": round(base_speed + random.uniform(-2, 2), 2),
                "engine_rpm": int(1200 + base_speed * 50 + random.randint(-300, 300)),
                "throttle_pct": round(max(0, min(100, random.gauss(50, 25))), 1),
                "gear": random.choice([2,3,4,5]),
                "brake_pct": round(max(0, min(100, random.gauss(2, 8))), 1),
                "steering": round(random.uniform(-1, 1), 3)
            }
            # normalize naming to match listener expectations if you want
            # keep both sets so you can test parser differences
            return payload
