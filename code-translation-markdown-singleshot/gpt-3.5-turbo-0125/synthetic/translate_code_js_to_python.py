#%%
from datasets import load_dataset
from openai import OpenAI
import json
from dotenv import load_dotenv
import os
import random

ds_js = load_dataset("THUDM/humaneval-x", "js")
ds_python = load_dataset("THUDM/humaneval-x", "python")

#load_dotenv(dotenv_path="../../.env")
#API_KEY = os.getenv("OPENAI_API_KEY")
API_KEY = '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'
client = OpenAI(api_key=API_KEY)

def random_exclude(n):    
    choices = list(range(164))
    choices.remove(n)
    return random.choice(choices)

with open('../../generate-synthetic-tests/js/failed_asserts.json', "r") as f:
    failed_asserts = json.load(f)
with open('../../generate-synthetic-tests/js/passed_asserts.json', "r") as f:
    passed_asserts = json.load(f)

#%%
# Baseline prompting with only function code, JS --> Python
result_dict = {}
for idx, data in enumerate(ds_js['test']):
    task_id = data['task_id'].split('/')[1]
    example_idx = random_exclude(idx)
    example_py = ds_python['test'][example_idx]
    example_js = ds_js['test'][example_idx]
    
    prompt = f"""
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
{data['test']}
```
## Python Code:
```
    """
    response = client.responses.create(
        model="gpt-3.5-turbo-0125",
        input=prompt
    )
    
    result_dict[task_id] = response.output_text
    
    with open("syn_js_to_python_code-output.json", "w") as f:
        json.dump(result_dict, f, indent=2)

# %%

cleaned_code = {}
for key, code in result_dict.items():
    lines = code.splitlines()
    start_idx = next((i for i, line in enumerate(lines) if line.strip().startswith('def')), 0)
    cleaned_code[key] = '\n'.join(lines[start_idx:])
    cleaned_code[key] = cleaned_code[key].replace("```", "")

with open("syn_js_to_python_code.json", "w") as f:
    json.dump(cleaned_code, f, indent=2)
# %%
