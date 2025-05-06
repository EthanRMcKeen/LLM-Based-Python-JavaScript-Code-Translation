#%%
# Test on translated Python code
from datasets import load_dataset
import json
import os
import subprocess
import tempfile
import re

FOLDER_PATH = './gemini-2.0-flash/'

ds_python = load_dataset("THUDM/humaneval-x", "python")
with open(f'{FOLDER_PATH}baseline_js_to_python_code.json', "r") as f:
    translated_code = json.load(f)

def remove_metadata_block(code_str):
    return re.sub(r"(?s)METADATA\s*=\s*\{.*?\}\s*", "", code_str)

def remove_trailing_quote_line(s):
    lines = s.rstrip().split('\n')
    if lines and lines[-1].strip() == '"':
        lines = lines[:-1]
    return '\n'.join(lines)

result_dict = {}
for data in ds_python['test']:
    all_test = remove_metadata_block(data['test'])
    task_id = data['task_id'].split('/')[1]
    complete_test_code = translated_code[task_id] + '\n' + all_test

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
        tmp.write(complete_test_code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(["python", tmp_path], capture_output=True, text=True, timeout=5)
    except subprocess.TimeoutExpired:
        continue

    if result.returncode == 0:
        result_dict[task_id] = True
    else:
        result_dict[task_id] = False

os.remove(tmp_path)
with open(f'{FOLDER_PATH}RESULT-baseline_js_to_python_code.json', "w") as f:
    json.dump(result_dict, f, indent=2)

true_count = sum(value is True for value in result_dict.values())
false_count = sum(value is False for value in result_dict.values())

print(f"Translated Python Code - True: {true_count}, False: {false_count}")

# %%
