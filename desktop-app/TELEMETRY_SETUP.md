# Telemetry Setup Guide for Assetto Corsa / Assetto Corsa Competizione

This guide explains how to configure your game to send telemetry data to the listener.

## Quick Setup

### For Assetto Corsa Competizione (ACC)

1. **Launch ACC** and go to **Settings**
2. Navigate to **General Settings** or **Telemetry Settings**
3. Find **"UDP Telemetry"** or **"UDP Output"** section
4. Enable **"Enable UDP Telemetry"** or toggle it ON
5. Set the following:
   - **UDP Port**: `9996` (or your preferred port)
   - **UDP IP**: `127.0.0.1` (localhost)
   - **Update Rate**: `20 Hz` (recommended)
6. **Save** and **Apply** settings

### For Assetto Corsa (AC)

1. **Launch Assetto Corsa**
2. Go to **Options** → **General** or **Telemetry**
3. Enable **"UDP Output"** or **"UDP Telemetry"**
4. Set:
   - **Port**: `9996` (or your preferred port)
   - **IP**: `127.0.0.1`
5. **Apply** settings

## Configuring the Listener

1. **Open the desktop app**
2. In the **Listener Configuration** section:
   - Set **UDP Port** to match the port you configured in the game (default: `9996`)
   - Select **Listener Mode**:
     - **ACC (JSON)** for Assetto Corsa Competizione
     - **Assetto Corsa (Binary)** for Assetto Corsa
3. Click **"Start Listener"**
4. The status should show: `"Status: listening on UDP 9996 (ACC (JSON))"`

## Troubleshooting

### Port Already in Use Error

If you get an error that the port is already in use:

1. **Try a different port**:
   - Change port in both the game settings AND the listener
   - Good ports to try: `9000`, `9997`, `9998`, `9999`

2. **Check what's using the port**:
   ```powershell
   netstat -ano | findstr :9996
   ```
   This will show if something else is using the port.

3. **Close other telemetry apps**:
   - Close any other apps that might be listening to telemetry (e.g., SimHub, RaceLab, etc.)
   - Make sure no other instance of this app is running

4. **Restart the game**:
   - Sometimes the game reserves the port
   - Close ACC/AC completely and restart it

### No Data Received

If the listener starts but you don't see any data:

1. **Verify game settings**:
   - Make sure UDP telemetry is ENABLED in game settings
   - Check that the port matches (game port = listener port)
   - Verify IP is set to `127.0.0.1` (localhost)

2. **Check firewall**:
   - Windows Firewall might be blocking UDP packets
   - Try temporarily disabling firewall to test
   - Or add an exception for the game and Python

3. **Test with simulator**:
   - Use the "Start ACC Simulator" button to test if the listener works
   - If simulator works but game doesn't, the issue is with game configuration

4. **Verify listener mode**:
   - ACC uses JSON mode
   - AC uses Binary mode
   - Make sure you selected the correct mode

### Windows Permission Error (WinError 10013)

If you get a permission error:

1. **Try a different port** (e.g., 9000, 9997, 9998)
2. **Run as administrator** (right-click → Run as administrator)
3. **Check Windows reserved ports**:
   ```powershell
   netsh interface ipv4 show excludedportrange protocol=udp
   ```
   If 9996 is in a reserved range, use a different port

## Default Ports

- **Default listener port**: `9996`
- **Common alternatives**: `9000`, `9997`, `9998`, `9999`

## Testing

1. **Start the listener** in the app
2. **Start a session** in the game (practice, race, etc.)
3. **Check the status** - you should see telemetry data updating
4. **Start session recording** to save telemetry data

## Notes

- The game must be running and in a session (not just in menus) for telemetry to be sent
- UDP is connectionless, so the listener must be running BEFORE you start a session in the game
- The listener can receive data from both ACC and AC, but you need to select the correct mode
- Port must match between game settings and listener settings

