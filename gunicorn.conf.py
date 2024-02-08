import multiprocessing
import os

from dotenv import load_dotenv

load_dotenv()

bind = os.getenv("GUNICORN_DOMEN")
workers = multiprocessing.cpu_count() * 2 + 1
timeout = 30
cache = None
