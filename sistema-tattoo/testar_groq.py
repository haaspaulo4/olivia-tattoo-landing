import requests

api_key = "SUA_API_KEY_GROQ_AQUI"
url_chat = "https://api.groq.com/openai/v1/chat/completions"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

modelos = ["llama-3.3-70b-versatile"]

for modelo in modelos:
    data = {
        "model": modelo,
        "messages": [{"role": "user", "content": "say hi in 2 words"}],
        "max_tokens": 20,
    }
    r = requests.post(url_chat, headers=headers, json=data, timeout=30)
    if r.status_code == 200:
        print(f"OK [{modelo}]: {r.json()['choices'][0]['message']['content']}")
    else:
        print(f"ERRO [{modelo}]: Status {r.status_code} - {r.text[:200]}")