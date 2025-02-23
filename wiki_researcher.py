import logging
import os
import sys
from typing import Dict, List

import requests
from dotenv import load_dotenv
from openai import OpenAI

from fairytaler.text_to_speech import TextToSpeech

logger = logging.getLogger(__name__)

load_dotenv()


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
    """

    def __init__(self):
        if sys.platform == "darwin":
            os.environ["REQUESTS_CA_BUNDLE"] = "/opt/homebrew/etc/openssl@3/cert.pem"
            os.environ["SSL_CERT_FILE"] = "/opt/homebrew/etc/openssl@3/cert.pem"

        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.tts = TextToSpeech()
        self.model_name = os.getenv("MODEL_NAME", "gpt-4-turbo-preview")

    def _search_wikipedia(self, topic: str) -> List[Dict]:
        """Search Wikipedia for articles related to the topic"""
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": topic,
            "srlimit": 5,
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
        LIMIT_IN_CHARS = 30_000
        prompt = f"Create an engaging podcast script about {topic}. Use this research: {research_data[:LIMIT_IN_CHARS]}. Make it around {length} words long."

        completion = self.openai_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        return completion.choices[0].message.content

    def generate_podcast(self, topic: str, output_file: str, length: int) -> str:
        """
        Generate a podcast about the given topic

        Args:
            topic: The research topic
            output_file: Path to save the audio file

        Returns:
            The generated podcast script
        """
        logger.info(f"Researching topic: {topic}")

        # Search Wikipedia
        search_results = self._search_wikipedia(topic)
        print(search_results)

        # Collect research data
        research_data = ""
        for result in search_results[:2]:  # Use top 2 articles
            content = self._get_article_content(result["pageid"])
            research_data += content + "\n\n"

        # Generate podcast script
        script = self._create_podcast_script(research_data, topic, length)

        return script


if __name__ == "__main__":
    researcher = WikiResearcher()
    topic = "The history of coffee"
    output_file = "podcast.mp3"
    length = 1000
    script = researcher.generate_podcast(topic, output_file, length)
    print(script)
