# Testing Visualizations Guide

This guide explains how to test the new visualization features (lap times, speeds, sectors) in the desktop app.

## Prerequisites

1. **Install dependencies:**
   ```bash
   cd desktop-app
   pip install -r requirements.txt
   ```
   
   This will install matplotlib (and other dependencies) if not already installed.

## Quick Test

### Step 1: Start the Desktop App

```bash
cd desktop-app
python main.py
```

The app window should open with two tabs:
- **Control** tab: Contains all the control buttons
- **Visualizations** tab: Contains the charts and metrics

### Step 2: Start the Simulator and Listener

1. Click **"Start Listener"** button
   - Status should show: "Status: listening on UDP 9996"

2. Click **"Start ACC Simulator"** button
   - Status should show: "Status: Monza simulator running -> sending UDP to 127.0.0.1:9996"
   - The simulator will start generating telemetry data

3. (Optional) Click **"Start Session Recording"** to save the session

### Step 3: View Visualizations

1. Click on the **"Visualizations"** tab

2. You should see:
   - **Lap Times section** (top left):
     - Current lap time
     - Best lap time (updates as you complete laps)
     - Current lap number
   
   - **Sector Times section** (top center):
     - Current sector times for S1, S2, S3
     - Best sector times for each sector
   
   - **Speed section** (top right):
     - Current speed in km/h
   
   - **Three charts** (bottom row):
     - **Lap Times History**: Shows completed lap times as a line chart
     - **Speed Over Time**: Real-time speed graph
     - **Sector Times Comparison**: Bar chart comparing current vs best sector times

### Step 4: Watch the Data Update

- The visualizations update in real-time (every 100ms) as telemetry data arrives
- After completing a full lap, you should see:
  - The lap time appear in the "Lap Times History" chart
  - Sector times updating as you progress through sectors
  - Speed graph showing speed variations around the track

## What to Expect

### Initial State (No Data Yet)
- Charts show placeholder text: "No lap data yet", "No speed data yet", "No sector data yet"
- All labels show "—" (dash) for missing values

### After Starting Simulator
- **Speed chart**: Should immediately start showing a red line with speed data
- **Speed label**: Shows current speed updating in real-time
- **Sector labels**: Show current sector and sector times as you progress

### After Completing Laps
- **Lap Times History**: Each completed lap appears as a blue dot on the chart
- **Best lap time**: Green dashed line shows your best lap time
- **Sector comparison**: Bars appear showing best sector times (green) and current sector time (blue)

### Typical Data Flow
1. **Lap 0**: Speed data starts flowing, sector times start accumulating
2. **Lap 1**: First lap completes → appears in lap times chart
3. **Lap 2+**: Subsequent laps appear, best lap time updates if you improve
4. **Sectors**: As you complete sectors, best sector times get recorded and displayed

## Testing Different Scenarios

### Test 1: Basic Functionality
- Start listener and simulator
- Switch to Visualizations tab
- Verify all three charts are visible
- Verify speed data is updating

### Test 2: Lap Completion
- Let the simulator run for at least one full lap (~90-120 seconds)
- Watch for lap completion in the "Lap Times History" chart
- Verify best lap time updates after first lap

### Test 3: Sector Times
- Watch the sector times update as you progress through sectors
- Verify the sector comparison chart shows bars for completed sectors
- Check that current sector time only shows for the active sector

### Test 4: Multiple Laps
- Let it run for 3-5 laps
- Verify multiple points appear in the lap times chart
- Check that the best lap time is the minimum of all completed laps

## Troubleshooting

### Charts Not Showing
- **Issue**: Charts are blank or show errors
- **Solution**: 
  - Make sure matplotlib is installed: `pip install matplotlib`
  - Check that you're on the "Visualizations" tab
  - Restart the app

### No Data in Charts
- **Issue**: Charts show "No data yet" even after starting simulator
- **Solution**:
  - Verify listener is started (green status)
  - Verify simulator is started (status shows "running")
  - Check that you're on the Visualizations tab (data only updates when tab is active)
  - Wait a few seconds for data to accumulate

### Lap Times Not Appearing
- **Issue**: Speed chart works but lap times don't appear
- **Solution**:
  - Lap times only appear after completing a full lap
  - Wait for at least one complete lap (~90-120 seconds)
  - Check that the lap number is incrementing in the UI

### Performance Issues
- **Issue**: App becomes slow or unresponsive
- **Solution**:
  - The speed chart stores up to 1000 data points by default
  - Close and restart the app if it becomes too slow
  - Consider reducing `max_data_points` in `VisualizationWidget` if needed

## Command Line Alternative

If you prefer to test without the GUI, you can still generate session data:

```bash
cd desktop-app
python tools/run_sim_and_listener.py 60  # Run for 60 seconds
```

Then open the app and the visualizations will work with recorded sessions if you load them (though currently the app only shows live data).

## Expected Visual Results

### Lap Times Chart
- Blue line with dots showing lap times
- Green dashed horizontal line showing best lap time
- X-axis: Lap number (1, 2, 3, ...)
- Y-axis: Time in seconds

### Speed Chart
- Red line showing speed over time
- X-axis: Time in seconds (relative to session start)
- Y-axis: Speed in km/h
- Should show speed variations (slower in corners, faster on straights)

### Sector Comparison Chart
- Green bars: Best sector times
- Blue bars: Current sector time (only for active sector)
- X-axis: Sector number (1, 2, 3)
- Y-axis: Time in seconds

## Next Steps

Once you've verified the visualizations work:
1. Record longer sessions to see more lap data
2. Try to improve your lap times and watch the best times update
3. Compare sector times to identify which sectors need improvement
4. Use the speed graph to analyze speed patterns around the track

