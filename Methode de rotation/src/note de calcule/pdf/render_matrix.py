import json

with open("/home/ubuntu/upload/MatriceDeRigidite.json", "r") as f:
    rigidity_matrix_data = json.load(f)

# Get the first few rows and columns to represent the matrix
matrix_representation = "$$\\begin{pmatrix}\n"

keys = list(rigidity_matrix_data.keys())

# Determine the maximum number of columns to display for readability
max_cols_to_display = 5 # Display first 5 columns

for i, key in enumerate(keys):
    if i >= 5: # Display first 5 rows
        matrix_representation += "\\vdots & \\ddots & \\vdots \\\\ \n"
        break
    row = rigidity_matrix_data[key]
    row_str = " & ".join([f"{val:.2f}" for val in row[:max_cols_to_display]])
    if len(row) > max_cols_to_display:
        row_str += " & \\dots"
    matrix_representation += f"    {row_str} \\\\ \n"

if len(keys) > 5:
    matrix_representation += "\\end{pmatrix}$$"
else:
    matrix_representation = matrix_representation.rstrip(" \\\\ \n") + "\\end{pmatrix}$$"

with open("/home/ubuntu/matrix_math_representation.txt", "w") as f:
    f.write(matrix_representation)


