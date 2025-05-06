#%%
from datasets import load_dataset
import json
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time

ds_python = load_dataset("THUDM/humaneval-x", "python")

load_dotenv(dotenv_path="../../.env")
GEMINI_KEY = os.getenv("GEMINI_KEY")
genai.configure(api_key=GEMINI_KEY)
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
result_dict = {}
with open('../../generate-synthetic-tests/gemini-2.0-flash/passed_asserts_python.json', "r") as f:
    passed_asserts = json.load(f)
    
for idx, data in enumerate(ds_python['test']):
    task_id = data['task_id']
    
    prompt_baseline = f"""
        You are given a Python function below.

        Your task: Translate the function to JavaScript.
        - The translated JavaScript code should preserve all functionalities in the original Python code.
        - Use **camelCase** for all function and variable names, following JavaScript conventions.
        - Output only the translated JavaScript code, nothing else.
        {data['declaration']}
        {data['canonical_solution']}
    """
    
    prompt_ground_truth_test = f"""
        You are given a Python function below.

        Your task: Translate the function to JavaScript.
        - The translated JavaScript code should preserve all functionalities in the original Python code.
        - Use **camelCase** for all function and variable names, following JavaScript conventions.
        - Output only the translated JavaScript code, nothing else.
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
        - Output only the translated JavaScript code, nothing else.
        {data['declaration']}
        {data['canonical_solution']}
        
        For reference, here are some test cases the original function passed, your translated function should also pass all the tests.
        {passed_asserts[task_id]}
    """
    
    # Change prompt passed to Gemini API
    js_code = "\n".join(send_request(prompt_baseline).split('\n')[1:-1])
    result_dict[task_id.split('/')[1]] = js_code
    
    with open("baseline-python_to_js_code.json", "w") as f:
        json.dump(result_dict, f, indent=2)
        
    time.sleep(4)

# %%