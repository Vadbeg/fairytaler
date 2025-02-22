import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()


SYSTEM_PROMPT = """
    You're a super creative writer of stories. Writer a story based on the description
"""

FAIRYTALE_PROMPT = """
    Write a magical bedtime story for children about {context} with the following elements:
    - Main character
    - Theme
    - Story structure:
        * One day, he discovers a lost baby bird
        * He must overcome his fears to help the bird find its way home
        * Along the way, he meets helpful forest creatures
    - Include friendly dialogue between animals
    - Add simple descriptions of the forest and its sounds
    - End with a heartwarming lesson about friendship
    - Keep the language simple and engaging for young children
    - Story should be around 100 words
"""


class GeneratorLM:

    def __init__(self):
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.model_name = os.getenv("MODEL_NAME")
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def generate_story(self, context: str, base_model: BaseModel) -> BaseModel:
        """
        Generates a story
        Args:
            context (str): Kontekst lub temat dla generowanej historii
            base_model (BaseModel): Model Pydantic definiujący strukturę wyjściową historii

        Returns:
            BaseModel: Wygenerowana historia zgodna z podanym modelem bazowym
        """
        completion = self.client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": FAIRYTALE_PROMPT.format(context=context)},
            ],
            response_format=base_model,
        )

        event = completion.choices[0].message.parsed

        return event
