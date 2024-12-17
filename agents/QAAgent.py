import pandas as pd
import requests
from utils import ColoredText, load_text
import re

gpt_prompt = """
Your Role: Questions and Answers Generator

Objective:
Given a sample that includes a prompt and a textual reasoning that explains whether the given image is normal (reasonable and factual) or weird (hallucination, incorrect, distorted, and contrary to common sense), generate multi-choice questions that verify if the image is normal or weird.
When a correctly or incorrectly generated image is provided for a given prompt, these QA(Question and Answers) sets are designed to accurately assess and distinguish the factual information regarding the image.

You should also match each QA with the most related compositions of interest (CoI).
The table of CoIs includes existence, size/color/shape/posture, relation, scene, and counting.

Constraints:
- If the correct answer to a question in the QA set is given for a given image, the image should contain factual information. In other words, an incorrectly generated image should not have the correct answer.
- In reasoning, exclude context evidence (i.e., "The Scream of Nature" falls under which art movement?) that cannot be visually recognized. In other words, you should only generate QA sets based on visual evidence; only referring to context evidence for better understanding.
- Avoid including explicit expressions (i.e., "The Scream of Nature", "Edvard Munch", etc.) in your QA. Rather, replace them with general expressions like "the image".

You should follow the response format below:

[Response Format]
Set 1:
Compositions of Interest:
Question:
Choices:
A)
B)
C)
D)
Answer:

Set 2:
Compositions of Interest:
Question:
Choices:
A)
B)
C)
D)
Answer:

Set 3:
Compositions of Interest:
Question:
Choices:
A)
B)
C)
D)
- Answer:

Set 4:
Compositions of Interest:
Question:
Choices:
A)
B)
C)
D)
Answer:

Set 5:
Compositions of Interest:
Question:
Choices:
A)
B)
C)
D)
Answer:

Your Current Task:
Given the reasoning for an image, generate five possible QA sets. Ensure adherence to the response format provided above.

Caption: {caption}
Reasoning: {reasoning}
"""

def parse_questions(input_string):
    # Define regex patterns for questions, choices, and answers
    cois_pattern = re.compile(r"Compositions of Interest:\s*(.*?)\s*Question:", re.DOTALL)
    question_pattern = re.compile(r"Question:\s*(.*?)\s*Choices:", re.DOTALL)
    choices_pattern = re.compile(r"Choices:\s*(.*?)\s*Answer:", re.DOTALL)
    answer_pattern = re.compile(r"Answer:\s*(.*?)\s*(?=Set|\Z)", re.DOTALL)

    # Find all matches for questions, choices, and answers
    cois = cois_pattern.findall(input_string)
    questions = question_pattern.findall(input_string)
    choices = choices_pattern.findall(input_string)
    answers = answer_pattern.findall(input_string)

    return cois, questions, choices, answers

class QAAgent:
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
        self.file_reasoning_directory= f'data/LV_reasoning_{category}.xlsx'
        self.file_caption_directory= f'data/captions.xlsx'
    
    def query(self, caption, reasoning):
        self.payload["messages"][0]["content"][0]["text"] = gpt_prompt.format(caption=caption,
                                                                              reasoning=reasoning)

        status_code = True
        while status_code:
            response = requests.post("https://api.openai.com/v1/chat/completions", 
                                    headers=self.headers, 
                                    json=self.payload)
            
            if response.status_code == 200:
                print(ColoredText.color_text("Response status code: " + str(response.status_code), ColoredText.GREEN))
                status_code = False
            else:
                print(ColoredText.color_text("Response status code: " + str(response.status_code), ColoredText.RED))
        
        content = response.json()['choices'][0]['message']['content']
        cois, questions, choices, answers = parse_questions(content)
        
        return cois, questions, choices, answers
        
    def run(self):
        print(ColoredText.color_text("Loading reasonings..", ColoredText.YELLOW))
        reasoning_table = load_text(self.file_reasoning_directory)
        caption_table = load_text(self.file_caption_directory)
        data_indices, reasonings = reasoning_table['Sheet1'].iloc[:, 0], reasoning_table['Sheet1'].iloc[:, 4]
        df_caption = caption_table[self.category].iloc[:, 0:2]

        print(ColoredText.color_text("Processing results..", ColoredText.YELLOW))
        results = []
        for data_index, caption, reasoning in zip(data_indices, df_caption.iloc[:,1], reasonings):
            cois, questions, choices, answers = self.query(caption, reasoning)
                
            # Output results
            for _cois, question, choice, answer in zip(cois, questions, choices, answers):
                results.append({
                    "data_index": data_index,
                    "cois":  _cois.strip(),
                    "question":  question.strip(),
                    "choices": choice.strip(),
                    "answer": answer.strip()
                })
        df = pd.DataFrame(results)
        df.to_excel(f"GPT4o_QA_{self.category}_mod_cois.xlsx", index=False)

if __name__ == "__main__":
    category = "history"
    agent = QAAgent(category)
    agent.run()