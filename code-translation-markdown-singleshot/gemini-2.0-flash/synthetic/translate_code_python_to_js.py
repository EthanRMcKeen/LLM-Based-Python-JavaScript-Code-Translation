#%%
from datasets import load_dataset
import json

ds_python = load_dataset("THUDM/humaneval-x", "python")

import google.generativeai as genai
from dotenv import load_dotenv
import os

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
with open('../../generate-synthetic-tests/gemini-2.0-flash-python/failed_asserts.json', "r") as f:
    failed_asserts = json.load(f)
with open('../../generate-synthetic-tests/gemini-2.0-flash-python/passed_asserts.json', "r") as f:
    passed_asserts = json.load(f)
#%%
# Baseline prompting with only function code, Python --> JS
import time

result_dict = {}
for idx, data in enumerate(ds_python['test']):
    task_id = data['task_id']

    # prompt = f"""
    #     You are given a Python function below.

    #     Your task: Translate the function to JavaScript.
    #     - The translated JavaScript code should preserve all functionalities in the original Python code.
    #     - Use **camelCase** for all function and variable names, following JavaScript conventions.
    #     - Output only the translated JavaScript code, nothing else.
    #     {data['declaration']}
    #     {data['canonical_solution']}
        
    #     For reference, here are some test cases the original function passed and failed. 
    #     Your translated function should pass all the passed tests and fail the same failed tests.
    #     Passed tests:
    #     {passed_asserts[task_id]}
    #     Failed tests:
    #     {failed_asserts[task_id]}
    # """
    
    prompt_v2 = f"""
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
    
    js_code = "\n".join(send_request(prompt_v2).split('\n')[1:-1])
    result_dict[task_id.split('/')[1]] = js_code
    
    with open("with_tests_python_to_js_code_v2.json", "w") as f:
        json.dump(result_dict, f, indent=2)
        
    time.sleep(4)

# %%