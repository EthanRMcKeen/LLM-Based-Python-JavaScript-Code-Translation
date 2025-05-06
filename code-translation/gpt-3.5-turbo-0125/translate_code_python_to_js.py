#%%
from datasets import load_dataset
from openai import OpenAI
import json
from dotenv import load_dotenv
import os

ds_python = load_dataset("THUDM/humaneval-x", "python")

load_dotenv(dotenv_path="../../.env")
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

#%%
result_dict = {}
with open('../../generate-synthetic-tests/gpt-3.5-turbo-0125/passed_asserts_python.json', "r") as f:
    passed_asserts = json.load(f)
    
for idx, data in enumerate(ds_python['test']):
    task_id = data['task_id']
    
    prompt_baseline = f"""
        You are given a Python function below.

        Your task: Translate the function to JavaScript.
        - The translated JavaScript code should preserve all functionalities in the original Python code.
        - Use **camelCase** for all function and variable names, following JavaScript conventions.
        - Make sure the translated code has function declaration.
        - Output only the translated executable JavaScript code, nothing else.
        {data['declaration']}
        {data['canonical_solution']}
    """
    
    prompt_ground_truth_test = f"""
        You are given a Python function below.

        Your task: Translate the function to JavaScript.
        - The translated JavaScript code should preserve all functionalities in the original Python code.
        - Use **camelCase** for all function and variable names, following JavaScript conventions.
        - Make sure the translated code has function declaration.
        - Output only the translated executable JavaScript code, nothing else.
        {data['declaration']}
        {data['canonical_solution']}
        
        For reference, here are some test cases the original function passed, your translated function should also pass all the tests.
        {data['test']}
    """
    
    prompt_synthetic_test = f"""
        You are given a Python function below.

        Your task: Translate the function to JavaScript.
        - The translated JavaScript code should preserve all functionalities in the original Python code.
        - Use **camelCase** for all function and variable names, following JavaScript conventions.
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
    
    
    with open("gt-js-output.json", "w") as f:
        json.dump(result_dict, f, indent=2)
        

# %%
# Baseline Prompt Output Cleaning
cleaned_code = {}
for key, code in result_dict.items():
    lines = code.splitlines()
    start_idx = next((i for i, line in enumerate(lines) if line.strip().startswith('function')), 0)
    cleaned_code[key] = '\n'.join(lines[start_idx:])

with open("baseline_python_to_js_code.json", "w") as f:
    json.dump(cleaned_code, f, indent=2)

# Test-Aware Prompt Output Cleaning
cleaned_code = {}
for key, code in result_dict.items():
    lines = code.splitlines()
    start_idx = next((i for i, line in enumerate(lines) if line.strip().startswith('function')), 0)
    key = key.split('/')[1]
    if lines[-1] == '```':
        lines = lines[:-1]
    cleaned_code[key] = '\n'.join(lines[start_idx:]).split('function check(')[0]

with open("with_test_python_to_js_code.json", "w") as f:
    json.dump(cleaned_code, f, indent=2)
# %%
