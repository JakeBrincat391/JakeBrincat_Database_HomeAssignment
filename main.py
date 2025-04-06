import os
import base64
import mimetypes
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://jake:Gunshot391@cluster.bynp3th.mongodb.net/")
client = AsyncIOMotorClient(MONGO_URI)
db = client["Assets"]

class PlayerScore(BaseModel):
    player_name: str
    score: int

def get_mime_type(filename):
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"

async def process_file(file: UploadFile):
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")
    encoded = base64.b64encode(content).decode("utf-8")
    return {
        "filename": file.filename,
        "file_type": get_mime_type(file.filename),
        "size": len(content),
        "upload_date": datetime.utcnow(),
        "content": encoded
    }

@app.post("/upload_sprite")
async def upload_sprite(file: UploadFile = File(...)):
    data = await process_file(file)
    result = await db["Sprites"].insert_one(data)
    return {"message": "Sprite uploaded", "id": str(result.inserted_id)}

@app.get("/sprite/{id}")
async def get_sprite(id: str):
    sprite = await db.sprites.find_one({"_id": ObjectId(id)})
    if not sprite:
        raise HTTPException(status_code=404, detail="Sprite not found")
    return Response(
        content=base64.b64decode(sprite["content"]),
        media_type=sprite["file_type"],
        headers={"Content-Disposition": f"inline; filename={sprite['filename']}"}
    )

@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...)):
    data = await process_file(file)
    result = await db["Audio"].insert_one(data)
    return {"message": "Audio uploaded", "id": str(result.inserted_id)}

@app.get("/audio/{id}")
async def get_audio(id: str):
    audio = await db.audio.find_one({"_id": ObjectId(id)})
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    return Response(
        content=base64.b64decode(audio["content"]),
        media_type=audio["file_type"],
        headers={"Content-Disposition": f"inline; filename={audio['filename']}"}
    )

@app.post("/player_score")
async def upload_score(score: PlayerScore):
    if score.score < 0:
        raise HTTPException(status_code=400, detail="Score must be non-negative")
    doc = {
        "player_name": score.player_name,
        "score": score.score,
        "date_achieved": datetime.utcnow()
    }
    result = await db["Score"].insert_one(doc)
    return {"message": "Score uploaded", "id": str(result.inserted_id)}

@app.get("/player_score/{id}")
async def get_score(id: str):
    score = await db.scores.find_one({"_id": ObjectId(id)})
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    return {
        "player_name": score["player_name"],
        "score": score["score"],
        "date_achieved": score["date_achieved"]
    }
