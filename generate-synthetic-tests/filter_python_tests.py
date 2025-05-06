#%%
from datasets import load_dataset
import json
import os
import subprocess
import tempfile
import pandas as pd

ds_python = load_dataset("THUDM/humaneval-x", "python")
    
FOLDER_PATH = './gemini-2.0-flash/'

with open(f'{FOLDER_PATH}gemini_python_tests_TEST-ONLY.json', "r") as f:
    tests_data = json.load(f)

result_dict = {}
failed_dict = {}

for idx, data in enumerate(ds_python['test']):
    base_code =data['declaration'].strip('\t') + '\n' + data['canonical_solution'].strip('\t')
    task_id = data['task_id']
    assert_lines = tests_data[task_id].split('\n')

    passed_asserts = []
    failed_asserts = []

    for assert_line in assert_lines:
        test_code = base_code.strip('\t') + '\n' + assert_line.strip('\t')

        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
            tmp.write(test_code)
            tmp_path = tmp.name

        try:
            result = subprocess.run(["python", tmp_path], capture_output=True, text=True, timeout=5)
        except subprocess.TimeoutExpired:
            os.remove(tmp_path)
            continue
        os.remove(tmp_path)

        if result.returncode == 0:
            passed_asserts.append(assert_line.strip('\t'))
        else:
            failed_asserts.append(assert_line.strip('\t'))
            
    result_dict[task_id] = "\n".join(passed_asserts)
    failed_dict[task_id] = "\n".join(failed_asserts)

with open(f"{FOLDER_PATH}passed_asserts_python.json", "w") as f:
    json.dump(result_dict, f, indent=2)
with open(f"{FOLDER_PATH}failed_asserts_python.json", "w") as f:
    json.dump(failed_dict, f, indent=2)
    
# %%
df = pd.DataFrame([
    {"task_id": k, "number of passed tests": v.count("assert")}
    for k, v in result_dict.items()
])

df['number of passed tests'].value_counts().sort_index()
# %%
