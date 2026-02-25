#!/usr/bin/env python3
"""
로컬 개발 서버 실행 스크립트
"""
import uvicorn
import os
import sys

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Starting User Service locally...")
    print("📍 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health/")
    print("📊 API Endpoints: http://localhost:8000/api/v1/")
    print("=" * 50)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
