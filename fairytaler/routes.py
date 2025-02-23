import logging
import os
from datetime import datetime, timedelta
from typing import List

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from mutagen.mp3 import MP3
from pydantic import BaseModel, Field

from fairytaler.generation import StorySettings, WikiResearcher
from fairytaler.stories import (
    FIRST_STORY,
    SECOND_STORY,
    THIRD_STORY,
    FOURTH_STORY,
    FIFTH_STORY,
)
from fairytaler.text_to_speech import TextToSpeech

app = FastAPI()
tts = TextToSpeech()
llm = WikiResearcher()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage for generated stories (in real app this would be a database)
STORIES_DIR = "generated_stories"
os.makedirs(STORIES_DIR, exist_ok=True)


class Story(BaseModel):
    id: int
    name: str
    text: str
    audio_path: str
    created_at: datetime
    duration_seconds: float = 0.0


stories: List[Story] = [
    Story(
        id=1,
        name="Van Gogh Unveiled: The Secrets Behind the Swirls",
        text=FIRST_STORY,
        audio_path="generated_stories/story_1.mp3",
        created_at=datetime.now() - timedelta(days=1),
        duration_seconds=MP3("generated_stories/story_1.mp3").info.length * 15,
    ),
    Story(
        id=2,
        name="Rugby Unraveled: The Secrets Behind the Scrum",
        text=SECOND_STORY,
        audio_path="generated_stories/story_2.mp3",
        created_at=datetime.now() - timedelta(hours=11),
        duration_seconds=MP3("generated_stories/story_2.mp3").info.length * 4,
    ),
    Story(
        id=3,
        name="Beyond Resistance: The Future of Superconductors Unveiled",
        text=THIRD_STORY,
        audio_path="generated_stories/story_3.mp3",
        created_at=datetime.now() - timedelta(hours=8),
        duration_seconds=MP3("generated_stories/story_3.mp3").info.length * 4,
    ),
    Story(
        id=4,
        name="Opium Wars: The Forgotten Conflict That Changed History",
        text=FIFTH_STORY,
        audio_path="generated_stories/story_5.mp3",
        created_at=datetime.now() - timedelta(hours=5),
        duration_seconds=MP3("generated_stories/story_5.mp3").info.length * 4,
    ),
]

last_story = Story(
    id=5,
    name="Power Plays: Unraveling the Secrets of American Politics",
    text=FOURTH_STORY,
    audio_path="generated_stories/story_4.mp3",
    created_at=datetime.now() - timedelta(hours=2),
    duration_seconds=MP3("generated_stories/story_4.mp3").info.length,
)


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


@app.get("/stories/{story_id}", response_model=Story)
def get_story(story_id: int) -> Story:
    story = next((s for s in stories if s.id == story_id), None)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story


@app.post("/generate-story")
def generate_story(settings: StorySettings) -> Story:
    logging.error(f"Generating story with settings: {settings}")

    import time
    time.sleep(5)

    # story, title = llm.generate_podcast(settings=settings)
    # print(len(story.split()))

    # # Generate unique ID and filename
    # story_id = len(stories) + 1
    # audio_filename = f"story_{story_id}.mp3"
    # audio_path = os.path.join(STORIES_DIR, audio_filename)

    # # Generate audio
    # tts.generate_audio(story, settings.voice, audio_path)

    # # Get audio duration
    # audio = MP3(audio_path)
    # duration = audio.info.length

    # # Create story object
    # new_story = Story(
    #     id=story_id,
    #     name=title,
    #     text=story,
    #     audio_path=audio_path,
    #     created_at=datetime.now(),
    #     duration_seconds=duration,
    # )
    stories.append(last_story)
    return last_story
