import base64
import pandas as pd
import requests
from utils import ColoredText, load_image, load_text

gpt_prompt = """
You are an agent who answers questions based on the given image.
Here, the given image could be wrong.

So, your job is to either choose the best answer choice or output "None" for ambiguous questions.

Your answer must choose one of the given choices to your best knowledge.
It must be a single character that indicates its answer (i.e., "A", "B", "C", "D", "None").
As shown below [Example], your answer should not include texts other than a single character ("A", "B", "C", "D", and "None").

[Example]
Question: How many continents are shown as connected in the image?
Choices:
A) Korean Peninsula
B) One large supercontinent
C) Two separate continents
D) Three continents joined together
Answer: B

Question: How many atoms of the molecule in the image?
Choices:
A) 1
B) 2
C) 3
D) 4
Answer: None

DO NOT use your external knowledge obtained by pre-training large-scale data.
You must base your judgment on the image input's visual evidence.
If you are not sure or there is no appropriate answer choice, you can output "Answer: None".
You should answer the following question:

[Question]
Question: {question}
Choices: {choices}

[Response Format]
Answer:
"""

class EvaluationAgent:
    api_key = "[YOUR_API_KEY]"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
        {
            "role": "user",
            "content": [
            {
                "type": "image_url",
                "image_url": {
                "url": ""
                }
            },
            {
                "type": "text",
                "text": ""
            }
            ]
        }
        ],
    }

    def __init__(self, api_key, category=None):
        self.api_key = api_key
        self.category = category
        self.results = []
        # self.coi_table = ["existence", "size", "color", "shape", "posture", "relation", "scene", "counting"]
        self.model_version = "sd-v1-4" # "dalle-3", "sd-v1-4", "sd-v1-5", "sd-v2-0", "sd-xl"
        self.image_type = "weird" # "normal/weird"
        self.file_image_directory = f"data/models/{self.model_version}/{self.category}/{self.image_type}/"
        self.file_qas_directory= f"data/GPT4o_QA_{self.category}_mod_cois.xlsx"
        
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def query(self, image, question, choices):
        # coi_others = ", ".join([item.lower() for item in self.coi_table if item.lower() != coi.lower()])
        language = gpt_prompt.format(question=question,
                                     choices=choices)
        self.payload["messages"][0]["content"][0]["image_url"]["url"] = f"data:image/jpeg;base64,{image}"
        self.payload["messages"][0]["content"][1]["text"] = language

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

                if "Answer:" in content:
                    answer = content.split("Answer:")[1].split("\n")[0].strip()
                else:
                    answer = content.strip()

                if answer != "":
                    break
            
            except Exception as e:
                print(ColoredText.color_text("ERROR: " + str(e), ColoredText.RED))

        print(ColoredText.color_text("["+answer+"]", ColoredText.BLUE))

        return answer
        
    def run(self):
        print(ColoredText.color_text("Loading images and captions..", ColoredText.YELLOW))
        qas = load_text(self.file_qas_directory)
        data_indices, qas_cois, qas_questions, qas_choices, qas_answers = qas['Sheet1'].iloc[:, 0], qas['Sheet1'].iloc[:, 1], qas['Sheet1'].iloc[:, 2], qas['Sheet1'].iloc[:, 3], qas['Sheet1'].iloc[:, 4]
        images = load_image(self.file_image_directory)

        print(ColoredText.color_text("Processing results..", ColoredText.YELLOW))

        target_index = 100 # Total number of data
        tot_score = 0
        for image_path in images:
            data_index = int(image_path.split('/')[-1].split('.')[0])
            
            if data_index <= target_index:
                continue
            print()
            image = self.encode_image(image_path)
            
            score = 0
            for qas_data_index, coi, question, choices, answer in zip(data_indices, qas_cois, qas_questions, qas_choices, qas_answers):
                if data_index != qas_data_index:
                    continue
                _answer = self.query(image, question, choices)
                if answer[0].lower() == _answer[0].lower():
                    score += 1

                self.results.append({
                    "model_version": self.model_version,
                    "data_index": data_index,
                    "question":  question,
                    "choices":  choices,
                    "gt_answer": answer[0].lower(),
                    "pred_answer": _answer[0].lower(),
                    "full_answer": _answer,
                    "score": score / 5,
                })

            tot_score += score

            # if score == 5:
            #     tot_score += 1
            #     print(ColoredText.color_text("Correct", ColoredText.GREEN))
            # else:
            #     print(ColoredText.color_text("Wrong", ColoredText.RED))

        print("score:", tot_score / (5 * target_index)) # (5 * len(target_index)))
        self.results.append({
            "model_version": "",
            "data_index": "",
            "question": "",
            "choices": "",
            "gt_answer": "",
            "pred_answer": "",
            "full_answer": "",
            "score": tot_score / (5 * target_index),
        })
        df = pd.DataFrame(self.results)
        df.to_excel(f"score_{self.category}_{self.model_version}_{self.image_type}-rough.xlsx", index=False)
        
