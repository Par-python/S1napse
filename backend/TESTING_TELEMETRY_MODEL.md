# Testing TelemetrySample Model

This guide explains how to test the new `TelemetrySample` model that stores individual telemetry data points.

## Prerequisites

1. **Backend is running:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Database is initialized** (tables will be created automatically on first run)

## Step 1: Restart Backend to Create New Table

The `TelemetrySample` table will be created automatically when the backend starts:

```bash
cd backend
uvicorn app.main:app --reload
```

You should see SQL logs showing the table creation.

## Step 2: Upload a Session

Upload a session file - the backend will now parse and store all telemetry samples:

```bash
cd desktop-app
python tools/upload_session.py
```

Or use curl:

```bash
curl -X POST "http://localhost:8000/sessions/upload" \
  -F "file=@sessions/session_20251107_094447.jsonl.gz" \
  -F "driver_name=Test Driver" \
  -F "car=Porsche GT3 RS" \
  -F "track=Monza" \
  -F "duration=30.04"
```

The response should now include `telemetry_samples_count`:

```json
{
  "id": 1,
  "filename": "...",
  "driver_name": "Test Driver",
  "car": "Porsche GT3 RS",
  "track": "Monza",
  "duration": 30.04,
  "telemetry_samples_count": 600,
  "message": "Session uploaded successfully"
}
```

## Step 3: Query Telemetry Samples

### Get all telemetry for a session:

```bash
curl http://localhost:8000/sessions/1/telemetry
```

### Get limited samples (pagination):

```bash
# Get first 100 samples
curl "http://localhost:8000/sessions/1/telemetry?limit=100&offset=0"

# Get next 100 samples
curl "http://localhost:8000/sessions/1/telemetry?limit=100&offset=100"
```

### Response format:

```json
{
  "session_id": 1,
  "count": 100,
  "samples": [
    {
      "id": 1,
      "lap": 1,
      "sector": 1,
      "position_m": 123.45,
      "lap_time_s": 45.123,
      "sector_time_s": 15.456,
      "speed": 250.5,
      "rpm": 7500,
      "throttle": 85.2,
      "brake": 0.0,
      "gear": 5,
      "steer": 0.05,
      "ts": 1699123456.789
    },
    ...
  ]
}
```

## Step 4: Verify in Database

### Using SQLite:

```bash
cd backend
sqlite3 telemetry.db

# Count telemetry samples
SELECT COUNT(*) FROM telemetrysample;

# View sample data
SELECT id, lap, sector, position_m, speed, rpm, throttle, brake, gear 
FROM telemetrysample 
WHERE session_id = 1 
LIMIT 10;

# Check relationship
SELECT s.id, s.driver_name, COUNT(t.id) as sample_count
FROM session s
LEFT JOIN telemetrysample t ON s.id = t.session_id
GROUP BY s.id;
```

### Using PostgreSQL:

```bash
psql -U telemetry_user -d telemetry

# Count telemetry samples
SELECT COUNT(*) FROM telemetrysample;

# View sample data
SELECT id, lap, sector, position_m, speed, rpm, throttle, brake, gear 
FROM telemetrysample 
WHERE session_id = 1 
LIMIT 10;
```

## Step 5: Test with Python

Create a test script:

```python
# test_telemetry.py
import requests

# Get session
session = requests.get("http://localhost:8000/sessions/1").json()
print(f"Session: {session['driver_name']} - {session['track']}")

# Get telemetry samples
telemetry = requests.get("http://localhost:8000/sessions/1/telemetry?limit=10").json()
print(f"\nFound {telemetry['count']} samples (showing first 10):")

for sample in telemetry['samples']:
    print(f"  Lap {sample['lap']}, Sector {sample['sector']}: "
          f"Speed={sample['speed']:.1f} km/h, "
          f"Gear={sample['gear']}, "
          f"RPM={sample['rpm']}")
```

Run it:

```bash
python test_telemetry.py
```

## Expected Results

1. **Upload should succeed** and return `telemetry_samples_count` > 0
2. **Query endpoint should return** telemetry samples with all fields
3. **Database should contain** rows in the `telemetrysample` table
4. **Relationship should work** - you can query samples by session_id

## Troubleshooting

### No telemetry samples stored:
- Check that the uploaded file is a valid `.jsonl.gz` file
- Check backend logs for parsing errors
- Verify the file contains valid JSON lines

### Database errors:
- Make sure database is initialized: restart backend
- Check database connection in `.env` or `config.py`
- For PostgreSQL, ensure user has CREATE TABLE permissions

### Performance issues:
- Large sessions (1000+ samples) may take a few seconds to upload
- Use pagination when querying large datasets
- Consider adding indexes on `session_id` and `ts` for better performance

## Next Steps

Once testing is complete:
1. Add indexes for better query performance
2. Add filtering endpoints (by lap, sector, etc.)
3. Add aggregation endpoints (average speed per lap, etc.)
4. Integrate with frontend to visualize the data

