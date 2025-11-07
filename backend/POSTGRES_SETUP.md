# PostgreSQL Setup Guide

This guide will help you migrate from SQLite to PostgreSQL for the telemetry backend.

## Step 1: Install PostgreSQL

### macOS (using Homebrew)
```bash
brew install postgresql@15
brew services start postgresql@15
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Windows
Download and install from: https://www.postgresql.org/download/windows/

## Step 2: Create Database and User

1. **Access PostgreSQL:**
   ```bash
   psql postgres
   ```
   (On macOS with Homebrew, you might need: `psql -d postgres`)

2. **Create a database:**
   ```sql
   CREATE DATABASE telemetry;
   ```

3. **Create a user (optional but recommended):**
   ```sql
   CREATE USER telemetry_user WITH PASSWORD 'your_secure_password_here';
   GRANT ALL PRIVILEGES ON DATABASE telemetry TO telemetry_user;
   \c telemetry
   GRANT ALL ON SCHEMA public TO telemetry_user;
   GRANT CREATE ON SCHEMA public TO telemetry_user;
   ```

4. **Exit psql:**
   ```sql
   \q
   ```

## Step 3: Update Configuration

### Option A: Using Environment Variables (Recommended)

Create a `.env` file in the `backend` directory:

```bash
cd backend
touch .env
```

Add to `.env`:
```env
DATABASE_URL=postgresql://telemetry_user:your_secure_password_here@localhost:5432/telemetry
```

### Option B: Update config.py directly

Edit `backend/app/config.py` and change the default:
```python
DATABASE_URL: str = "postgresql://telemetry_user:your_secure_password_here@localhost:5432/telemetry"
```

**Note:** Using `.env` is more secure and flexible.

## Step 4: Test Connection

Test the connection before starting the server:

```bash
cd backend
python -c "from app.config import settings; from app.db import engine; print('Connection successful!' if engine.connect() else 'Failed')"
```

Or start the server:
```bash
uvicorn app.main:app --reload
```

If successful, you should see:
```
INFO:     Database initialized successfully
INFO:     Application startup complete.
```

## Step 5: Migrate Existing Data (Optional)

If you have existing SQLite data you want to migrate:

### Export from SQLite
```bash
cd backend
sqlite3 telemetry.db .dump > telemetry_dump.sql
```

### Convert and Import to PostgreSQL
1. Edit `telemetry_dump.sql` to remove SQLite-specific syntax
2. Connect to PostgreSQL:
   ```bash
   psql -U telemetry_user -d telemetry
   ```
3. Import:
   ```sql
   \i telemetry_dump.sql
   ```

**Note:** For a fresh setup, you can just delete `telemetry.db` and let the app create new tables.

## Step 6: Verify Setup

1. **Check tables exist:**
   ```bash
   psql -U telemetry_user -d telemetry -c "\dt"
   ```

2. **Test upload:**
   ```bash
   cd desktop-app
   python tools/upload_session.py
   ```

3. **Verify in database:**
   ```bash
   psql -U telemetry_user -d telemetry -c "SELECT * FROM session;"
   ```

## Troubleshooting

### Connection refused
- Check PostgreSQL is running: `brew services list` (macOS) or `sudo systemctl status postgresql` (Linux)
- Verify port 5432 is not blocked by firewall

### Authentication failed
- Check username/password in `.env` file
- Verify user exists: `psql -U postgres -c "\du"`
- Reset password: `ALTER USER telemetry_user WITH PASSWORD 'new_password';`

### Database does not exist
- Create it: `createdb telemetry` or use psql as shown above

### Permission denied
- Grant database privileges: `GRANT ALL PRIVILEGES ON DATABASE telemetry TO telemetry_user;`
- Grant schema privileges (IMPORTANT for creating tables):
  ```sql
  \c telemetry
  GRANT ALL ON SCHEMA public TO telemetry_user;
  GRANT CREATE ON SCHEMA public TO telemetry_user;
  ```
- For existing tables: `GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO telemetry_user;`

## Production Considerations

For production, consider:
- Strong passwords
- SSL connections: `DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require`
- Connection pooling
- Regular backups
- Environment-specific `.env` files (don't commit `.env` to git)

