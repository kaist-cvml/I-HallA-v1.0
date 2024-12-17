import requests
import json
from utils import ColoredText, load_image, load_text
import base64
from transformers import AutoProcessor, Blip2ForConditionalGeneration
import torch
from PIL import Image

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

class BLIP2:
    processor = AutoProcessor.from_pretrained("Salesforce/blip2-opt-2.7b")
    model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-2.7b", torch_dtype=torch.float16)
    
    def __init__(self, category) -> None:
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.category = category
        self.model_version = "dalle-3" # "dalle-3", "sd-v1-4", "sd-v1-5", "sd-v2-0", "sd-xl"
        self.image_type = "normal" # "normal/weird"
        self.file_image_directory = f"data/models/{self.model_version}/{self.category}/{self.image_type}"
        self.file_qas_directory= f"data/GPT4o_QA_{self.category}_mod_cois.xlsx"


    def encode_image(self, image_path):
        image = Image.open(image_path).convert('RGB')
        return image
        
    def query(self, image, question, choices):
        language = gpt_prompt.format(question=question,
                                     choices=choices)

        inputs = self.processor(image, text=language, return_tensors="pt").to(self.device, torch.float16)

        generated_ids = self.model.generate(**inputs, max_new_tokens=20)
        content = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

        if "Answer:" in content:
            answer = content.split("Answer:")[1].split("\n")[0].strip()
        else:
            answer = content.strip()

        print(ColoredText.color_text("["+answer+"]", ColoredText.BLUE))

        return answer


    def run(self):
        qas = load_text(self.file_qas_directory)
        data_indices, qas_cois, qas_questions, qas_choices, qas_answers = qas['Sheet1'].iloc[:, 0], qas['Sheet1'].iloc[:, 1], qas['Sheet1'].iloc[:, 2], qas['Sheet1'].iloc[:, 3], qas['Sheet1'].iloc[:, 4]
        images = load_image(self.file_image_directory)

        target_index = 1
        tot_score = 0
        for image_path in images:
            data_index = int(image_path.split('/')[-1].split('.')[0])
            
            if data_index != target_index:
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
