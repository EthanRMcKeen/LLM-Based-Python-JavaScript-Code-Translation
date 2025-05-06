# %%
# Test on translated JS code
from datasets import load_dataset
import json
import os
import subprocess

FOLDER_PATH = './gemini-2.0-flash/'

ds_js = load_dataset("THUDM/humaneval-x", "js")
with open(f'{FOLDER_PATH}baseline_python_to_js_code.json', "r") as f:
    translated_code = json.load(f)

result_dict = {}
for data in ds_js['test']:
    all_test = data['test']
    task_id = data['task_id'].split('/')[1]
    complete_test_code = translated_code[task_id] + '\n' + all_test

    with open("temp_test.js", "w") as f:
        f.write(complete_test_code)

    result = subprocess.run(["node", "temp_test.js"], capture_output=True, text=True)
    if result.stderr:
        result_dict[task_id] = False
    else:
        result_dict[task_id] = True

os.remove("temp_test.js")
with open(f'{FOLDER_PATH}RESULT-baseline_python_to_js_code.json', "w") as f:
    json.dump(result_dict, f, indent=2)
    
true_count = sum(value is True for value in result_dict.values())
false_count = sum(value is False for value in result_dict.values())

print(f"Translated JS Code - True: {true_count}, False: {false_count}")
