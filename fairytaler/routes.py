from fastapi import FastAPI, Response, HTTPException
from datetime import datetime
from typing import List
from pydantic import BaseModel
import os

from fairytaler.text_to_speech import TextToSpeech

app = FastAPI()
tts = TextToSpeech()

# Storage for generated stories (in real app this would be a database)
STORIES_DIR = "generated_stories"
os.makedirs(STORIES_DIR, exist_ok=True)


class Story(BaseModel):
    id: int
    name: str
    text: str
    audio_path: str
    created_at: datetime


stories: List[Story] = []


class StoryCreate(BaseModel):
    name: str
    text: str


@app.get("/stories", response_model=List[Story])
def get_stories() -> List[Story]:
    return stories


@app.post("/stories", response_model=Story)
def create_story(story: StoryCreate) -> Story:
    # Generate unique ID and filename
    story_id = len(stories) + 1
    audio_filename = f"story_{story_id}.mp3"
    audio_path = os.path.join(STORIES_DIR, audio_filename)

    # Generate audio
    tts.generate_audio(story.text, audio_path)

    # Create story object
    new_story = Story(
        id=story_id,
        name=story.name,
        text=story.text,
        audio_path=audio_path,
        created_at=datetime.now(),
    )
    stories.append(new_story)
    return new_story


@app.get("/stories/{story_id}/audio")
def get_story_audio(story_id: int) -> Response:
    # Find story
    story = next((s for s in stories if s.id == story_id), None)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    # Read audio file
    with open(story.audio_path, "rb") as f:
        audio_data = f.read()

    return Response(content=audio_data, media_type="audio/mpeg")


# Mock story generator endpoint
@app.post("/generate-story")
def generate_story() -> Story:
    # This is a mock implementation
    mock_story = StoryCreate(
        name="The Adventure Begins",
        text="Once upon a time in a magical forest, there lived a wise old owl...",
    )
    return create_story(mock_story)
