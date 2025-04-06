import os
import base64
import mimetypes
import io
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://jake:Gunshot391@cluster.bynp3th.mongodb.net/")
client = AsyncIOMotorClient(MONGO_URI)
db = client["multimedia_db"]

class PlayerScore(BaseModel):
    player_name: str
    score: int

def get_mime_type(filename):
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"

async def process_file(file: UploadFile):
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB size limit
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
    result = await db.sprites.insert_one(data)
    return {"message": "Sprite uploaded", "id": str(result.inserted_id)}

@app.get("/sprite/{asset_id}")
async def get_sprite(asset_id: str):
    asset = await db.sprites.find_one({"_id": ObjectId(asset_id)})
    if not asset:
        raise HTTPException(status_code=404, detail="Sprite not found")
    file_bytes = base64.b64decode(asset["content"])
    return StreamingResponse(io.BytesIO(file_bytes), media_type=asset["file_type"], headers={
        "Content-Disposition": f"inline; filename={asset['filename']}"
    })

@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...)):
    data = await process_file(file)
    result = await db.audio.insert_one(data)
    return {"message": "Audio uploaded", "id": str(result.inserted_id)}

@app.get("/audio/{asset_id}")
async def get_audio(asset_id: str):
    asset = await db.audio.find_one({"_id": ObjectId(asset_id)})
    if not asset:
        raise HTTPException(status_code=404, detail="Audio not found")
    file_bytes = base64.b64decode(asset["content"])
    return StreamingResponse(io.BytesIO(file_bytes), media_type=asset["file_type"], headers={
        "Content-Disposition": f"inline; filename={asset['filename']}"
    })

@app.post("/player_score")
async def upload_score(score: PlayerScore):
    if score.score < 0:
        raise HTTPException(status_code=400, detail="Score must be non-negative")
    doc = {
        "player_name": score.player_name,
        "score": score.score,
        "date_achieved": datetime.utcnow()
    }
    result = await db.scores.insert_one(doc)
    return {"message": "Score uploaded", "id": str(result.inserted_id)}

@app.get("/player_score/{score_id}")
async def get_score(score_id: str):
    score = await db.scores.find_one({"_id": ObjectId(score_id)})
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    score["id"] = str(score["_id"])
    del score["_id"]
    return score
