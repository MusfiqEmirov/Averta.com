@echo off
REM Helper script for running local docker-compose
REM Usage: docker-compose-local.bat up
REM        docker-compose-local.bat down
REM        docker-compose-local.bat build
REM        etc.

if "%1"=="" (
    echo Usage: docker-compose-local.bat [command]
    echo Example: docker-compose-local.bat up
    exit /b 1
)

docker-compose -f docker-compose-local.yaml %*

