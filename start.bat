@echo off
REM NeuroInsight - Automated Startup Script for Windows
REM This script handles all environment setup automatically

echo 🧠 Starting NeuroInsight...

REM Get the directory where this script is located
SET SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Create .env if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file...
    (
        echo # Database Configuration
        echo POSTGRES_USER=neuroinsight
        echo POSTGRES_PASSWORD=neuroinsight_secure_password
        echo POSTGRES_DB=neuroinsight
        echo POSTGRES_HOST=db
        echo POSTGRES_PORT=5432
        echo.
        echo # Redis Configuration
        echo REDIS_HOST=redis
        echo REDIS_PORT=6379
        echo.
        echo # MinIO Configuration
        echo MINIO_ROOT_USER=minioadmin
        echo MINIO_ROOT_PASSWORD=minioadmin
        echo MINIO_ENDPOINT=minio:9000
        echo MINIO_BUCKET=neuroinsight
        echo.
        echo # Application Configuration
        echo SECRET_KEY=your-secret-key-change-in-production
        echo DEBUG=true
        echo UPLOAD_DIR=/data/uploads
        echo OUTPUT_DIR=/data/outputs
        echo.
        echo # Celery Configuration
        echo CELERY_BROKER_URL=redis://redis:6379/0
        echo CELERY_RESULT_BACKEND=redis://redis:6379/0
    ) > .env
    echo ✅ Created .env file
)

REM Auto-detect absolute paths for Docker-in-Docker
REM Convert Windows path to WSL/Docker path format
SET HOST_UPLOAD_DIR=%SCRIPT_DIR%data\uploads
SET HOST_OUTPUT_DIR=%SCRIPT_DIR%data\outputs

echo 📂 Host paths configured:
echo    Uploads: %HOST_UPLOAD_DIR%
echo    Outputs: %HOST_OUTPUT_DIR%

REM Create data directories if they don't exist
if not exist data\uploads mkdir data\uploads
if not exist data\outputs mkdir data\outputs
if not exist data\logs mkdir data\logs
echo ✅ Data directories ready

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker is not running
    echo    Please start Docker Desktop and try again
    exit /b 1
)

echo ✅ Docker is running

REM Parse command line arguments
SET COMMAND=%1
if "%COMMAND%"=="" SET COMMAND=up

if /i "%COMMAND%"=="up" goto START
if /i "%COMMAND%"=="start" goto START
if /i "%COMMAND%"=="down" goto STOP
if /i "%COMMAND%"=="stop" goto STOP
if /i "%COMMAND%"=="restart" goto RESTART
if /i "%COMMAND%"=="logs" goto LOGS
if /i "%COMMAND%"=="rebuild" goto REBUILD
if /i "%COMMAND%"=="status" goto STATUS
goto USAGE

:START
echo 🚀 Starting all services...
docker-compose up -d
echo.
echo ✅ NeuroInsight is starting!
echo    Frontend:  http://localhost:3000
echo    Backend:   http://localhost:8000
echo.
echo 📊 To view logs:
echo    All services:    docker-compose logs -f
echo    Worker only:     docker-compose logs -f worker
echo.
echo 🛑 To stop:
echo    start.bat stop
goto END

:STOP
echo 🛑 Stopping all services...
docker-compose down
echo ✅ All services stopped
goto END

:RESTART
echo 🔄 Restarting all services...
docker-compose down
docker-compose up -d
echo ✅ Services restarted
goto END

:LOGS
if "%2"=="" (
    docker-compose logs -f
) else (
    docker-compose logs -f %2
)
goto END

:REBUILD
echo 🔨 Rebuilding all containers...
docker-compose down
docker-compose build --no-cache
docker-compose up -d
echo ✅ Rebuild complete
goto END

:STATUS
docker-compose ps
goto END

:USAGE
echo Usage: start.bat [command]
echo.
echo Commands:
echo   up, start   - Start all services (default)
echo   down, stop  - Stop all services
echo   restart     - Restart all services
echo   logs [svc]  - View logs (optionally for specific service)
echo   rebuild     - Rebuild and restart all containers
echo   status      - Show status of all services
exit /b 1

:END

