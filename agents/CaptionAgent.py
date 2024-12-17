import pandas as pd
import requests
from utils import ColoredText, load_text
import os

gpt_prompt = """
Your Role: Excellent Caption Analyst

Objective:
Given the input caption, assume there is a realistic image that matches the caption.
Your goal is to generate a reasoning about things within the image where the caption is illustrated.
Based on the factual information of the corresponding image, generate reasoning explaining why the image is appropriate for the given caption.

You should follow the response format below:

[Response Format]
- Reasoning: <Your reasoning about why you have made this decision>
  - **Visual Evidence**: <Your reasoning about why you made this decision solely based on the visual appearance>
  - **Contextual Evidence**: <Your reasoning about why you made this decision solely based on the context>

When evaluating a caption, use very detailed aspects of the scene and compare them with reality as the basis for your judgment.
For example, consider the number of objects, the shapes of structures, the number of floors in buildings, and other similar information.
Compare these details with real-life facts to distinguish and identify the scene accurately.

Ensure adherence to the response format provided above.

Caption: {caption}
"""

class CaptionAgent:
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
                reasoning = content.split("Reasoning:")[1].strip()

                print(ColoredText.color_text("Reasoning: " + reasoning, ColoredText.BLUE))
            
                break
            
            except Exception as e:
                print(ColoredText.color_text("ERROR: " + str(e), ColoredText.RED))

        return reasoning
        
    def run(self):
        print(ColoredText.color_text("Loading images and captions..", ColoredText.YELLOW))
        captions = load_text(self.file_caption_directory)

        print(ColoredText.color_text("Processing results..", ColoredText.YELLOW))
        
        df = captions[self.category].iloc[:, 0:2]
        for data_index, caption in zip(df.iloc[:, 0], df.iloc[:, 1]):
            reasoning = self.query(caption)

            self.results.append({
                "data_index": data_index,
                "reasoning": reasoning,
            })
        df = pd.DataFrame(self.results)
        df.to_excel(f"GPT4o_output_{self.category}_cap.xlsx", index=False)