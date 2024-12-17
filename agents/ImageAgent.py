import base64
import pandas as pd
import requests
from utils import ColoredText, load_image, load_text
from .fewshot import fewshot_captions, fewshot_responses, fewshot_reasonings
from agents.ReasoningAgent import ReasoningAgent

example_api = """
### Example {example_number}
- Caption: {example_caption}
- Response: {example_response}
- Reasoning: {example_reasoning}
- Image:
"""

gpt_prompt = """
Your Role: Excellent Image Distinguisher

Objective: Given the input image and caption, Distinguish whether the given image is normal (reasonable and factual), or if it is weird (incorrect, distorted, and contrary to common sense).
More specifically, if the truth is important such as science and history, you might need to say "weird" for the given image is different from the fact; otherwise "normal".

Your reasoning must be as detailed as it covers the explanations about almost every component within the image.
When determining if an image is normal or weird, do not judge it solely based on whether it has a virtual or cartoon-like style.

You should follow the response format below:

[Response Format]
- Response: <Normal or Weird>
- Reasoning: <Your reasoning about why you have made this decision>
  - **Visual Evidence**: <Your reasoning about why you made this decision solely based on the visual appearance>
  - **Contextual Evidence**: <Your reasoning about why you made this decision solely based on the context>

When evaluating an image, use very detailed aspects of the image and compare them with reality as the basis for your judgment.
For example, consider the number of objects in the image, the shapes of structures, the number of floors in buildings, and other similar information. Compare these details with real-life facts to distinguish and identify the image accurately.

We provide you with a few-shot examples to help you better handle your task.

For each example below, an input image is given and paired with three parameters: the caption for the normal image, the response, and the reasoning.
Considering these few-shot examples, we expect you to successfully achieve your current task.

[Example]
"""

goal_prompt = """
Your Current Task:
Given the input image and its corresponding caption, distinguish whether it is weird or normal. Ensure adherence to the response format provided above.

Caption: {caption}
Image:
"""

class ImageAgent:
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
            # few-shot examples
            # example 1
            {
                "type": "text",
                "text": ""
            },
            {
                "type": "image_url",
                "image_url": {
                "url": ""
                }
            },
            # example 2
            {
                "type": "text",
                "text": ""
            },
            {
                "type": "image_url",
                "image_url": {
                "url": ""
                }
            },
            # example 3
            {
                "type": "text",
                "text": ""
            },
            {
                "type": "image_url",
                "image_url": {
                "url": ""
                }
            },
            # example 4
            {
                "type": "text",
                "text": ""
            },
            {
                "type": "image_url",
                "image_url": {
                "url": ""
                }
            },
            # goal prompt
            {
                "type": "text",
                "text": ""
            },
            {
                "type": "image_url",
                "image_url": {
                "url": ""
                }
            }
            ]
        }
        ],
    }

    def __init__(self, api_key, category=None):
        self.api_key = api_key
        self.category = category
        self.results = []
        self.file_image_directory = f"data/models/dalle-3/{category}/"
        self.file_caption_directory= 'data/captions.xlsx'
        self.fewshot_caption_directory = f"data/fewshot/"
        self.fewshot_images = []
        self.reasoningAgent = ReasoningAgent(api_key=api_key)
        
        self.payload["messages"][0]["content"][0]["text"] = gpt_prompt
    
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def generate_example(self,
                         number: int,
                         caption: str, 
                         response: str, 
                         reasoning: str):
        language = example_api.format(example_number=str(number+1),
                                      example_caption=caption,
                                      example_response=response,
                                      example_reasoning=reasoning)
        self.payload["messages"][0]["content"][1 + number*2]["text"] = language
        self.payload["messages"][0]["content"][2 + number*2]["image_url"]["url"] = f"data:image/jpeg;base64,{self.fewshot_images[number]}"

    def query(self, image, caption):
        language = goal_prompt.format(caption=caption)
        self.payload["messages"][0]["content"][9]["text"] = language
        self.payload["messages"][0]["content"][10]["image_url"]["url"] = f"data:image/jpeg;base64,{image}"

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
                response = content.split("Response:")[1].split("\n")[0].strip()
                reasoning = content.split("Reasoning:")[1].strip()

                print(ColoredText.color_text("Response: " + response, ColoredText.BLUE))
                print(ColoredText.color_text("Reasoning: " + reasoning, ColoredText.BLUE))
            
                break
            
            except Exception as e:
                print(ColoredText.color_text("ERROR: " + str(e), ColoredText.RED))

        return response, reasoning
        
    def run(self):
        print(ColoredText.color_text("Loading images and captions..", ColoredText.YELLOW))
        captions = load_text(self.file_caption_directory)
        images = load_image(self.file_image_directory)
        fewshot_images = load_image(self.fewshot_caption_directory)
        
        for image_path in fewshot_images:
            image = self.encode_image(image_path)
            self.fewshot_images.append(image)

        for count, (_caption, _reasoning, _response) in enumerate(zip(fewshot_captions, fewshot_responses, fewshot_reasonings)):
            self.generate_example(count, _caption, _reasoning, _response)

        print(ColoredText.color_text("Processing results..", ColoredText.YELLOW))

        for image_path in images:
            data_index = int(image_path.split('/')[-1].split('.')[0])
            status = image_path.split('/')[-2] # normal or weird for GT

            reasonings_correct, reasonings_wrong, responses = [], [], []
            for _ in range(5):
                image = self.encode_image(image_path)
                caption = captions[self.category][captions[self.category].iloc[:, 0] == data_index].iloc[0, 1]

                response, reasoning = self.query(image, caption)
                response = response.split('\n')[0]

                responses.append(response)
                if status.lower() == response.lower():
                    reasonings_correct.append(reasoning)
                else:
                    reasonings_wrong.append(reasoning)
            candidate_reasonings_correct, combined_reasonining_correct = self.reasoningAgent.query(reasonings_correct)
            candidate_reasonings_wrong, combined_reasonining_wrong = self.reasoningAgent.query(reasonings_wrong)
            self.results.append({
                "data_index": data_index,
                "status": status,
                "response": ','.join(responses),
                "combined_reasonining_correct": combined_reasonining_correct,
                "combined_reasonining_wrong": combined_reasonining_wrong,
                "candidate_reasonings_correct": candidate_reasonings_correct,
                "candidate_reasonings_wrong": candidate_reasonings_wrong,
            })
        df = pd.DataFrame(self.results)
        df.to_excel(f"GPT4o_output_{self.category}_img.xlsx", index=False)
        