#%%
import google.generativeai as genai
from dotenv import load_dotenv
import os
from datasets import load_dataset
import time
import json

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

# %%
tests_data = {}
for data in ds_js['test']:
    prompt = f"""
        You are given a JavaScript function below.

        Your task: Generate exactly FIVE test cases to test the function.
        - Each test case must use `console.assert(...)`, and all should pass if the function is correct.
        - Output must contain five lines of assert statements. Not more, not less.
        - The provided function is assumed to be **correct** — all test cases MUST pass without raising an exception.
        {data['declaration']}
        {data['canonical_solution']}
    """
    task_id = data['task_id']
    tests_data[task_id] = send_request(prompt)

    with open('./gemini_tests.json', "w") as f:
        json.dump(tests_data, f, indent=2)
    time.sleep(4)
    
# %%
for key, value in tests_data.items():
    tests_only = "\n".join(
        line.strip() for line in value.splitlines()
        if line.strip().startswith("console.assert")
    )
    tests_data[key] = tests_only

with open('./js_tests_TEST-ONLY.json', "w") as f:
        json.dump(tests_data, f, indent=2)
        
# %%
