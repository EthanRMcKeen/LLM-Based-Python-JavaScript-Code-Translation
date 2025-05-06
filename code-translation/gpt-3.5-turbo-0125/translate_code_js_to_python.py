#%%
from datasets import load_dataset
from openai import OpenAI
import json
from dotenv import load_dotenv
import os

ds_js = load_dataset("THUDM/humaneval-x", "js")

load_dotenv(dotenv_path="../../.env")
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

#%%
result_dict = {}
with open('../../generate-synthetic-tests/gpt-3.5-turbo-0125/passed_asserts_js.json', "r") as f:
    passed_asserts = json.load(f)


for idx, data in enumerate(ds_js['test']):
    task_id = data['task_id'].split('/')[1]
    
    prompt_baseline = f"""
        You are given a JavaScript function below.

        Your task: Translate the function to Python.
        - The translated Python code should preserve all functionalities in the original JavaScript code.
        - Use **snake_case** for all function and variable names, following Python conventions.
        - Make sure the translated code has function declaration.
        - Output only the translated executable Python code, nothing else.
        {data['declaration']}
        {data['canonical_solution']}
    """
    prompt_ground_truth_test = f"""
        You are given a JavaScript function below.

        Your task: Translate the function to Python.
        - The translated Python code should preserve all functionalities in the original JavaScript code.
        - Use **snake_case** for all function and variable names, following Python conventions.
        - Make sure the translated code has function declaration.
        - Output only the translated executable JavaScript code, nothing else.
        {data['declaration']}
        {data['canonical_solution']}
        
        For reference, here are some test cases the original function passed, your translated function should also pass all the tests.
        {data['test']}
    """
    
    prompt_synthetic_test = f"""
        You are given a JavaScript function below.

        Your task: Translate the function to Python.
        - The translated Python code should preserve all functionalities in the original JavaScript code.
        - Use **snake_case** for all function and variable names, following Python conventions.
        - Make sure the translated code has function declaration.
        - Output only the translated executable JavaScript code, nothing else.
        {data['declaration']}
        {data['canonical_solution']}
        
        For reference, here are some test cases the original function passed, your translated function should also pass all the tests.
        {passed_asserts[task_id]}
    """
    
    # Change prompt passed to Gemini API
    response = client.responses.create(
        model="gpt-3.5-turbo-0125",
        input=prompt_baseline
    )
    
    result_dict[task_id] = response.output_text
    
    with open("baseline_js_to_python_code-output.json", "w") as f:
        json.dump(result_dict, f, indent=2)

# %%
# Baseline Prompt Output Cleaning
cleaned_code = {}
for key, code in result_dict.items():
    lines = code.splitlines()
    start_idx = next((i for i, line in enumerate(lines) if line.strip().startswith('def')), 0)
    cleaned_code[key] = '\n'.join(lines[start_idx:])

with open("baseline_js_to_python_code.json", "w") as f:
    json.dump(cleaned_code, f, indent=2)

# Test-Aware Prompt Output Cleaning
cleaned_code = {}
for key, code in result_dict.items():
    lines = code.splitlines()
    start_idx = next((i for i, line in enumerate(lines) if line.strip().startswith('def')), 0)
    key = key.split('/')[1]
    cleaned_lines = [line for line in lines[start_idx:] if not line.strip().startswith('assert')]
    if cleaned_lines[-1] == '```':
        cleaned_lines = cleaned_lines[:-1]
    cleaned_code[key] = '\n'.join(cleaned_lines).split('def test_')[0]

with open("with_test_js_to_python_code.json", "w") as f:
    json.dump(cleaned_code, f, indent=2)
# %%
