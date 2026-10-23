import os
import time

from groq import RateLimitError
from dotenv import load_dotenv
from groq import Groq
from deepeval.models import DeepEvalBaseLLM

load_dotenv()


class GroqJudge(DeepEvalBaseLLM):
    def __init__(self):
        self.client = Groq(
            api_key=os.environ["GROQ_API_KEY"],
            timeout=60,
            max_retries=1,
        )

    def load_model(self):
        return self.client

    def get_model_name(self):
        return "Groq GPT-OSS-120B Judge"

    def generate(self, prompt, schema=None):
        messages = [
            {"role": "user", "content": prompt}
        ]

        options = {}

        if schema is not None:
            messages[0]["content"] += (
                "\nReturn only valid JSON matching this schema:\n"
                + str(schema.model_json_schema())
            )
            options["response_format"] = {
                "type": "json_object"
            }

        for attempt in range(6):
            try:
                response = self.client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=messages,
                    temperature=0,
                    **options,
                )
                break
            except RateLimitError as error:
                if attempt == 5:
                    raise

                retry_after = error.response.headers.get(
                    "retry-after"
                )
                delay = (
                    float(retry_after)
                    if retry_after
                    else min(60, 5 * 2**attempt)
                )
                print(f"Rate limited. Waiting {delay + 1:.1f}s...")
                time.sleep(delay + 1)

        text = response.choices[0].message.content

        if schema is not None:
            return schema.model_validate_json(text)

        return text

    async def a_generate(self, prompt, schema=None):
        import asyncio

        return await asyncio.to_thread(
            self.generate, prompt, schema
        )


if __name__ == "__main__":
    judge = GroqJudge()
    print(judge.generate("Reply with exactly: Judge ready"))