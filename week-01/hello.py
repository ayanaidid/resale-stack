"""
what this does: when run, this outputs a short poem about the beauty of nature using the Claude model from Anthropic.

In: nothing, i hardcoded the prompt for the sake of this test
Out: the poem as instructed by the prompt, as well as the number of input and output tokens used to generate the poem.
Fails: i didn't have "ANTHROPIC_API_KEY" set in my environment variables, so the code failed to run. I added it to my .env file and re-ran the code, and it worked.

"""

import os
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
message = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "Hello, can you write a short poem about the beauty of nature?"
        }
    ]
)
print(f"Input tokens: {message.usage.input_tokens}")
print(f"Output tokens: {message.usage.output_tokens}")

for block in message.content:
    if block.type == "text":
        print(block.text)
