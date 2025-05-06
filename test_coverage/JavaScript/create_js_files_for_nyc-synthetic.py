#%%
import os
import json
import re
from datasets import load_dataset

ds_js = load_dataset("THUDM/humaneval-x", "js")

os.makedirs("dataset_synthetic", exist_ok=True)
os.makedirs("dataset_synthetic/src", exist_ok=True)
os.makedirs("dataset_synthetic/tests", exist_ok=True)

with open('./passed_asserts_js.json', "r") as f:
    passed_asserts = json.load(f)
    
folder_path = './dataset/tests'

def extract_function_name_js(code):
    match = re.search(r'const\s+(\w+)\s*=\s*\(', code)
    return match.group(1) if match else None

function_names_saved = {}
for data in ds_js['test']:
    js_func_name = extract_function_name_js(data['declaration'])
    if js_func_name in function_names_saved:
        function_names_saved[js_func_name] += 1
        js_func_name_file = js_func_name + '_' + str(function_names_saved[js_func_name] - 1)
    else:
        function_names_saved[js_func_name] = 1
        js_func_name_file = js_func_name
    filename = f'{js_func_name_file}.test.js'
    file_path = os.path.join(folder_path, filename)
    output_file_path = os.path.join('./dataset_synthetic/tests', filename)

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    cleaned_lines = [line for line in lines if 'console.assert' not in line]

    syntests = passed_asserts[data['task_id']]
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.writelines('\n'.join(cleaned_lines[:3]) + '\n' + syntests + '\n' + '\n'.join(cleaned_lines[-3:]))


#%%
import shutil
src_folder = './dataset/src'
dst_folder = './dataset_synthetic/src'

for filename in os.listdir(src_folder):
    src_file = os.path.join(src_folder, filename)
    dst_file = os.path.join(dst_folder, filename)
    if os.path.isfile(src_file): 
        shutil.copy2(src_file, dst_file) 

# %%
