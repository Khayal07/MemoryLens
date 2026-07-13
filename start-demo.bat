@echo off
REM One-click MemoryLens launcher for the demo.
REM Double-click this file. It starts EVERYTHING (Postgres, Redis, API, frontend)
REM in one go, then opens the app in your browser. No separate `npm run dev`.

echo Starting MemoryLens (all services)...
cd /d "%~dp0"
docker compose up -d

echo.
echo Waiting for the app to be ready (first start builds/loads models, ~1-2 min)...

:wait
timeout /t 3 /nobreak >nul
curl -s -o nul http://localhost:5173 && goto ready
goto wait

:ready
echo.
echo MemoryLens is up. Opening http://localhost:5173
start "" http://localhost:5173
echo.
echo TIP: do one warm-up search before the demo — the very first search loads the
echo      AI models (~30-40s once); after that searches take ~2-3s.
echo.
echo To stop later, run: docker compose down
pause
