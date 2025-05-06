#%%
from datasets import load_dataset
from openai import OpenAI
import json
from dotenv import load_dotenv
import os
import random
import re

ds_python = load_dataset("THUDM/humaneval-x", "python")
ds_js = load_dataset("THUDM/humaneval-x", "js")

# load_dotenv(dotenv_path="../../.env")
# API_KEY = os.getenv("OPENAI_API_KEY")
API_KEY = '<insert key>'
client = OpenAI(api_key=API_KEY)

def random_exclude(n):    
    choices = list(range(164))
    choices.remove(n)
    return random.choice(choices)

def remove_metadata_block(code_str):
    return re.sub(r"(?s)METADATA\s*=\s*\{.*?\}\s*", "", code_str)

with open('../../generate-synthetic-tests/python/failed_asserts.json', "r") as f:
    failed_asserts = json.load(f)
with open('../../generate-synthetic-tests/python/passed_asserts.json', "r") as f:
    passed_asserts = json.load(f)

#%%
# Baseline prompting with only function code, Python --> JS
result_dict = {}
for idx, data in enumerate(ds_python['test']):
    task_id = data['task_id'].split('/')[1]
    example_idx = random_exclude(idx)
    example_py = ds_python['test'][example_idx]
    example_js = ds_js['test'][example_idx]
    prompt = f"""
You are given a Python function below.

Your task: Translate the function to JavaScript.
- The translated JavaScript code should preserve all functionalities in the original Python code.
- Use **camelCase** for all function and variable names, following JavaScript conventions.
- Make sure the translated code has function declaration.
- Output only the translated executable JavaScript code, nothing else.
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
{passed_asserts[data['task_id']]}
```
## JavaScript Code:
```
    """
    response = client.responses.create(
        model="gpt-3.5-turbo-0125",
        input=prompt
    )
    
    result_dict[task_id] = response.output_text
    
    with open("syn_python_to_js_code-output.json", "w") as f:
        json.dump(result_dict, f, indent=2)

# %%
with open("syn_python_to_js_code-output.json", "r") as f:
    result_dict = json.load(f)

cleaned_code = {}
for key, code in result_dict.items():
    lines = code.splitlines()
    start_idx = next((i for i, line in enumerate(lines) if line.strip().startswith(('function', 'const'))), 0)
    cleaned_code[key] = '\n'.join(lines[start_idx:])
    cleaned_code[key] = cleaned_code[key].replace("```", "")

with open("syn_python_to_js_code.json", "w") as f:
    json.dump(cleaned_code, f, indent=2)
# %%
