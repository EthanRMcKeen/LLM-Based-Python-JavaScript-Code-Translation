#%%
from datasets import load_dataset
import json
import os
import subprocess
import pandas as pd

ds_js = load_dataset("THUDM/humaneval-x", "js")

FOLDER_PATH = './gemini-2.0-flash/'

with open(f'{FOLDER_PATH}gemini_js_tests_TEST-ONLY.json', "r") as f:
    tests_data = json.load(f)

result_dict = {}
failed_dict = {}

for idx, data in enumerate(ds_js['test']):
    base_code =data['declaration'].strip('\t') + '\n' + data['canonical_solution'].strip('\t')
    task_id = data['task_id']
    assert_lines = tests_data[task_id].split('\n')

    passed_asserts = []
    failed_asserts = []

    for assert_line in assert_lines:
        test_code = base_code.strip('\t') + '\n' + assert_line.strip('\t')

        with open("temp_test.js", "w") as f:
            f.write(test_code)
        
        task_id = data['task_id']
        try:
            result = subprocess.run(
                ["node", "temp_test.js"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.stderr:   # Need manual check for stringToMD5 function, requires js package import
                failed_asserts.append(assert_line.strip('\t'))
            else:
                passed_asserts.append(assert_line.strip('\t'))
        except subprocess.TimeoutExpired:
            print(task_id, assert_line)
            
    result_dict[task_id] = "\n".join(passed_asserts)
    failed_dict[task_id] = "\n".join(failed_asserts)

os.remove("temp_test.js")
with open(f"{FOLDER_PATH}passed_asserts_js.json", "w") as f:
    json.dump(result_dict, f, indent=2)
with open(f"{FOLDER_PATH}failed_asserts_js.json", "w") as f:
    json.dump(failed_dict, f, indent=2)
  
# %%
df = pd.DataFrame([
    {"task_id": k, "number of passed tests": v.count("assert")}
    for k, v in result_dict.items()
])

df['number of passed tests'].value_counts().sort_index()
# %%
