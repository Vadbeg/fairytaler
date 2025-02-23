import logging
import os
import sys

import requests
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

load_dotenv()


class StorySettings(BaseModel):
    context: str | None = None
    voice: str | None = None
    length: int | None = None


class WikiResearcher:
    SYSTEM_PROMPT = """
    You are a podcast which specializes in making complex topics engaging and accessible. 
    Say that you are personal podcast of the user.
    Take the provided research and create an engaging podcast text that:
    - Has a clear narrative structure
    - Uses conversational language
    - Includes interesting facts and anecdotes
    - Maintains an engaging flow
    - Is educational but entertaining

    Do not include words which wouldn't be spoken in a podcast. Do not include tags, or anything. Just the words which would be spoken in a podcast.
    Script should be around {length} words long.
    """

    def __init__(self):
        if sys.platform == "darwin":
            os.environ["REQUESTS_CA_BUNDLE"] = "/opt/homebrew/etc/openssl@3/cert.pem"
            os.environ["SSL_CERT_FILE"] = "/opt/homebrew/etc/openssl@3/cert.pem"

        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")

        print(self.model_name)
        print(os.getenv("OPENAI_API_KEY"))

    def _search_wikipedia(self, topic: str) -> list[dict]:
        """Search Wikipedia for articles related to the topic"""
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": topic,
            "srlimit": 10,
        }

        response = requests.get(search_url, params=params)
        return response.json()["query"]["search"]

    def _get_article_content(self, page_id: int) -> str:
        """Get the content of a Wikipedia article"""
        content_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "pageids": page_id,
            "prop": "extracts",
            "explaintext": True,
        }

        response = requests.get(content_url, params=params)
        pages = response.json()["query"]["pages"]
        return pages[str(page_id)]["extract"]

    def _create_podcast_script(
        self, research_data: str, topic: str, length: int
    ) -> str:
        """Generate a podcast script from the research data"""
        LIMIT_IN_CHARS = 30_000 * 4
        number_of_words = length * 7 * 60
        prompt = f"Create an engaging podcast script about {topic}. Use this research: {research_data[:LIMIT_IN_CHARS]}. Make it more then {number_of_words} words long."

        completion = self.openai_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        return completion.choices[0].message.content

    def _create_episode_title(self, topic: str) -> str:
        """Generate an engaging title for the podcast episode"""
        prompt = f"Create a catchy and engaging podcast episode title about {topic}. The title should be concise but intriguing, making listeners want to learn more. Do not use quotes in the response."

        completion = self.openai_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a podcast title generator. Create engaging, catchy titles that grab attention.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        return completion.choices[0].message.content.strip()

    def generate_podcast(self, settings: StorySettings) -> tuple[str, str]:
        """
        Generate a podcast about the given topic

        Args:
            topic: The research topic
            output_file: Path to save the audio file

        Returns:
            The generated podcast script
        """
        logger.info(f"Researching topic: {settings.context}")

        # Search Wikipedia
        search_results = self._search_wikipedia(settings.context)

        # Collect research data
        research_data = ""
        for result in search_results[:2]:  # Use top 2 articles
            content = self._get_article_content(result["pageid"])
            research_data += content + "\n\n"

        # Generate podcast script
        script = self._create_podcast_script(
            research_data, settings.context, settings.length
        )
        title = self._create_episode_title(settings.context)

        return script, title
