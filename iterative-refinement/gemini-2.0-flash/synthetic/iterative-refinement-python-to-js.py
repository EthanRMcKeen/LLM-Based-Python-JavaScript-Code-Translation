# %%
from datasets import load_dataset
import json

FILE_PATH = './with_tests_python_to_js_code.json'
RESULTS_PATH = './RESULT-with_tests_python_to_js_code.json'

ds_js = load_dataset("THUDM/humaneval-x", "js")
with open(FILE_PATH, "r") as f:
    translated_code = json.load(f)

with open(RESULTS_PATH, "r") as f:
    results = json.load(f)

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

def remove_metadata_block(code_str):
    return re.sub(r"(?s)METADATA\s*=\s*\{.*?\}\s*", "", code_str)

def random_exclude(n):    
    choices = list(range(164))
    choices.remove(n)
    return random.choice(choices)

result_dict = {}
for idx, data in enumerate(ds_python['test']):
    if str(idx) in results and results[str(idx)] == False:
        task_id = data['task_id']

        prompt_v2 = f"""
# The following Python code has been translated into the following JavaScript code but the translation is incorrect, please correct the translation.
## Python Code:
```
{data['declaration']}
{data['canonical_solution']}
```
## Incorrect JavaScript Code:
```
{translated_code[str(idx)]}
```
## Correct JavaScript Code:
```
"""
    
        js_code = "\n".join(send_request(prompt_v2).split('\n')[1:-1])
        result_dict[task_id.split('/')[1]] = js_code

        with open("iterative-refinement-correction-js.json", "w") as f:
            json.dump(result_dict, f, indent=2)
        
        time.sleep(4)
# %%
# Test on translated JS code
import subprocess

OUTPUT_PATH = './RESULT-iterative_refinement_python_to_js.json'
IR_PATH = 'iterative-refinement-correction-js.json'

with open(IR_PATH, "r") as f:
    corrected_code = json.load(f)

result_dict = {}

for task_id, code_str in corrected_code.items():
    idx = int(task_id)
    data = ds_js['test'][idx]
    all_test = data['test']
    complete_test_code = code_str + '\n' + all_test
    # check all 164 pass on ground truth
    # complete_test_code = f"""
    # {data['declaration']}
    # {data['canonical_solution']}
    # {all_test}
    # """

    with open("temp_test.js", "w") as f:
        f.write(complete_test_code)

    result = subprocess.run(["node", "temp_test.js"], capture_output=True, text=True)
    if "Assertion failed" in result.stderr:
        result_dict[task_id] = False
    else:
        result_dict[task_id] = True

os.remove("temp_test.js")
with open(OUTPUT_PATH, "w") as f:
    json.dump(result_dict, f, indent=2)
    
true_count = sum(value is True for value in result_dict.values())
false_count = sum(value is False for value in result_dict.values())

print(f"Corrected JS Code - True: {true_count}, False: {false_count}")

# %%
