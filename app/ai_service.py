import os
import ollama


class AIService:
    def __init__(self):
        self.host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
        self.client = ollama.Client(host=self.host)

    def build_context(self, messages, max_messages=20):
        system_prompt = {
            "role": "system",
            "content": (
                "Você é o Oracle.ia, um assistente inteligente, claro e objetivo. "
                "Responda em português do Brasil, com explicações organizadas e úteis."
            ),
        }

        recent_messages = messages[-max_messages:]

        return [system_prompt] + recent_messages

    def get_response_stream(self, messages):
        try:
            context = self.build_context(messages)

            stream = self.client.chat(
                model=self.model,
                messages=context,
                stream=True,
            )

            for chunk in stream:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content

        except Exception as e:
            yield f"Erro na IA: {e}"