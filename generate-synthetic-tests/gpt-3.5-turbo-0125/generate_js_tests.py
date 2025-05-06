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
    
    response = client.responses.create(
        model="gpt-3.5-turbo-0125",
        input=prompt
    )
    
    task_id = data['task_id']
    tests_data[task_id] = response.output_text

    with open('./js-synthetic-tests-output.json', "w") as f:
        json.dump(tests_data, f, indent=2)
    
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
