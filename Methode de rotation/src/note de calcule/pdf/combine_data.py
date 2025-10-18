import json
import pandas as pd

with open('/home/ubuntu/upload/line_properties.json', 'r') as f: 
    line_properties_json = json.load(f)
with open('/home/ubuntu/upload/MomentMax.json', 'r') as f: 
    moment_max = json.load(f)
with open('/home/ubuntu/upload/solution.json', 'r') as f: 
    solution = json.load(f)
with open('/home/ubuntu/upload/verdicte.json', 'r') as f: 
    verdicte = json.load(f)

line_properties_excel_df = pd.read_excel('/home/ubuntu/upload/line_properties.xlsx')
line_properties_excel = line_properties_excel_df.to_dict(orient='records')

combined_data = {
    'line_properties_json': line_properties_json,
    'moment_max': moment_max,
    'solution': solution,
    'verdicte': verdicte,
    'line_properties_excel': line_properties_excel
}

with open('combined_structural_data.json', 'w') as f: 
    json.dump(combined_data, f, indent=4)


