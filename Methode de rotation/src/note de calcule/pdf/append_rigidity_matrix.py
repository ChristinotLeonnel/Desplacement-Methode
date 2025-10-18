import json
import pandas as pd

with open("/home/ubuntu/upload/MatriceDeRigidite.json", "r") as f:
    rigidity_matrix_data = json.load(f)

# Convert the dictionary of lists into a more readable format, e.g., a DataFrame for display
# For very large matrices, displaying the full matrix might not be feasible or readable.
# We'll display a summary or a representative part if it's too big.

# Let's check the size of the matrix
first_key = next(iter(rigidity_matrix_data))
num_rows = len(rigidity_matrix_data)
num_cols = len(rigidity_matrix_data[first_key])

markdown_content = "\n## Matrice de Rigidité\n\n"
markdown_content += "La matrice de rigidité représente la relation entre les forces appliquées et les déplacements résultants dans la structure. Elle est fondamentale pour comprendre la raideur globale du système.\n\n"

if num_rows > 10 or num_cols > 10: # If the matrix is large, display only a part or summary
    markdown_content += "Étant donné la taille de la matrice de rigidité ({} lignes x {} colonnes), une représentation complète n'est pas pratique pour ce document de synthèse. Voici un extrait des premières lignes pour illustration :\n\n".format(num_rows, num_cols)
    markdown_content += "```json\n"
    # Display first 5 rows
    count = 0
    for key, value in rigidity_matrix_data.items():
        if count < 5:
            markdown_content += f'    "{key}": {value},\n'
            count += 1
        else:
            break
    markdown_content += "    ...\n"
    markdown_content += "```\n\n"
    markdown_content += "Pour une analyse détaillée de la matrice complète, veuillez vous référer aux données brutes du fichier `MatriceDeRigidite.json`.\n\n"
else:
    markdown_content += "Voici la matrice de rigidité complète :\n\n"
    markdown_content += "```json\n"
    markdown_content += json.dumps(rigidity_matrix_data, indent=4)
    markdown_content += "```\n\n"

with open("/home/ubuntu/structural_calculation_note_business.md", "a") as f:
    f.write(markdown_content)


