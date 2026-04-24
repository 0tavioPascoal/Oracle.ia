import os
import ollama

class AIService:
    def __init__(self):
        self.host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
        self.client = ollama.Client(host=self.host)
        # Você pode trocar para "qwen2.5:3b", "gemma:2b" ou "llama3" conforme seu download
        self.model = "qwen2.5:3b"

    def get_response_stream(self, messages):
        try:
            stream = self.client.chat(
                model=self.model,
                messages=messages,
                stream=True
            )
            for chunk in stream:
                yield chunk['message']['content']
        except Exception as e:
            yield f"Erro na IA: {e}"