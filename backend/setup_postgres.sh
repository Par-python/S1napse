#!/bin/bash
# PostgreSQL Setup Script for Telemetry App

set -e

echo "🚀 Setting up PostgreSQL for Telemetry App"
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed or not in PATH"
    echo ""
    echo "Install PostgreSQL:"
    echo "  macOS: brew install postgresql@15 && brew services start postgresql@15"
    echo "  Linux: sudo apt install postgresql postgresql-contrib"
    exit 1
fi

echo "✓ PostgreSQL found"
echo ""

# Get database credentials
read -p "Enter PostgreSQL username (default: postgres): " DB_USER
DB_USER=${DB_USER:-postgres}

read -sp "Enter PostgreSQL password for $DB_USER: " DB_PASSWORD
echo ""

read -p "Enter database name (default: telemetry): " DB_NAME
DB_NAME=${DB_NAME:-telemetry}

read -p "Enter host (default: localhost): " DB_HOST
DB_HOST=${DB_HOST:-localhost}

read -p "Enter port (default: 5432): " DB_PORT
DB_PORT=${DB_PORT:-5432}

echo ""
echo "Creating database and user..."

# Create database and user
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres <<EOF
-- Create database if it doesn't exist
SELECT 'CREATE DATABASE $DB_NAME'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

-- Create user if it doesn't exist
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '${DB_NAME}_user') THEN
        CREATE USER ${DB_NAME}_user WITH PASSWORD '$DB_PASSWORD';
    END IF;
END
\$\$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO ${DB_NAME}_user;
\c $DB_NAME
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${DB_NAME}_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${DB_NAME}_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${DB_NAME}_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${DB_NAME}_user;
EOF

if [ $? -eq 0 ]; then
    echo "✓ Database and user created successfully"
else
    echo "❌ Failed to create database. You may need to run manually:"
    echo "   psql -U $DB_USER -d postgres"
    echo "   CREATE DATABASE $DB_NAME;"
    echo "   CREATE USER ${DB_NAME}_user WITH PASSWORD '$DB_PASSWORD';"
    echo "   GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO ${DB_NAME}_user;"
    exit 1
fi

echo ""
echo "Creating .env file..."

# Create .env file
cat > .env <<EOF
# Database Configuration
DATABASE_URL=postgresql://${DB_NAME}_user:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}

# AWS S3 Configuration (optional)
S3_BUCKET=your-bucket
S3_REGION=your-region
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Application Secret Key
SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
EOF

echo "✓ .env file created"
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Review the .env file: cat .env"
echo "2. Start the backend: uvicorn app.main:app --reload"
echo "3. Test the connection by uploading a session"
echo ""

