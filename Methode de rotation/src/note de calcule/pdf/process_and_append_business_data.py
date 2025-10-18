import json
import pandas as pd

with open("/home/ubuntu/combined_structural_data.json", "r") as f:
    data = json.load(f)

# Process line_properties_json and line_properties_excel
line_properties_json = data["line_properties_json"]
line_properties_excel = data["line_properties_excel"]

# Convert line_properties_json to a list of dictionaries for easier processing
line_properties_json_list = []
for key, value in line_properties_json.items():
    value["ID_Ligne"] = key  # Add the line ID to the dictionary
    line_properties_json_list.append(value)

# Combine both line properties data into a single DataFrame for analysis
df_json = pd.DataFrame(line_properties_json_list)
df_excel = pd.DataFrame(line_properties_excel)

# Merge or concatenate if there's a common key, for now, let's just use the excel data as it's already a list of dicts
# For simplicity, let's assume line_properties_excel is the primary source for summarized properties
df_combined_properties = df_excel.copy()

# Calculate summary statistics for key properties
summary_stats = {
    "Longueur Moyenne (L)": df_combined_properties["L"].mean(),
    "Hauteur Moyenne (Hauteur)": df_combined_properties["Hauteur"].mean(),
    "Base Moyenne (Base)": df_combined_properties["Base"].mean(),
    "Moment d'Inertie Moyen (I)": df_combined_properties["I"].mean(),
    "Charge Moyenne (charge)": df_combined_properties["charge"].mean(),
    "Nombre de Poutres": df_combined_properties[df_combined_properties["is_beam"] == 1].shape[0],
    "Nombre de Poteaux": df_combined_properties[df_combined_properties["is_column"] == 1].shape[0],
}

# Identify critical elements (e.g., very small cross-sections, very large lengths)
critical_elements = df_combined_properties[
    (df_combined_properties["Base"] < df_combined_properties["Base"].mean() * 0.5) |
    (df_combined_properties["Hauteur"] < df_combined_properties["Hauteur"].mean() * 0.5) |
    (df_combined_properties["L"] > df_combined_properties["L"].mean() * 1.5)
].to_dict(orient="records")

# Process MomentMax.json
moment_max_data = data["moment_max"]
max_moment_value = moment_max_data["M_MAX"]
max_moment_key = moment_max_data["key_max"]
max_moment_line = moment_max_data["ligne_max"]

# Process solution.json and verdicte.json
solution_data = data["solution"]
verdicte_data = data["verdicte"]

# Convert solution and verdicte to DataFrames for easier analysis
df_solution = pd.DataFrame([solution_data])
df_verdicte = pd.DataFrame([verdicte_data])

# Identify nodes with significant displacements (from solution)
significant_displacements = {}
for key, value in solution_data.items():
    if abs(value) > 50:  # Example threshold for significant displacement
        significant_displacements[key] = value

# Identify nodes with non-zero verdicts (from verdicte) - indicating potential issues
non_zero_verdicts = {}
for key, value in verdicte_data.items():
    if abs(value) > 1e-9:  # Using a small epsilon for floating point comparison
        non_zero_verdicts[key] = value

# Append processed data to the Markdown file
with open("/home/ubuntu/structural_calculation_note_business.md", "a") as f:
    f.write("### Statistiques Générales des Propriétés des Lignes\n\n")
    f.write("| Propriété | Valeur Moyenne |\n")
    f.write("|---|---|\n")
    for key, value in summary_stats.items():
        f.write(f"| {key} | {value:.2f} |\n")
    f.write("\n")

    if critical_elements:
        f.write("### Éléments Structurels Critiques Potentiels\n\n")
        f.write("Certains éléments présentent des caractéristiques qui pourraient nécessiter une attention particulière :\n\n")
        f.write("| ID Ligne | Longueur (L) | Base | Hauteur | Charge | Est Poutre | Est Poteau |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for elem in critical_elements:
            f.write(f"| {elem.get('ID_Ligne', 'N/A')} | {elem.get('L', 0):.2f} | {elem.get('Base', 0):.2f} | {elem.get('Hauteur', 0):.2f} | {elem.get('charge', 0):.2f} | {'Oui' if elem.get('is_beam') == 1 else 'Non'} | {'Oui' if elem.get('is_column') == 1 else 'Non'} |\n")
        f.write("\n")
    else:
        f.write("### Éléments Structurels Critiques Potentiels\n\n")
        f.write("Aucun élément n'a été identifié comme potentiellement critique sur la base des critères actuels.\n\n")

    f.write("## Analyse des Moments et Déplacements\n\n")
    f.write("### Moment Maximal Identifié\n\n")
    f.write(f"Le moment maximal enregistré dans la structure est de **{max_moment_value:.2f}** et se produit sur l'élément **{max_moment_line}** (clé : **{max_moment_key}**). Un moment élevé à cet endroit indique une zone de forte contrainte qui mérite une vérification approfondie.\n\n")

    if significant_displacements:
        f.write("### Déplacements Nœudaux Significatifs\n\n")
        f.write("Les nœuds suivants présentent des déplacements significatifs, ce qui pourrait indiquer des déformations importantes ou des zones nécessitant un renforcement :\n\n")
        f.write("| Nœud | Déplacement |\n")
        f.write("|---|---|\n")
        for node, disp in significant_displacements.items():
            f.write(f"| {node} | {disp:.2f} |\n")
        f.write("\n")
    else:
        f.write("### Déplacements Nœudaux Significatifs\n\n")
        f.write("Aucun déplacement nodal significatif n'a été détecté au-delà du seuil défini.\n\n")

    if non_zero_verdicts:
        f.write("### Vérifications et Verdicts\n\n")
        f.write("Les nœuds suivants ont des 'verdicts' non nuls, ce qui peut signaler des points où les conditions de conception ou les limites de tolérance sont atteintes ou dépassées. Ces points nécessitent une analyse détaillée :\n\n")
        f.write("| Nœud | Verdict |\n")
        f.write("|---|---|\n")
        for node, verdict in non_zero_verdicts.items():
            f.write(f"| {node} | {verdict:.2e} |\n")
        f.write("\n")
    else:
        f.write("### Vérifications et Verdicts\n\n")
        f.write("Toutes les vérifications de 'verdict' sont dans les limites acceptables.\n\n")

    f.write("## Conclusion et Recommandations\n\n")
    f.write("Cette analyse préliminaire met en lumière les aspects clés de la performance structurelle. Les zones identifiées avec des moments maximaux élevés et des déplacements significatifs devraient faire l'objet d'une étude plus approfondie. Il est recommandé de consulter un ingénieur structure pour une interprétation détaillée de ces résultats et pour toute décision de conception ou de renforcement.\n\n")
    f.write("--- \n\n*Note : Ce document est une synthèse et ne remplace pas une note de calcul complète et détaillée réalisée par un professionnel qualifié.*\n")


