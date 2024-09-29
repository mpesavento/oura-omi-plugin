from fasthtml.common import JSON
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# import the server app
from main import app

class TranscriptSegment(BaseModel):
    text: str
    speaker: str
    speakerId: int
    is_user: bool
    start: float
    end: float

class ActionItem(BaseModel):
    description: str
    completed: bool

class StructuredData(BaseModel):
    title: str
    overview: str
    emoji: str
    category: str
    action_items: List[ActionItem]
    events: List[str] = []

class PluginResponse(BaseModel):
    plugin_id: str
    content: str

class Memory(BaseModel):
    id: int
    created_at: datetime
    started_at: datetime
    finished_at: datetime
    transcript: str
    transcript_segments: List[TranscriptSegment]
    photos: List[str] = []
    structured: StructuredData
    plugins_response: List[PluginResponse]
    discarded: bool


@app.route('/omi_webhook', methods=['POST'])
def omi_webhook():
    uid = request.query_params.get("uid")
    if not uid:
        return JSON({"error": "Missing uid parameter"}, status_code=400)

    try:
        memory = Memory(**request.json)
    except ValueError as e:
        return JSON({"error": str(e)}, status_code=400)

    # Process the memory object
    processed_data = process_memory(memory, uid)

    return JSON({"message": "Memory processed successfully", "processed_data": processed_data})

def process_memory(memory: Memory, uid: str):
    # This is where you would implement your logic to process the memory
    # For this example, we'll just return some basic information
    return {
        "uid": uid,
        "memory_id": memory.id,
        "title": memory.structured.title,
        "category": memory.structured.category,
        "action_items_count": len(memory.structured.action_items),
        "transcript_length": len(memory.transcript)
    }
