import pandas as pd
import requests
from utils import ColoredText, load_text
import os

gpt_prompt = """
Your Role: History Categorization Expert

Objective:
Given the input caption, you should understand it and answer the response format.

Caption: {caption}

Response Format:
Spatial: Eastern/Western/Africa
Temporal: Ancient/Medieval/Modern
"""

class CatAgent:
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

    def __init__(self, api_key, category=None):
        self.api_key = api_key
        self.category = category
        self.results = []
        self.file_caption_directory= os.path.join(os.path.dirname(__file__), '..', 'data', 'captions.xlsx')
    
    def query(self, caption):
        language = gpt_prompt.format(caption=caption)
        self.payload["messages"][0]["content"][0]["text"] = language

        n_early_stopping = 0
        while True:
            if n_early_stopping > 2:
                print(ColoredText.color_text("Early stop", ColoredText.RED))
                import sys
                sys.exit()
            try:
                n_early_stopping += 1
                response = requests.post("https://api.openai.com/v1/chat/completions", 
                                        headers=self.headers, 
                                        json=self.payload)
                content = response.json()['choices'][0]['message']['content']
                spatial = content.split("Spatial:")[1].split('\n')[0].strip()
                termporal = content.split("Temporal:")[1].strip()

                break
            
            except Exception as e:
                print(ColoredText.color_text("ERROR: " + str(e), ColoredText.RED))

        return spatial, termporal
        
    def run(self):
        print(ColoredText.color_text("Loading images and captions..", ColoredText.YELLOW))
        captions = load_text(self.file_caption_directory)

        print(ColoredText.color_text("Processing results..", ColoredText.YELLOW))
        
        df = captions[self.category].iloc[:, 0:2]
        for count, (data_index, caption) in enumerate(zip(df.iloc[2:, 0], df.iloc[2:, 1])):
            spatial, termporal = self.query(caption)
            print(count, spatial, termporal)

            self.results.append({
                "data_index": data_index,
                "spatial": spatial,
                "termporal": termporal,
            })
        df = pd.DataFrame(self.results)
        df.to_excel(f"GPT4o_output_{self.category}_cat.xlsx", index=False)