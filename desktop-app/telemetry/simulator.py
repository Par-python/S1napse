# telemetry/simulator.py
"""
Monza + Porsche GT3 RS telemetry simulator.

Usage:
    from telemetry.simulator import TrackSimulator
    sim = TrackSimulator(target_host="127.0.0.1", target_port=9996, rate_hz=20)
    sim.set_track("Monza")
    sim.set_car("Porsche GT3 RS")
    # run in a background thread:
    # threading.Thread(target=sim.run, daemon=True).start()
    # to stop: sim.stop()
"""

import socket
import time
import json
import random
import math

# Monza official length ~5.793 km (5793 m)
MONZA_LENGTH_M = 5793.0

# Simplified Monza segments (name, length_m, target_speed_kmh)
MONZA_SEGMENTS = [
    ("Rettifilo", 1200, 320),
    ("Variante del Rettifilo", 200, 90),
    ("Curva Grande", 900, 170),
    ("Lesmo 1", 300, 120),
    ("Lesmo 2", 300, 120),
    ("Variante della Roggia", 200, 100),
    ("Back Straight", 900, 320),
    ("Parabolica", 600, 140),
    ("Ascari-ish/Approach", 893, 220),
]

CAR_PRESETS = {
    "Porsche GT3 RS": {
        "mass_kg": 1420,
        "max_speed_kmh": 315,
        "max_rpm": 9000,
        "redline_rpm": 8800,
        "idle_rpm": 900,
        "gears": 6,
        "gear_speed_kmh": [0, 60, 110, 160, 220, 275, 330],
        "accel_m_s2": 6.5,
        "brake_m_s2": 10.0,
        "power_curve": 1.0,
    }
}


def clamp(x, a, b):
    return max(a, min(b, x))


class TrackSimulator:
    def __init__(self, target_host="127.0.0.1", target_port=9996, rate_hz=20, random_seed=None):
        self.host = target_host
        self.port = target_port
        self.rate_hz = rate_hz
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = False

        self.track_name = "Monza"
        self.track_segments = MONZA_SEGMENTS
        self.track_length_m = MONZA_LENGTH_M

        self.car_name = "Porsche GT3 RS"
        self.car = CAR_PRESETS[self.car_name].copy()

        self.random = random.Random(random_seed)

        self.lap = 0
        self.position_m = 0.0
        self.speed_ms = 0.0
        self.gear = 1

    def set_track(self, name: str):
        if name.lower() == "monza":
            self.track_name = "Monza"
            self.track_segments = MONZA_SEGMENTS
            self.track_length_m = MONZA_LENGTH_M
        else:
            raise ValueError("Unknown track")

    def set_car(self, name: str):
        if name in CAR_PRESETS:
            self.car_name = name
            self.car = CAR_PRESETS[name].copy()
        else:
            raise ValueError("Unknown car preset")

    def stop(self):
        self.running = False

    def run(self):
        """Blocking run; call stop() to exit (or use in a thread)."""
        self.running = True
        t0 = time.time()
        lap_start = t0
        self.lap = 1
        self.position_m = 0.0
        self.speed_ms = 0.0
        self.gear = 1

        tick_dt = 1.0 / self.rate_hz
        while self.running:
            loop_start = time.time()

            seg_name, seg_len, target_kmh = self._segment_for_position(self.position_m)
            target_ms = (target_kmh / 3.6)

            speed_error = target_ms - self.speed_ms
            if speed_error > 0:
                desired_acc = clamp(speed_error * 0.7 + self.random.gauss(0, 0.2), -self.car["brake_m_s2"], self.car["accel_m_s2"])
            else:
                desired_acc = clamp(speed_error * 0.9 + self.random.gauss(0, 0.5), -self.car["brake_m_s2"], self.car["accel_m_s2"])

            speed_kmh = self.speed_ms * 3.6
            drag_acc = -0.0005 * (speed_kmh ** 2) / self.car["mass_kg"]
            net_acc = desired_acc + drag_acc

            self.speed_ms += net_acc * tick_dt
            if self.speed_ms < 0:
                self.speed_ms = 0.0

            self.position_m += self.speed_ms * tick_dt

            if self.position_m >= self.track_length_m:
                self.position_m -= self.track_length_m
                self.lap += 1
                lap_start = time.time()

            self.gear = self._gear_for_speed(speed_kmh)

            gear_ratio_factor = 60
            rpm = int(clamp(self.speed_ms * 3.6 * gear_ratio_factor / max(1, self.gear), self.car["idle_rpm"], self.car["max_rpm"]))
            rpm += int(self.random.gauss(0, 50))

            throttle_pct = 0.0
            brake_pct = 0.0
            if net_acc >= 0.1:
                throttle_pct = clamp(100 * (net_acc / (self.car["accel_m_s2"] + 0.001)), 0, 100)
                throttle_pct = round(throttle_pct * self.random.uniform(0.9, 1.05), 1)
            elif net_acc < -0.5:
                brake_pct = clamp(100 * (-net_acc / (self.car["brake_m_s2"] + 0.001)), 0, 100)
                brake_pct = round(brake_pct * self.random.uniform(0.9, 1.05), 1)

            steer = self._steer_for_segment(seg_name, self.position_m)
            lap_time = time.time() - lap_start

            payload = {
                "source": "SIM",
                "car": self.car_name,
                "track": self.track_name,
                "lap": self.lap,
                "segment": seg_name,
                "position_m": round(self.position_m, 2),
                "lap_time_s": round(lap_time, 3),
                "speed": round(self.speed_ms * 3.6, 2),
                "rpm": rpm,
                "throttle": throttle_pct,
                "brake": brake_pct,
                "gear": int(self.gear),
                "steer": round(steer, 3),
                "ts": time.time()
            }

            try:
                self.sock.sendto(json.dumps(payload).encode("utf-8"), (self.host, self.port))
            except Exception:
                pass

            elapsed = time.time() - loop_start
            to_sleep = tick_dt - elapsed
            if to_sleep > 0:
                time.sleep(to_sleep)

        try:
            self.sock.close()
        except Exception:
            pass

    def _segment_for_position(self, pos_m):
        p = pos_m % self.track_length_m
        acc = 0.0
        for name, length, speed in self.track_segments:
            if acc <= p < acc + length:
                return name, length, speed
            acc += length
        return self.track_segments[-1][0], self.track_segments[-1][1], self.track_segments[-1][2]

    def _gear_for_speed(self, speed_kmh):
        thresholds = self.car.get("gear_speed_kmh", [])
        gear = 1
        for g in range(1, min(len(thresholds), self.car["gears"] + 1)):
            if speed_kmh >= thresholds[g]:
                gear = g
        return clamp(gear, 1, self.car["gears"])

    def _steer_for_segment(self, seg_name, pos_m):
        corner_keywords = ["Variante", "Lesmo", "Parabolica", "Curva", "Roggio", "Approach", "Ascari", "Lesmo"]
        base = 0.0
        for kw in corner_keywords:
            if kw.lower() in seg_name.lower():
                seg_start = self._segment_start_position(seg_name)
                seg_length = self._segment_length_by_name(seg_name)
                if seg_length <= 0:
                    return 0.0
                rel = ((pos_m - seg_start) % self.track_length_m) / seg_length
                steer_peak = math.sin(math.pi * clamp(rel, 0.0, 1.0))
                base = steer_peak * self.random.uniform(0.4, 0.85)
                if self.random.random() < 0.5:
                    base = -base
                return base
        return round(self.random.gauss(0.0, 0.005), 3)

    def _segment_start_position(self, seg_name):
        acc = 0.0
        for name, length, speed in self.track_segments:
            if name == seg_name:
                return acc
            acc += length
        return 0.0

    def _segment_length_by_name(self, seg_name):
        for name, length, speed in self.track_segments:
            if name == seg_name:
                return length
        return 0.0