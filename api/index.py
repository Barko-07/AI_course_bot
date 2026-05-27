from fastapi import FastAPI, Request
from aiogram import types
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import bot, dp

app = FastAPI()

@app.post("/api/webhook")
async def webhook(request: Request):
    try:
        update_data = await request.json()
        update = types.Update(**update_data)
        await dp.feed_update(bot, update)
    except Exception as e:
        print(f"Error handling update: {e}")
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Telegram Bot is running smoothly on Vercel Serverless Function!"}
