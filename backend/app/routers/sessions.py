from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from sqlmodel import Session as DBSession, select
from datetime import datetime
import shutil
import gzip
import json
from pathlib import Path
from ..models import Session, TelemetrySample
from ..schemas import SessionCreate
from ..db import engine

router = APIRouter()

# Directory to store uploaded session files
UPLOAD_DIR = Path("uploads/sessions")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def extract_metadata_from_file(file_path: Path) -> dict:
    """
    Extract metadata from a session file by reading the first and last samples.
    Returns dict with car, track, and duration.
    """
    metadata = {
        "car": None,
        "track": None,
        "duration": None,
    }
    
    try:
        with gzip.open(file_path, "rt", encoding="utf-8") as f:
            first = None
            last = None
            
            for line in f:
                try:
                    obj = json.loads(line.strip())
                    if not obj:
                        continue
                    if first is None:
                        first = obj
                    last = obj
                except json.JSONDecodeError:
                    continue
            
            if first and last:
                metadata["car"] = first.get("car") or last.get("car")
                metadata["track"] = first.get("track") or last.get("track")
                
                first_ts = first.get("ts")
                last_ts = last.get("ts")
                if first_ts and last_ts:
                    metadata["duration"] = last_ts - first_ts
    except Exception as e:
        print(f"Error extracting metadata from file: {e}")
    
    return metadata

@router.post("/upload")
async def upload_session(
    file: UploadFile = File(...),
    driver_name: str = Form(...),
    car: str = Form(...),
    track: str = Form(...),
    duration: float = Form(...)
):
    """
    Upload a session file and store metadata in the database.
    The file is saved locally (can be extended to S3 later).
    """
    try:
        # Validate file extension
        if not file.filename or not file.filename.endswith(('.jsonl.gz', '.gz')):
            raise HTTPException(status_code=400, detail="File must be a .jsonl.gz file")
        
        # Generate unique filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{driver_name.replace(' ', '_')}_{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Verify file was saved and has content
        if not file_path.exists() or file_path.stat().st_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty or could not be saved")
        
        # Extract metadata from file if provided values are missing/default
        if car == "Unknown" or track == "Unknown" or duration == 0.0:
            file_metadata = extract_metadata_from_file(file_path)
            if file_metadata["car"]:
                car = file_metadata["car"]
            if file_metadata["track"]:
                track = file_metadata["track"]
            if file_metadata["duration"] is not None:
                duration = file_metadata["duration"]
        
        # Store metadata in database
        session_record = Session(
            driver_name=driver_name,
            car=car,
            track=track,
            duration=duration,
            upload_time=datetime.utcnow()
        )
        
        with DBSession(engine) as db:
            db.add(session_record)
            db.commit()
            db.refresh(session_record)
            
            # Extract values while session is still active
            session_id = session_record.id
            upload_time_iso = session_record.upload_time.isoformat()
            
            # Parse and store telemetry samples
            sample_count = 0
            error_count = 0
            try:
                with gzip.open(file_path, "rt", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        try:
                            line = line.strip()
                            if not line:
                                continue
                            
                            data = json.loads(line)
                            if not data or not isinstance(data, dict):
                                continue
                            
                            # Create telemetry sample
                            sample = TelemetrySample(
                                session_id=session_id,
                                source=data.get("source", "UNKNOWN"),
                                car=data.get("car", car),
                                track=data.get("track", track),
                                lap=data.get("lap", 0),
                                segment=data.get("segment", ""),
                                sector=data.get("sector", 0),
                                position_m=data.get("position_m", 0.0),
                                lap_time_s=data.get("lap_time_s", 0.0),
                                sector_time_s=data.get("sector_time_s", 0.0),
                                best_lap_time_s=data.get("best_lap_time_s"),
                                best_sector_1_s=data.get("best_sector_1_s"),
                                best_sector_2_s=data.get("best_sector_2_s"),
                                best_sector_3_s=data.get("best_sector_3_s"),
                                speed=data.get("speed", 0.0),
                                rpm=data.get("rpm", 0),
                                throttle=data.get("throttle", 0.0),
                                brake=data.get("brake", 0.0),
                                gear=data.get("gear", 0),
                                steer=data.get("steer", 0.0),
                                in_pitlane=data.get("in_pitlane", False),
                                is_curve=data.get("is_curve", False),
                                ts=data.get("ts", 0.0)
                            )
                            db.add(sample)
                            sample_count += 1
                            
                            # Commit in batches for performance
                            if sample_count % 1000 == 0:
                                db.commit()
                        except json.JSONDecodeError as e:
                            error_count += 1
                            if error_count <= 5:  # Log first 5 JSON errors
                                print(f"JSON decode error on line {line_num}: {e}")
                            continue  # Skip invalid JSON lines
                        except Exception as e:
                            error_count += 1
                            if error_count <= 5:  # Log first 5 errors
                                print(f"Error parsing telemetry sample on line {line_num}: {e}")
                                import traceback
                                traceback.print_exc()
                            continue
                
                # Final commit for remaining samples
                if sample_count > 0:
                    db.commit()
                    print(f"Successfully stored {sample_count} telemetry samples for session {session_id}")
                else:
                    print(f"Warning: No telemetry samples found in file {file_path}")
            except Exception as e:
                # If telemetry parsing fails, still return the session
                print(f"Warning: Failed to parse telemetry samples: {e}")
                import traceback
                traceback.print_exc()
                # Try to commit any samples that were added before the error
                try:
                    if sample_count > 0:
                        db.commit()
                except:
                    pass
        
        return {
            "id": session_id,
            "filename": safe_filename,
            "file_path": str(file_path),
            "driver_name": driver_name,
            "car": car,
            "track": track,
            "duration": duration,
            "upload_time": upload_time_iso,
            "telemetry_samples_count": sample_count,
            "message": "Session uploaded successfully"
        }
    
    except Exception as e:
        # Clean up file if database insert failed
        if 'file_path' in locals() and file_path.exists():
            try:
                file_path.unlink()
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/")
async def list_sessions():
    """List all uploaded sessions."""
    with DBSession(engine) as db:
        statement = select(Session)
        sessions = db.exec(statement).all()
        return [
            {
                "id": s.id,
                "driver_name": s.driver_name,
                "car": s.car,
                "track": s.track,
                "duration": s.duration,
                "upload_time": s.upload_time.isoformat() if s.upload_time else None,
            }
            for s in sessions
        ]


@router.get("/{session_id}")
async def get_session(session_id: int):
    """Get a specific session by ID."""
    with DBSession(engine) as db:
        session = db.get(Session, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return {
            "id": session.id,
            "driver_name": session.driver_name,
            "car": session.car,
            "track": session.track,
            "duration": session.duration,
            "upload_time": session.upload_time.isoformat() if session.upload_time else None,
        }

@router.get("/{session_id}/telemetry")
async def get_session_telemetry(session_id: int, limit: int = 1000, offset: int = 0):
    """Get telemetry samples for a specific session."""
    with DBSession(engine) as db:
        session = db.get(Session, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        statement = (
            select(TelemetrySample)
            .where(TelemetrySample.session_id == session_id)
            .order_by(TelemetrySample.ts)
            .limit(limit)
            .offset(offset)
        )
        samples = db.exec(statement).all()
        
        return {
            "session_id": session_id,
            "count": len(samples),
            "samples": [
                {
                    "id": s.id,
                    "lap": s.lap,
                    "sector": s.sector,
                    "position_m": s.position_m,
                    "lap_time_s": s.lap_time_s,
                    "sector_time_s": s.sector_time_s,
                    "speed": s.speed,
                    "rpm": s.rpm,
                    "throttle": s.throttle,
                    "brake": s.brake,
                    "gear": s.gear,
                    "steer": s.steer,
                    "ts": s.ts,
                }
                for s in samples
            ]
        }
