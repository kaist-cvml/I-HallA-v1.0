import pandas as pd
import requests
from utils import ColoredText, load_text
import re

gpt_prompt = """
Your Role: Composition of Interest Generator

Objective:
Given a sample that includes a [question, choices, and answer], Generate a composition of interest (CoI) that is related to the [question, choices, and answer].
The CoIs are Existence, Size, Color, Shape, Posture, Relation, Scene, and Counting. Pick the most relevant CoI from CoIs related to the given [question, choices, and answer].
You MUST generate ONLY JUST ONE CoI in CoIs. If you cannot find any relevant CoI in CoIs, Choose "Others".

[Response Example]
Set 1:
Question: What is depicted at the center of the molecule in the image?
Choices:
A) Carbon atom
B) Hydrogen atom
C) Oxygen atom
D) Nitrogen atom
Answer: A
CoI: Existence

Set 2:
Question: Which atoms are smaller in comparison to the central atom in the image?
Choices:
A) Carbon atoms
B) Hydrogen atoms
C) Oxygen atoms
D) Nitrogen atoms
Answer: B
CoI: Size

Set 3:
Question: How many hydrogen atoms are connected to the central atom in the image?
Choices:
A) Two
B) Three
C) Four
D) Five
CoI: Counting

Set 4:
Question: How are the hydrogen atoms positioned relative to the central carbon atom in the image?
Choices:
A) Opposite sides
B) Equidistant
C) Adjacent
D) Randomly
CoI: Relation

Set 5:
Question: Are the names of the states distinctly and correctly written?
Choices:
A) Yes
B) No
C) The image does not show any name.
D) Most states share the same name like "Segregation"
CoI: Scene

Set 6:
Question: What are the predominant colors in the flag visible in the image?
Choices:
A) Green and yellow
B) Red, white, and blue
C) Black and white
D) Orange and purple
CoI: Color

Set 7:
Question: What is included in the design of the Australian flag?
Choices:
A) A triangle
B) A circle
C) A square
D) A Union Jack
CoI: Shape

Set 8:
Question: Is the statue holding a sword downward?
Choices:
A) Yes
B) No
C) It holds a sword upward.
D) It holds no sword.
CoI: Posture


Question: {question}
Choices: {choices}
Answer: {answer}
"""

def parse_questions(input_string):
    # Define regex patterns for questions, choices, and answers
    cois_pattern = re.compile(r"CoI:\s*(.*?)\s*$", re.DOTALL)

    coi = cois_pattern.findall(input_string)
    
    return coi

class CoIAgent:
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
        self.file_reasoning_directory= f'data/GPT4o_QA_history_mod_cois.xlsx'
    
    def query(self, question, choices, answer):
        self.payload["messages"][0]["content"][0]["text"] = gpt_prompt.format(question=question, choices=choices, answer=answer)

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
        print(content)
        coi = parse_questions(content)
        
        return coi
        
    def run(self):
        print(ColoredText.color_text("Loading reasonings..", ColoredText.YELLOW))
        reasoning_table = load_text(self.file_reasoning_directory)
        data_indices, questions, choicess, answers = reasoning_table['Sheet1'].iloc[:, 0], reasoning_table['Sheet1'].iloc[:, 2], reasoning_table['Sheet1'].iloc[:, 3], reasoning_table['Sheet1'].iloc[:, 4]
        print(ColoredText.color_text("Processing results..", ColoredText.YELLOW))
        results = []

        for data_index, question, choices, answer in zip(data_indices, questions, choicess, answers):
            # if data_index >5:
            #     break
            coi = self.query(question, choices, answer)
            print('coi: ', coi)
            # Output results
            # for _cois, question, choice, answer in zip(cois, questions, choices, answers):
            results.append({
                "data_index": data_index,
                "coi":  coi[0],
                "question":  question.strip(),
                "choices": choices.strip(),
                "answer": answer.strip()
            })
        df = pd.DataFrame(results)
        df.to_excel(f"0812_history_CoIs.xlsx", index=False)