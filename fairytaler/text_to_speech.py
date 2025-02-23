import os
import sys

from elevenlabs import ElevenLabs, save


class TextToSpeech:
    VOICE_CONFIG = {
        "rachel": "21m00Tcm4TlvDq8ikWAM",
        "brian": "nPczCjzI2devNBz1zQrb",
        "charlotte": "pMsXgVXv3BLzUgSXRplE",
        "joseph": "TX3LPaxmHKxFdv7VOQHJ",
    }

    def __init__(self) -> None:
        if sys.platform == "darwin":
            os.environ["REQUESTS_CA_BUNDLE"] = "/opt/homebrew/etc/openssl@3/cert.pem"
            os.environ["SSL_CERT_FILE"] = "/opt/homebrew/etc/openssl@3/cert.pem"

        self.api_key = os.environ["ELEVEN_LABS_API_KEY"]
        self.client = ElevenLabs(api_key=self.api_key)

    def generate_audio(
        self, text: str, voice: str, output_file: str | None = None
    ) -> bytes:
        audio_iterator = self.client.text_to_speech.convert(
            voice_id=self.VOICE_CONFIG[voice],
            output_format="mp3_44100_128",
            text=text,
            model_id="eleven_multilingual_v2",
            request_options={"timeout_in_seconds": 1200},
        )

        audio = b""
        for chunk in audio_iterator:
            audio += chunk

        if output_file:
            save(audio, output_file)
        return audio
