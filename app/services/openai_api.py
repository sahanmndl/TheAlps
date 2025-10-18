from app.core.config import settings
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class OpenAIAPI:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_text(self, prompt: str, model: str = "gpt-5") -> str:
        try:
            response = client.responses.create(
                model=model,
                input=prompt
            )
            return response.output_text
        except Exception as e:
            raise RuntimeError(f"Error generating text: {str(e)}")