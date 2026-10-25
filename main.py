from ollama import chat, ChatResponse

message = 'Translate this html from polish to english, while preserving the formating, and style and the vibe of my writing. ' + '<h1>"Co tu się dzieje?"</h1><br><p>"Zimno mi!"</p>'

response: ChatResponse = chat(
    model='gemma3:4b',
    messages=[
        {
            'role': 'user',
            'content': message,
        },
    ],
    stream=True,
)

for chunk in response:
    print(chunk['message']['content'], end='', flush=True)

print()
