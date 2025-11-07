# ui/visualization_widget.py
import matplotlib
# Use Qt backend compatible with PyQt6
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
except ImportError:
    # Fallback for older matplotlib versions
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QScrollArea
)
from collections import deque
import time


class VisualizationWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Per-lap data storage (resets each lap)
        self.lap_data = {
            'time': [],      # Time within lap (0 to lap_time_s)
            'speed': [],     # Speed in km/h
            'throttle': [],  # Throttle in %
            'brake': [],     # Brake in %
            'steering': [],  # Steering in degrees
            'gear': [],      # Gear number
            'rpm': []        # RPM
        }
        
        # Current values for display
        self.current_speed = 0.0
        self.current_throttle = 0.0
        self.current_brake = 0.0
        self.current_steering = 0.0
        self.current_gear = 0
        self.current_rpm = 0
        self.current_lap_time = 0.0
        self.current_lap = 0
        self.best_lap_time = None
        
        # Track lap state
        self.lap_start_time = None
        self.last_lap = -1
        self.track_length_m = 5793.0  # Monza track length (will be updated from telemetry)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Current values display
        current_layout = QHBoxLayout()
        
        speed_label = QLabel("Speed: — km/h")
        speed_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.speed_value_label = speed_label
        
        throttle_label = QLabel("Gas: — %")
        throttle_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #4CAF50;")
        self.throttle_value_label = throttle_label
        
        brake_label = QLabel("Brake: — %")
        brake_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #F44336;")
        self.brake_value_label = brake_label
        
        steering_label = QLabel("Steering: — °")
        steering_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.steering_value_label = steering_label
        
        gear_label = QLabel("Gear: —")
        gear_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.gear_value_label = gear_label
        
        rpm_label = QLabel("RPM: —")
        rpm_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.rpm_value_label = rpm_label
        
        lap_label = QLabel("Lap: —")
        lap_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.lap_value_label = lap_label
        
        current_layout.addWidget(speed_label)
        current_layout.addWidget(throttle_label)
        current_layout.addWidget(brake_label)
        current_layout.addWidget(steering_label)
        current_layout.addWidget(gear_label)
        current_layout.addWidget(rpm_label)
        current_layout.addWidget(lap_label)
        current_layout.addStretch()
        
        layout.addLayout(current_layout)
        
        # Create scroll area for charts
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # Speed chart
        self.speed_fig = Figure(figsize=(10, 2))
        self.speed_canvas = FigureCanvas(self.speed_fig)
        self.speed_ax = self.speed_fig.add_subplot(111)
        self.speed_ax.set_title("Speed in kph")
        self.speed_ax.set_xlabel("Distance/Time")
        self.speed_ax.set_ylabel("Speed (km/h)")
        self.speed_ax.grid(True, alpha=0.3)
        scroll_layout.addWidget(self.speed_canvas)
        
        # Brake/Gas chart
        self.brake_gas_fig = Figure(figsize=(10, 2))
        self.brake_gas_canvas = FigureCanvas(self.brake_gas_fig)
        self.brake_gas_ax = self.brake_gas_fig.add_subplot(111)
        self.brake_gas_ax.set_title("Brake/Gas in %")
        self.brake_gas_ax.set_xlabel("Distance/Time")
        self.brake_gas_ax.set_ylabel("Percentage (%)")
        self.brake_gas_ax.grid(True, alpha=0.3)
        scroll_layout.addWidget(self.brake_gas_canvas)
        
        # Steering chart
        self.steering_fig = Figure(figsize=(10, 2))
        self.steering_canvas = FigureCanvas(self.steering_fig)
        self.steering_ax = self.steering_fig.add_subplot(111)
        self.steering_ax.set_title("Steering in °")
        self.steering_ax.set_xlabel("Distance/Time")
        self.steering_ax.set_ylabel("Steering (°)")
        self.steering_ax.grid(True, alpha=0.3)
        scroll_layout.addWidget(self.steering_canvas)
        
        # Gear chart
        self.gear_fig = Figure(figsize=(10, 2))
        self.gear_canvas = FigureCanvas(self.gear_fig)
        self.gear_ax = self.gear_fig.add_subplot(111)
        self.gear_ax.set_title("Gear in #")
        self.gear_ax.set_xlabel("Distance/Time")
        self.gear_ax.set_ylabel("Gear (#)")
        self.gear_ax.grid(True, alpha=0.3)
        scroll_layout.addWidget(self.gear_canvas)
        
        # RPM chart
        self.rpm_fig = Figure(figsize=(10, 2))
        self.rpm_canvas = FigureCanvas(self.rpm_fig)
        self.rpm_ax = self.rpm_fig.add_subplot(111)
        self.rpm_ax.set_title("RPMs in revs/min")
        self.rpm_ax.set_xlabel("Distance/Time")
        self.rpm_ax.set_ylabel("RPM (revs/min)")
        self.rpm_ax.grid(True, alpha=0.3)
        scroll_layout.addWidget(self.rpm_canvas)
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
        
    def reset_lap_data(self):
        """Reset all lap data for a new lap."""
        self.lap_data = {
            'time': [],
            'speed': [],
            'throttle': [],
            'brake': [],
            'steering': [],
            'gear': [],
            'rpm': []
        }
        self.lap_start_time = None
        
    def update_telemetry(self, data: dict):
        """Update visualization with new telemetry data."""
        # Update track length if available
        if "position_m" in data and data["position_m"] is not None:
            # Estimate track length from position (it resets to 0 each lap)
            # We'll use a known value or estimate from max position
            pass  # Keep using default or update if we detect it
        
        # Detect lap completion
        if "lap" in data and data["lap"] is not None:
            new_lap = data["lap"]
            if new_lap != self.current_lap and self.current_lap > 0:
                # Lap completed - reset data for new lap
                self.reset_lap_data()
            self.current_lap = new_lap
        
        # Update best lap time
        if "best_lap_time_s" in data and data["best_lap_time_s"] is not None:
            self.best_lap_time = data["best_lap_time_s"]
        
        # Get current lap time (x-axis for charts)
        if "lap_time_s" in data and data["lap_time_s"] is not None:
            self.current_lap_time = data["lap_time_s"]
        
        # Only collect data if we're in a valid lap
        if self.current_lap >= 0 and self.current_lap_time is not None:
            # Use position_m as x-axis (distance) if available, otherwise use lap_time_s
            if "position_m" in data and data["position_m"] is not None:
                x_value = data["position_m"]
            else:
                x_value = self.current_lap_time
            
            # Store data for current lap
            self.lap_data['time'].append(x_value)
            
            # Speed
            if "speed" in data and data["speed"] is not None:
                self.current_speed = data["speed"]
                self.lap_data['speed'].append(self.current_speed)
            else:
                self.lap_data['speed'].append(0)
            
            # Throttle
            if "throttle" in data and data["throttle"] is not None:
                self.current_throttle = data["throttle"]
                self.lap_data['throttle'].append(self.current_throttle)
            else:
                self.lap_data['throttle'].append(0)
            
            # Brake
            if "brake" in data and data["brake"] is not None:
                self.current_brake = data["brake"]
                self.lap_data['brake'].append(self.current_brake)
            else:
                self.lap_data['brake'].append(0)
            
            # Steering
            if "steer" in data and data["steer"] is not None:
                self.current_steering = data["steer"] * 180.0  # Convert to degrees if needed
                self.lap_data['steering'].append(self.current_steering)
            elif "steering" in data and data["steering"] is not None:
                self.current_steering = data["steering"]
                self.lap_data['steering'].append(self.current_steering)
            else:
                self.lap_data['steering'].append(0)
            
            # Gear
            if "gear" in data and data["gear"] is not None:
                self.current_gear = int(data["gear"])
                self.lap_data['gear'].append(self.current_gear)
            else:
                self.lap_data['gear'].append(0)
            
            # RPM
            if "rpm" in data and data["rpm"] is not None:
                self.current_rpm = int(data["rpm"])
                self.lap_data['rpm'].append(self.current_rpm)
            else:
                self.lap_data['rpm'].append(0)
        
        # Update UI
        self.update_labels()
        self.update_charts()
        
    def update_labels(self):
        """Update text labels with current values."""
        self.speed_value_label.setText(f"Speed: {self.current_speed:.2f} km/h")
        self.throttle_value_label.setText(f"Gas: {self.current_throttle:.2f} %")
        self.brake_value_label.setText(f"Brake: {self.current_brake:.2f} %")
        self.steering_value_label.setText(f"Steering: {self.current_steering:.2f} °")
        self.gear_value_label.setText(f"Gear: {self.current_gear}")
        self.rpm_value_label.setText(f"RPM: {self.current_rpm}")
        self.lap_value_label.setText(f"Lap: {self.current_lap}")
        
    def update_charts(self):
        """Update all charts with current lap data."""
        if len(self.lap_data['time']) == 0:
            # No data yet - show placeholder
            for ax in [self.speed_ax, self.brake_gas_ax, self.steering_ax, self.gear_ax, self.rpm_ax]:
                ax.clear()
                ax.text(0.5, 0.5, 'No lap data yet', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=12, alpha=0.5)
                ax.grid(True, alpha=0.3)
            self.speed_canvas.draw()
            self.brake_gas_canvas.draw()
            self.steering_canvas.draw()
            self.gear_canvas.draw()
            self.rpm_canvas.draw()
            return
        
        time_data = self.lap_data['time']
        
        # Speed chart
        self.speed_ax.clear()
        self.speed_ax.set_title("Speed in kph")
        self.speed_ax.set_xlabel("Distance/Time")
        self.speed_ax.set_ylabel("Speed (km/h)")
        self.speed_ax.grid(True, alpha=0.3)
        # Always set x-axis to track length (fixed, doesn't scroll)
        self.speed_ax.set_xlim(0, self.track_length_m)
        if len(self.lap_data['speed']) > 0:
            self.speed_ax.plot(time_data, self.lap_data['speed'], 'b-', linewidth=1.5)
            # Show current value in top right
            self.speed_ax.text(0.98, 0.98, f"Speed: {self.current_speed:.2f}", 
                              transform=self.speed_ax.transAxes,
                              horizontalalignment='right', verticalalignment='top',
                              bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        self.speed_canvas.draw()
        
        # Brake/Gas chart
        self.brake_gas_ax.clear()
        self.brake_gas_ax.set_title("Brake/Gas in %")
        self.brake_gas_ax.set_xlabel("Distance/Time")
        self.brake_gas_ax.set_ylabel("Percentage (%)")
        self.brake_gas_ax.grid(True, alpha=0.3)
        # Always set x-axis to track length (fixed, doesn't scroll)
        self.brake_gas_ax.set_xlim(0, self.track_length_m)
        if len(self.lap_data['throttle']) > 0:
            self.brake_gas_ax.plot(time_data, self.lap_data['throttle'], 'g-', linewidth=1.5, label='Gas')
            self.brake_gas_ax.plot(time_data, self.lap_data['brake'], 'r-', linewidth=1.5, label='Brake')
            self.brake_gas_ax.legend(loc='upper right')
            # Show current values
            self.brake_gas_ax.text(0.98, 0.98, f"Gas: {self.current_throttle:.2f}\nBrake: {self.current_brake:.2f}", 
                                  transform=self.brake_gas_ax.transAxes,
                                  horizontalalignment='right', verticalalignment='top',
                                  bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        self.brake_gas_canvas.draw()
        
        # Steering chart
        self.steering_ax.clear()
        self.steering_ax.set_title("Steering in °")
        self.steering_ax.set_xlabel("Distance/Time")
        self.steering_ax.set_ylabel("Steering (°)")
        self.steering_ax.grid(True, alpha=0.3)
        # Always set x-axis to track length (fixed, doesn't scroll)
        self.steering_ax.set_xlim(0, self.track_length_m)
        if len(self.lap_data['steering']) > 0:
            self.steering_ax.plot(time_data, self.lap_data['steering'], 'b-', linewidth=1.5)
            # Show current value
            self.steering_ax.text(0.98, 0.98, f"Steering: {self.current_steering:.2f}", 
                                 transform=self.steering_ax.transAxes,
                                 horizontalalignment='right', verticalalignment='top',
                                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        self.steering_canvas.draw()
        
        # Gear chart
        self.gear_ax.clear()
        self.gear_ax.set_title("Gear in #")
        self.gear_ax.set_xlabel("Distance/Time")
        self.gear_ax.set_ylabel("Gear (#)")
        self.gear_ax.grid(True, alpha=0.3)
        # Always set x-axis to track length (fixed, doesn't scroll)
        self.gear_ax.set_xlim(0, self.track_length_m)
        if len(self.lap_data['gear']) > 0:
            self.gear_ax.plot(time_data, self.lap_data['gear'], 'b-', linewidth=1.5, drawstyle='steps-post')
            # Show current value
            self.gear_ax.text(0.98, 0.98, f"Gear: {self.current_gear}", 
                             transform=self.gear_ax.transAxes,
                             horizontalalignment='right', verticalalignment='top',
                             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        self.gear_canvas.draw()
        
        # RPM chart
        self.rpm_ax.clear()
        self.rpm_ax.set_title("RPMs in revs/min")
        self.rpm_ax.set_xlabel("Distance/Time")
        self.rpm_ax.set_ylabel("RPM (revs/min)")
        self.rpm_ax.grid(True, alpha=0.3)
        # Always set x-axis to track length (fixed, doesn't scroll)
        self.rpm_ax.set_xlim(0, self.track_length_m)
        if len(self.lap_data['rpm']) > 0:
            self.rpm_ax.plot(time_data, self.lap_data['rpm'], 'b-', linewidth=1.5)
            # Show current value
            self.rpm_ax.text(0.98, 0.98, f"RPM: {self.current_rpm}", 
                            transform=self.rpm_ax.transAxes,
                            horizontalalignment='right', verticalalignment='top',
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        self.rpm_canvas.draw()
