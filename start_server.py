#!/usr/bin/env python3
"""
Startup script for Trip Planner Backend API
"""
import os
import uvicorn
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"Starting Trip Planner Backend API...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Reload: {reload}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"ReDoc Documentation: http://{host}:{port}/redoc")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()