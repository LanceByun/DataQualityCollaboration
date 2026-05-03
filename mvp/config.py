import os

from dotenv import load_dotenv

load_dotenv()

BUS_API_KEY = os.getenv("BUS_API_KEY")
if not BUS_API_KEY:
    raise RuntimeError("BUS_API_KEY is missing. Please set it in mvp/.env")
