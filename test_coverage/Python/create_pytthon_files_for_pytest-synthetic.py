#%%
from datasets import load_dataset
import re
import os
import json

ds_python = load_dataset("THUDM/humaneval-x", "python")
def extract_function_name_python(code):
    match = re.search(r'def\s+(\w+)\s*\(', code)
    return match.group(1) if match else None

def remove_trailing_quote_line(s):
    lines = s.rstrip().split('\n')
    if lines and lines[-1].strip() == '"':
        lines = lines[:-1]
    return '\n'.join(lines)

def remove_metadata_block(code_str):
    return re.sub(r"(?s)METADATA\s*=\s*\{.*?\}\s*", "", code_str)

def extract_all_function_names_python(code):
    return re.findall(r'\ndef\s+(\w+)\s*\(', code)

def extract_check_body(code_str):
    lines = code_str.strip().split('\n')
    inside = False
    extracted_lines = []
    for line in lines:
        if line.strip().startswith("def check"):
            inside = True
            continue
        if inside:
            if line.strip() == "":
                continue
            if line.startswith(" ") or line.startswith("\t"):
                extracted_lines.append(line)
            else:
                break 
    return "\n".join(extracted_lines)

os.makedirs("./dataset_synthetic/tests/", exist_ok=True)
os.makedirs("./dataset_synthetic/", exist_ok=True)
with open('./passed_asserts-GEMINI2.json', "r") as f:
    tests_data = json.load(f)
function_names_saved = {}
for data in ds_python['test']:
    function_code = remove_trailing_quote_line(data['declaration']) + '\n' + data['canonical_solution']
    python_func_name = extract_function_name_python(data['declaration'])
    if python_func_name in function_names_saved:
        function_names_saved[python_func_name] += 1
        python_func_name = python_func_name + '_' + str(function_names_saved[python_func_name])
    else:
        function_names_saved[python_func_name] = 1
    python_func_names = extract_all_function_names_python('\n' + function_code)
    import_statements = '\n'.join([f'from {python_func_name} import {name}' for name in python_func_names])
    intended_test_code = ('\n    '.join(tests_data[data['task_id']].split('\n')))
    if not intended_test_code:
        intended_test_code = 'return'
    import_lines = '\n'.join([
        line.strip() for line in function_code.splitlines()
        if line.strip().startswith("import") or line.strip().startswith("from")
    ])
    test_code = f"""
{import_statements}
{import_lines}

def test_{python_func_name}():
    {intended_test_code}
"""
    with open(f"./dataset_synthetic/{python_func_name}.py", "w") as f:
        f.write(function_code)
    with open(f"./dataset_synthetic/tests/test_{python_func_name}.py", "w") as f:
        f.write(test_code)

# %%