# Setup Guide for New Laptop

This guide will help you set up and run both the backend and desktop app on a new machine.

## Prerequisites

- Python 3.8+ installed
- PostgreSQL set up (you mentioned you know how to do this)
- Git repository cloned

## Backend Setup

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend` directory with your PostgreSQL connection:

```bash
cd backend
# Create .env file
```

Example `.env` content (adjust for your PostgreSQL setup):
```
DATABASE_URL=postgresql://telemetry_user:your_password@localhost:5432/telemetry
SECRET_KEY=your-secret-key-here
S3_BUCKET=your-bucket
S3_REGION=your-region
```

**Note:** If you don't have a `.env` file, the backend will use SQLite by default (`sqlite:///./telemetry.db`).

### 3. Run the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`

You can verify it's working by visiting `http://localhost:8000` in your browser or running:
```bash
curl http://localhost:8000
```

## Desktop App Setup

### 1. Install Python Dependencies

```bash
cd desktop-app
pip install -r requirements.txt
```

### 2. Run the Desktop App

```bash
cd desktop-app
python main.py
```

This will open the PyQt6 GUI window where you can:
- Start the telemetry listener
- Start the ACC simulator
- Record sessions
- Upload sessions to the backend

## Running Both Together

1. **Terminal 1 - Start Backend:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Terminal 2 - Start Desktop App:**
   ```bash
   cd desktop-app
   python main.py
   ```

## Quick Verification

1. Backend is running: Visit `http://localhost:8000` - should see `{"message": "Backend running successfully"}`
2. Desktop app is running: GUI window should open
3. Test upload: In desktop app, record a session and try uploading it with backend URL `http://localhost:8000`

## Troubleshooting

### Backend Issues

- **Database connection errors:** Check your `.env` file has the correct `DATABASE_URL`
- **Port already in use:** Change the port with `--port 8001` or stop other services on port 8000
- **Module not found:** Make sure you've installed all dependencies from `requirements.txt`
- **uvloop installation error on Windows:** This is expected - `uvloop` is not available on Windows. The `requirements.txt` file has been updated to exclude it. Uvicorn will work fine without it (it just uses the default event loop).

### Desktop App Issues

- **PyQt6 import errors:** Make sure PyQt6 is installed: `pip install PyQt6`
- **Module not found:** Make sure you're running from the `desktop-app` directory and dependencies are installed

## Notes

- The backend runs on port 8000 by default
- The desktop app's telemetry listener runs on port 9996
- Session files are stored in `desktop-app/sessions/`
- Backend uses PostgreSQL if configured, otherwise falls back to SQLite
- **Windows compatibility:** The `requirements.txt` excludes `uvloop` (not available on Windows). For Unix/Linux systems, you can optionally install `requirements-unix.txt` which includes uvloop for better performance.

