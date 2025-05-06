#%%
from datasets import load_dataset
import json

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
# Baseline prompting with only function code, Python --> JS
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

##### code to look at specific examples #####
# data = ds_python['test'][5]
# print(f"""
# {data['declaration']} 
# {data['canonical_solution']}
#     """)

for idx, data in enumerate(ds_python['test']):
    # data = ds_python['test'][5]
    # idx = 5
    task_id = data['task_id']
    example_idx = random_exclude(idx)
    example_py = ds_python['test'][example_idx]
    example_js = ds_js['test'][example_idx]
    data_js = ds_js['test'][idx]

    prompt_v2 = f"""
# Translate the Python function to JavaScript.
## Python Code:
```
{example_py['declaration']}
{example_py['canonical_solution']}
```
## Python Test Cases:
```
{remove_metadata_block(example_py['test'])}
```
## JavaScript Code:
```
{example_js['declaration']}
{example_js['canonical_solution']}
```
# Translate the Python function to JavaScript.
## Python Code:
```
{data['declaration']}
{data['canonical_solution']}
```
## Python Test Cases:
```
{remove_metadata_block(data['test'])}
```
## JavaScript Code:
```
"""

    js_code = "\n".join(send_request(prompt_v2).split('\n')[1:-1])
    result_dict[task_id.split('/')[1]] = js_code

    with open("with_tests_python_to_js_code_v2.json", "w") as f:
        json.dump(result_dict, f, indent=2)
        
    time.sleep(4)

# %%