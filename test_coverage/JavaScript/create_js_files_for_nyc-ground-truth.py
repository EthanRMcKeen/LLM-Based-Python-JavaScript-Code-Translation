#%%
from datasets import load_dataset
import re
import os

ds_js = load_dataset("THUDM/humaneval-x", "js")

def extract_function_name_js(code):
    match = re.search(r'const\s+(\w+)\s*=\s*\(', code)
    return match.group(1) if match else None

os.makedirs("dataset", exist_ok=True)
os.makedirs("dataset/src", exist_ok=True)
os.makedirs("dataset/tests", exist_ok=True)

def get_all_function_names(function_code):
    function_names = re.findall(r'const\s+(\w+)\s*=\s*\(.*?\)\s*=>', function_code)
    return ', '.join(function_names)

function_names_saved = {}
for data in ds_js['test']:
    function_code = data['declaration'] + '\n' + data['canonical_solution']
    js_func_name = extract_function_name_js(data['declaration'])
    exports_str = f"\n\nmodule.exports = {{ {get_all_function_names(function_code)} }};\n"
    
    if js_func_name in function_names_saved:
        function_names_saved[js_func_name] += 1
        js_func_name_file = js_func_name + '_' + str(function_names_saved[js_func_name] - 1)
    else:
        function_names_saved[js_func_name] = 1
        js_func_name_file = js_func_name
            
    with open(f"dataset/src/{js_func_name_file}.js", "w", encoding="utf-8") as f:
        f.write(function_code + '\n' + exports_str)
        
    import_statement = f"const {{ {get_all_function_names(function_code)} }} = require('../src/{js_func_name_file}');\n"
    test_code = import_statement + '\n' +  data['test']
    test_function_name = extract_function_name_js(data['test'])
    if test_function_name not in data['test'].strip().split('\n')[-1]:
        test_code =  test_code + '\n' + test_function_name + '()'
    with open(f"dataset/tests/{js_func_name_file}.test.js", "w", encoding="utf-8") as f:
        f.write(test_code)


#%%
import os

test_dir = './dataset/tests' 
output_file = 'testRunner.js'

test_files = [
    f for f in os.listdir(test_dir)
    if f.endswith('.js')
]

lines = [f"require('./tests/{filename}');\n" for filename in test_files]

with open(output_file, 'w') as f:
    f.writelines(lines)
