#!/usr/bin/env python3
"""Скрипт для запуска бота."""
import sys
import os

# Добавляем текущую директорию в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from app.main import main
    import asyncio
    asyncio.run(main())
