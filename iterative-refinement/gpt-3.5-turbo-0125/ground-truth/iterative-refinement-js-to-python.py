# %%
from datasets import load_dataset
import json
from openai import OpenAI

FILE_PATH = './baseline_js_to_python_code.json'
RESULTS_PATH = './RESULT-baseline_js_to_python_code.json'

with open(FILE_PATH, "r") as f:
    translated_code = json.load(f)

with open(RESULTS_PATH, "r") as f:
    results = json.load(f)

#%%
#setup data and gemini
ds_python = load_dataset("THUDM/humaneval-x", "python")
ds_js = load_dataset("THUDM/humaneval-x", "js")


import os

API_KEY = '<insert key>'
client = OpenAI(api_key=API_KEY)

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
    

def clean_code_string(code):
    lines = code.splitlines()
    # Find the index of the first line starting with 'def'
    start_idx = next((i for i, line in enumerate(lines) if line.strip().startswith('def')), 0)
    # Extract and clean the code
    cleaned_code = '\n'.join(lines[start_idx:])
    cleaned_code = cleaned_code.replace("```", "")
    return cleaned_code

result_dict = {}
for idx, data in enumerate(ds_js['test']):
    if str(idx) in results and results[str(idx)] == False:
        task_id = data['task_id']
        data_py = ds_python['test'][idx]
        all_test = remove_metadata_block(data_py['test'])

        prompt = f"""
# The following JavaScript code has been translated into the following Python code but the translation is incorrect, please correct the translation.
## JavaScript Code:
```
{data['declaration']}
{data['canonical_solution']}
```
## Incorrect Python Code:
```
{translated_code[str(idx)]}
```
## Correct Python Code:
```
"""
    
        response = client.responses.create(
            model="gpt-3.5-turbo-0125",
            input=prompt
        )
        corrected_python = response.output_text
        corrected_python = clean_code_string(corrected_python)
        success = run_py_test(task_id, corrected_python, all_test)
        
        if not success:
            for i in range(4):
                #print(f"first try failed for test: {idx}")
                prompt = f"""
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
## First Attempt Incorrect Python Code:
```
{translated_code[str(idx)]}
```
## Second Attempt Incorrect Python Code:
```
{corrected_python}
```
## Correct Python Code:
```
"""
                response = client.responses.create(
                    model="gpt-3.5-turbo-0125",
                    input=prompt
                )
                corrected_python = response.output_text
                corrected_python = clean_code_string(corrected_python)
                success = run_py_test(task_id, corrected_python, all_test)
                if success:
                    print(f"Example {idx} took {i+2} attempts")
                    break
        if not success:
            print(f"Example {idx} could not translate")


        result_dict[task_id] = response.output_text

        with open("iterative-refinement-correction-python.json", "w") as f:
            json.dump(result_dict, f, indent=2)
        


# %%

cleaned_code = {}
for key, code in result_dict.items():
    lines = code.splitlines()
    start_idx = next((i for i, line in enumerate(lines) if line.strip().startswith('def')), 0)
    cleaned_code[key] = '\n'.join(lines[start_idx:])
    cleaned_code[key] = cleaned_code[key].replace("```", "")

with open("iterative-refinement-correction-python.json", "w") as f:
    json.dump(cleaned_code, f, indent=2)

# %%
# Test on translated JS code

OUTPUT_PATH = './RESULT-iterative_refinement_js_to_python.json'
IR_PATH = 'iterative-refinement-correction-python.json'

with open(IR_PATH, "r") as f:
    corrected_code = json.load(f)

result_dict = {}
def extract_numbers(input_string):
    return ''.join(char for char in input_string if char.isdigit())

for task_id, code_str in corrected_code.items():
    idx = int(extract_numbers(task_id))
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
