# Quick PostgreSQL Setup

## Option 1: Automated Setup (Recommended)

Run the setup script:

```bash
cd backend
./setup_postgres.sh
```

This will:
- Check if PostgreSQL is installed
- Create database and user
- Generate `.env` file with connection string

## Option 2: Manual Setup

### 1. Install PostgreSQL

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux:**
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Create Database

```bash
# Connect to PostgreSQL
psql postgres

# In psql, run:
CREATE DATABASE telemetry;
CREATE USER telemetry_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE telemetry TO telemetry_user;
\c telemetry
GRANT ALL ON SCHEMA public TO telemetry_user;
GRANT CREATE ON SCHEMA public TO telemetry_user;
\q
```

### 3. Create .env File

```bash
cd backend
cat > .env <<EOF
DATABASE_URL=postgresql://telemetry_user:your_secure_password@localhost:5432/telemetry
SECRET_KEY=$(openssl rand -hex 32)
EOF
```

### 4. Test Connection

```bash
# Start the backend
uvicorn app.main:app --reload
```

You should see: `INFO: Database initialized successfully`

### 5. Verify

```bash
# Check tables were created
psql -U telemetry_user -d telemetry -c "\dt"

# Test upload
cd ../desktop-app
python tools/upload_session.py
```

## Troubleshooting

**Connection refused:**
- Check PostgreSQL is running: `brew services list` (macOS) or `sudo systemctl status postgresql` (Linux)

**Authentication failed:**
- Verify password in `.env` matches the one you set
- Check user exists: `psql -U postgres -c "\du"`

**Permission denied:**
```sql
psql -U postgres -d telemetry
GRANT ALL ON SCHEMA public TO telemetry_user;
GRANT CREATE ON SCHEMA public TO telemetry_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO telemetry_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO telemetry_user;
```

## Migrate Existing SQLite Data (Optional)

If you have data in SQLite you want to keep:

```bash
# Export from SQLite
sqlite3 telemetry.db .dump > dump.sql

# Edit dump.sql to remove SQLite-specific syntax, then:
psql -U telemetry_user -d telemetry < dump.sql
```

For a fresh start, just delete `telemetry.db` and let the app create new tables.

