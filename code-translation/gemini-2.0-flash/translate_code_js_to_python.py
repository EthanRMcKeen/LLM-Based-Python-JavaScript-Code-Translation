#%%
from datasets import load_dataset
import json
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time

ds_js = load_dataset("THUDM/humaneval-x", "js")

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
with open('../../generate-synthetic-tests/gemini-2.0-flash/passed_asserts_js.json', "r") as f:
    passed_asserts = json.load(f)

for idx, data in enumerate(ds_js['test']):
    task_id = data['task_id']

    prompt_baseline = f"""
        You are given a JavaScript function below.

        Your task: Translate the function to Python.
        - The translated Python code should preserve all functionalities in the original JavaScript code.
        - Use **snake_case** for all function and variable names, following Python conventions.
        - Output only the translated Python code, nothing else.
        {data['declaration']}
        {data['canonical_solution']}
    """

    prompt_ground_truth_test = f"""
        You are given a JavaScript function below.

        Your task: Translate the function to Python.
        - The translated Python code should preserve all functionalities in the original JavaScript code.
        - Use **snake_case** for all function and variable names, following Python conventions.
        - Output only the translated Python code, nothing else.
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
        - Output only the translated Python code, nothing else.
        {data['declaration']}
        {data['canonical_solution']}
        
        For reference, here are some test cases the original function passed, your translated function should also pass all the tests.
        {passed_asserts[task_id]}
    """
    
    # Change prompt passed to Gemini API
    python_code = "\n".join(send_request(prompt_baseline).split('\n')[1:-1])
    result_dict[task_id.split('/')[1]] = python_code
    
    with open("baseline_js_to_python_code.json", "w") as f:
        json.dump(result_dict, f, indent=2)

    time.sleep(4)

# %%
