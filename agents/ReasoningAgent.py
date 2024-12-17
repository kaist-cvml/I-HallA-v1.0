import requests

gpt_prompt = """
You are an agent who helps combine the given textual reasonings.
Your goal is to combine them all, ensuring they do not overlap with each other.

[Reasoning]
{reasoning}
"""

class ReasoningAgent:
    api_key = "[YOUR_API_KEY]"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
        {
            "role": "user",
            "content": [
            {
                "type": "text",
                "text": ""
            },
            ]
        }
        ],
    }

    def __init__(self, api_key):
        self.api_key = api_key

    def query(self, reasonings):
        reasoning_string = "\n".join([f"[{i+1}] {reasoning}" for i, reasoning in enumerate(reasonings)])

        language = gpt_prompt.format(reasoning=reasoning_string)
        self.payload["messages"][0]["content"][0]["text"] = language
        
        while True:
            response = requests.post("https://api.openai.com/v1/chat/completions", 
                                    headers=self.headers, 
                                    json=self.payload)
            if response.status_code == 200:
                break
        
        content = response.json()['choices'][0]['message']['content']

        return reasoning_string, content