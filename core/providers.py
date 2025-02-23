import openai
import asyncio


class OpenAIAsyncClient:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        openai.api_key = self.api_key

    async def stream_response(self, prompt: str):
        response = await openai.Completion.create(
            model=self.model,
            prompt=prompt,
            max_tokens=150,
            stream=True
        )
        async for chunk in response:
            if 'choices' in chunk:
                for choice in chunk['choices']:
                    if 'text' in choice:
                        yield choice['text']

# Example usage


async def main():
    client = OpenAIAsyncClient(api_key="your_openai_api_key")
    async for text in client.stream_response("Hello, how are you?"):
        print(text, end='')
