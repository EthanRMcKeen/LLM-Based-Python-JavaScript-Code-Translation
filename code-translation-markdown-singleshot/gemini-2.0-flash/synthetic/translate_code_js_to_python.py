#%%
from datasets import load_dataset
import json
import time

ds_js = load_dataset("THUDM/humaneval-x", "js")
ds_python = load_dataset("THUDM/humaneval-x", "python")

import google.generativeai as genai
from dotenv import load_dotenv
import os

# load_dotenv(dotenv_path="../../.env")
# GEMINI_KEY = os.getenv("GEMINI_KEY")
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
with open('../../generate-synthetic-tests/gemini-2.0-flash-js/failed_asserts.json', "r") as f:
    failed_asserts = json.load(f)
with open('../../generate-synthetic-tests/gemini-2.0-flash-js/passed_asserts-JS-GEMINI-FINAL.json', "r") as f:
    passed_asserts = json.load(f)

#%%
import re
import random

def remove_metadata_block(code_str):
    return re.sub(r"(?s)METADATA\s*=\s*\{.*?\}\s*", "", code_str)

def random_exclude(n):    
    choices = list(range(164))
    choices.remove(n)
    return random.choice(choices)

result_dict = {}
for idx, data in enumerate(ds_js['test']):
    task_id = data['task_id']
    example_idx = random_exclude(idx)
    example_py = ds_python['test'][example_idx]
    example_js = ds_js['test'][example_idx]
    data_py = ds_python['test'][idx]
    
    prompt_v2 = f"""
You are given a JavaScript function below.
Your task: Translate the function to Python.
- The translated Python code should preserve all functionalities in the original JavaScript code.
- Use **snake_case** for all function and variable names, following Python conventions.
- Output only the translated Python code, nothing else.
- You are provided with an example translation for reference.
## JavaScript Code Example:
```
{example_js['declaration']}
{example_js['canonical_solution']}
```
## JavaScript Example Test Cases:
```
{example_js['test']}
```
## Python Code Example Translation:
```
{example_py['declaration']}
{example_py['canonical_solution']}
```
# Translate the JavaScript function to Python.
## JavaScript Code:
```
{data['declaration']}
{data['canonical_solution']}
```
## JavaScript Test Cases:
```
{passed_asserts[task_id]}
```
## Python Code:
```
"""
    python_code = "\n".join(send_request(prompt_v2).split('\n')[1:-1])
    result_dict[task_id.split('/')[1]] = python_code
    
    with open("with_tests_js_to_python_code_v2.json", "w") as f:
        json.dump(result_dict, f, indent=2)

    time.sleep(4)

# %%
