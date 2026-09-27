from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

response = client.chat.completions.create(
    model="qwen",
    messages=[
        {
            "role": "user",
            "content": "Explain what a CDR is in simple words."
        }
    ],
    temperature=0.2
)

print(response.choices[0].message.content)