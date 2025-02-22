from fastapi import FastAPI, Response, HTTPException
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
import os
from fastapi.middleware.cors import CORSMiddleware
from fairytaler.text_to_speech import TextToSpeech
from fairytaler.generation import GeneratorLM

app = FastAPI()
tts = TextToSpeech()
llm = GeneratorLM()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage for generated stories (in real app this would be a database)
STORIES_DIR = "generated_stories"
os.makedirs(STORIES_DIR, exist_ok=True)


class StorySettings(BaseModel):
    context: str | None = None


class Story(BaseModel):
    id: int
    name: str
    text: str
    audio_path: str
    created_at: datetime


stories: List[Story] = [
    Story(
        id=1,
        name="The Adventure in the Forest",
        text="Once upon a time in a forest, there lived a wise old owl...",
        audio_path="generated_stories/story_1.mp3",
        created_at=datetime.now(),
    )
]

class StoryCreate(BaseModel):
    name: str = Field(description="The title of the story")
    text: str = Field(description="Text of the story")


@app.get("/stories", response_model=List[Story])
def get_stories() -> List[Story]:
    return stories


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


@app.post("/generate-story")
def generate_story(settings: StorySettings) -> Story:

    
    story = llm.generate_story(context=settings.context, base_model=StoryCreate)

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
