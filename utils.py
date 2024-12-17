import pandas as pd
import os
import sys

def load_image(file_path):
    image_filenames = []
    for root, dirs, files in os.walk(file_path):
        for filename in files:
            if filename.lower().endswith(".jpg"):  
                image_path = f"{root}/{filename}"
                image_filenames.append(image_path)
    return image_filenames

def load_text(file_path):
    if os.path.exists(file_path):
        excel_file = pd.ExcelFile(file_path)
        tables = {}
        for sheet_name in excel_file.sheet_names:
            tables[sheet_name] = pd.read_excel(file_path, sheet_name=sheet_name)
    
        return tables
    else:
        print(ColoredText.color_text("File not found:" + file_path, ColoredText.RED))
        sys.exit()

class ColoredText:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    
    color_list = [GREEN, YELLOW, BLUE, MAGENTA, CYAN]

    @staticmethod
    def color_text(text, color):
        return color + text + ColoredText.RESET