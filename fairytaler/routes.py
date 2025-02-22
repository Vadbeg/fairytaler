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
    allow_origins=["*"],  # Add your frontend URL
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


HUGE_TEXT = """
Edward George Gerard (February 22, 1890 – August 7, 1937) was a Canadian professional ice hockey player, coach, and manager. Born in Ottawa, Ontario, he played for 10 seasons for his hometown Ottawa Senators. He spent the first three years of his playing career as a left winger before switching to defence, retiring in 1923 due to a throat ailment. Gerard won the Stanley Cup in four consecutive years from 1920 to 1923 (with the Senators three times and as an injury replacement player with the Toronto St. Patricks in 1922), the first player to do so.
After his playing career, he served as a coach and manager, working with the Montreal Maroons from 1925 until 1929 and winning the Stanley Cup in 1926. Gerard also coached the New York Americans for two seasons between 1930 and 1932 before returning to the Maroons for two more seasons. He ended his career coaching the St. Louis Eagles in 1934 before retiring due to the same throat issue that had ended his playing career. He died from complications related to it in 1937.
Renowned as a talented athlete in multiple sports, Gerard first gained prominence in rugby football as a halfback for the Ottawa Rough Riders club from 1909 to 1913; however, he left the sport when he moved to hockey. Outside hockey, he worked initially for the Canadian government as a printer before working in the Geodetic Survey, ultimately becoming chief engineering clerk. Well-renowned during his hockey-playing career, he was regarded as one of the best defenders of his era and gained notice for being a tough player (though not considered violent or dirty). Gerard was one of the original nine players inducted into the Hockey Hall of Fame when it was founded in 1945. He is also an inductee of Canada's Sports Hall of Fame.
"""


stories: List[Story] = [
    Story(
        id=1,
        name="Some random story",
        text="Once upon a time in a forest, there lived a wise old owl... " + HUGE_TEXT,
        audio_path="generated_stories/story_2.mp3",
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


@app.get("/stories/{story_id}", response_model=Story)
def get_story(story_id: int) -> Story:
    story = next((s for s in stories if s.id == story_id), None)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story


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
