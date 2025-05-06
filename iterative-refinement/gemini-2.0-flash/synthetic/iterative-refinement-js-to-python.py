# %%
from datasets import load_dataset
import json

FILE_PATH = './with_tests_js_to_python_code_v2.json'
RESULTS_PATH = './RESULT-with_tests_js_to_python_code_v2.json'

with open(FILE_PATH, "r") as f:
    translated_code = json.load(f)

with open(RESULTS_PATH, "r") as f:
    results = json.load(f)

#%%

with open('./passed_asserts-JS-GEMINI-FINAL.json', "r") as f:
    passed_asserts = json.load(f)

#%%
#setup data and gemini
ds_python = load_dataset("THUDM/humaneval-x", "python")
ds_js = load_dataset("THUDM/humaneval-x", "js")

import google.generativeai as genai
from dotenv import load_dotenv
import os

#load_dotenv(dotenv_path="../../.env")
#GEMINI_KEY = os.getenv("GEMINI_KEY")
genai.configure(api_key="<insert key>")
gemini = genai.GenerativeModel("gemini-2.0-flash")
def send_request(prompt, max_tokens=512, temperature=0.8):
    try:
        response = gemini.generate_content(
            [prompt],
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            ),
        )
        if response:
            return response.text
    except Exception as e:
        print(e)
    return ''

#%%
import time
import re
import random
import tempfile
import subprocess

def remove_metadata_block(code_str):
    return re.sub(r"(?s)METADATA\s*=\s*\{.*?\}\s*", "", code_str)

def run_py_test(task_id: str, py_code: str, test_code: str) -> bool:
    complete_test_code = py_code + '\n' + test_code
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
        tmp.write(complete_test_code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(["python", tmp_path], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    

result_dict = {}
for idx, data in enumerate(ds_js['test']):
    if str(idx) in results and results[str(idx)] == False:
        task_id = data['task_id']

        prompt_v2 = f"""
# The following JavaScript code has been translated into the following Python code but the translation is incorrect.
Your task: Correct the translation to Python.
- The translated Python code should preserve all functionalities in the original JavaScript code.
- Use **snake_case** for all function and variable names, following Python conventions.
- Output only the translated Python code, nothing else.
## JavaScript Code:
```
{data['declaration']}
{data['canonical_solution']}
```
## JavaScript Test Cases:
```
{passed_asserts[task_id]}
```
## Incorrect Python Code:
```
{translated_code[str(idx)]}
```
## Correct Python Code:
```
"""
    
        js_code = "\n".join(send_request(prompt_v2).split('\n')[1:-1])
        result_dict[task_id.split('/')[1]] = js_code

        with open("iterative-refinement-correction-python_v2.json", "w") as f:
            json.dump(result_dict, f, indent=2)
        
        time.sleep(4)

# %%
# Test on translated JS code

OUTPUT_PATH = './RESULT-iterative_refinement_js_to_python_v2.json'
IR_PATH = 'iterative-refinement-correction-python_v2.json'

with open(IR_PATH, "r") as f:
    corrected_code = json.load(f)

result_dict = {}

for task_id, code_str in corrected_code.items():
    idx = int(task_id)
    data = ds_python['test'][idx]
    all_test = remove_metadata_block(data['test'])
    complete_test_code = code_str + '\n' + all_test
    # check all 164 pass on ground truth
    # complete_test_code = f"""
    # {data['declaration']}
    # {data['canonical_solution']}
    # {all_test}
    # """

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
        tmp.write(complete_test_code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(["python", tmp_path], capture_output=True, text=True, timeout=5)
    except subprocess.TimeoutExpired:
        continue

    if result.returncode == 0:
        result_dict[task_id] = True
    else:
        result_dict[task_id] = False

os.remove(tmp_path)
with open(OUTPUT_PATH, "w") as f:
    json.dump(result_dict, f, indent=2)

true_count = sum(value is True for value in result_dict.values())
false_count = sum(value is False for value in result_dict.values())

print(f"Corrected Python Code - True: {true_count}, False: {false_count}")


# %%
