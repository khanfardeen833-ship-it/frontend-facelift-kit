@echo off
echo Starting Manager Feedback Server...
echo.
echo Installing dependencies...
call npm install
echo.
echo Starting server on port 3002...
echo.
echo Feedback form will be available at: http://localhost:3002
echo.
call npm start
pause
