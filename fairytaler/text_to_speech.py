import os
from elevenlabs import ElevenLabs, save


class TextToSpeech:
    def __init__(self) -> None:
        os.environ["REQUESTS_CA_BUNDLE"] = "/opt/homebrew/etc/openssl@3/cert.pem"
        os.environ["SSL_CERT_FILE"] = "/opt/homebrew/etc/openssl@3/cert.pem"

        self.api_key = os.environ["ELEVEN_LABS_API_KEY"]
        self.client = ElevenLabs(api_key=self.api_key)

    def generate_audio(self, text: str, output_file: str | None = None) -> bytes:
        """
        Generate audio from text and optionally save to file

        Args:
            text (str): Text to convert to speech
            output_file (str, optional): Path to save the audio file. Defaults to None.

        Returns:
            bytes: Audio data
        """
        audio_iterator = self.client.text_to_speech.convert(
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            output_format="mp3_44100_128",
            text=text,
            model_id="eleven_multilingual_v2",
        )

        audio = b""
        for chunk in audio_iterator:
            audio += chunk

        if output_file:
            save(audio, output_file)
        return audio
