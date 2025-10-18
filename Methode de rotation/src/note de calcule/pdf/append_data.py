import json

with open('/home/ubuntu/combined_structural_data.json', 'r') as f:
    data = json.load(f)

line_properties_json_str = json.dumps(data['line_properties_json'], indent=4)

with open('/home/ubuntu/structural_calculation_note.md', 'a') as f:
    f.write(line_properties_json_str)
    f.write('\n```\n\n')

moment_max_str = json.dumps(data['moment_max'], indent=4)
with open('/home/ubuntu/structural_calculation_note.md', 'a') as f:
    f.write('### Moment Maximum\n\n```json\n')
    f.write(moment_max_str)
    f.write('\n```\n\n')

solution_str = json.dumps(data['solution'], indent=4)
with open('/home/ubuntu/structural_calculation_note.md', 'a') as f:
    f.write('### Solution\n\n```json\n')
    f.write(solution_str)
    f.write('\n```\n\n')

verdicte_str = json.dumps(data['verdicte'], indent=4)
with open('/home/ubuntu/structural_calculation_note.md', 'a') as f:
    f.write('### Verdict\n\n```json\n')
    f.write(verdicte_str)
    f.write('\n```\n\n')

line_properties_excel_str = json.dumps(data['line_properties_excel'], indent=4)
with open('/home/ubuntu/structural_calculation_note.md', 'a') as f:
    f.write('### Propriétés des lignes (extrait du fichier Excel)\n\n```json\n')
    f.write(line_properties_excel_str)
    f.write('\n```\n\n')


