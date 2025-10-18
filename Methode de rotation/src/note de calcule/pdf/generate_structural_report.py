import json
import pandas as pd
import os

def generate_report(upload_dir="/home/ubuntu/upload", output_dir="/home/ubuntu"):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # --- 1. Load and Combine Data ---
    with open(os.path.join(upload_dir, 'line_properties.json'), 'r') as f:
        line_properties_json = json.load(f)
    with open(os.path.join(upload_dir, 'MomentMax.json'), 'r') as f:
        moment_max = json.load(f)
    with open(os.path.join(upload_dir, 'solution.json'), 'r') as f:
        solution = json.load(f)
    with open(os.path.join(upload_dir, 'verdicte.json'), 'r') as f:
        verdicte = json.load(f)

    line_properties_excel_df = pd.read_excel(os.path.join(upload_dir, 'line_properties.xlsx'))
    line_properties_excel = line_properties_excel_df.to_dict(orient='records')

    combined_data = {
        'line_properties_json': line_properties_json,
        'moment_max': moment_max,
        'solution': solution,
        'verdicte': verdicte,
        'line_properties_excel': line_properties_excel
    }

    # Save combined data (optional, for debugging/inspection)
    with open(os.path.join(output_dir, 'combined_structural_data.json'), 'w') as f:
        json.dump(combined_data, f, indent=4)

    # --- 2. Process Data for Business-Oriented Report ---
    line_properties_json = combined_data["line_properties_json"]
    line_properties_excel = combined_data["line_properties_excel"]

    line_properties_json_list = []
    for key, value in line_properties_json.items():
        value["ID_Ligne"] = key
        line_properties_json_list.append(value)

    df_json = pd.DataFrame(line_properties_json_list)
    df_excel = pd.DataFrame(line_properties_excel)

    df_combined_properties = df_excel.copy()

    summary_stats = {
        "Longueur Moyenne (L)": df_combined_properties["L"].mean(),
        "Hauteur Moyenne (Hauteur)": df_combined_properties["Hauteur"].mean(),
        "Base Moyenne (Base)": df_combined_properties["Base"].mean(),
        "Moment d'Inertie Moyen (I)": df_combined_properties["I"].mean(),
        "Charge Moyenne (charge)": df_combined_properties["charge"].mean(),
        "Nombre de Poutres": df_combined_properties[df_combined_properties["is_beam"] == 1].shape[0],
        "Nombre de Poteaux": df_combined_properties[df_combined_properties["is_column"] == 1].shape[0],
    }

    critical_elements = df_combined_properties[
        (df_combined_properties["Base"] < df_combined_properties["Base"].mean() * 0.5) |
        (df_combined_properties["Hauteur"] < df_combined_properties["Hauteur"].mean() * 0.5) |
        (df_combined_properties["L"] > df_combined_properties["L"].mean() * 1.5)
    ].to_dict(orient="records")

    moment_max_data = combined_data["moment_max"]
    max_moment_value = moment_max_data["M_MAX"]
    max_moment_key = moment_max_data["key_max"]
    max_moment_line = moment_max_data["ligne_max"]

    solution_data = combined_data["solution"]
    verdicte_data = combined_data["verdicte"]

    df_solution = pd.DataFrame([solution_data])
    df_verdicte = pd.DataFrame([verdicte_data])

    significant_displacements = {}
    for key, value in solution_data.items():
        if abs(value) > 50:
            significant_displacements[key] = value

    non_zero_verdicts = {}
    for key, value in verdicte_data.items():
        if abs(value) > 1e-9:
            non_zero_verdicts[key] = value

    # --- 3. Generate Markdown Report ---
    report_path = os.path.join(output_dir, "structural_calculation_note_business.md")
    with open(report_path, "w") as f:
        f.write("# Note de Calcul Structurel - Synthèse pour Décideurs\n\n")
        f.write("## Introduction\n\n")
        f.write("Ce document présente une synthèse des calculs structurels, destinée à fournir aux décideurs une vue d'ensemble claire et concise des performances de la structure. L'objectif est de mettre en évidence les points critiques et les résultats clés, sans s'attarder sur les détails techniques bruts.\n\n")
        f.write("## Résumé des Propriétés des Éléments Linéaires\n\n")
        f.write("Les éléments structurels (poutres et poteaux) ont été analysés en fonction de leurs propriétés géométriques et matérielles. Voici un aperçu des caractéristiques moyennes et des plages de valeurs pour les propriétés les plus pertinentes :\n\n")

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

        # --- 4. Add Rigidity Matrix (Mathematical Visualization) ---
        with open(os.path.join(upload_dir, "MatriceDeRigidite.json"), "r") as f_matrix:
            rigidity_matrix_data = json.load(f_matrix)

        matrix_math_representation_path = os.path.join(output_dir, "matrix_math_representation.md")
        rigidity_matrix_image_path = os.path.join(output_dir, "rigidity_matrix.png")

        # Generate LaTeX representation for image generation
        matrix_latex = "$$\\begin{pmatrix}\n"
        keys = list(rigidity_matrix_data.keys())
        max_cols_to_display = 5

        for i, key in enumerate(keys):
            if i >= 5:
                matrix_latex += "\\vdots & \\ddots & \\vdots \\\\ \n"
                break
            row = rigidity_matrix_data[key]
            row_str = " & ".join([f"{val:.2f}" for val in row[:max_cols_to_display]])
            if len(row) > max_cols_to_display:
                row_str += " & \\dots"
            matrix_latex += f"    {row_str} \\\\ \n"

        if len(keys) > 5:
            matrix_latex += "\\end{pmatrix}$$"
        else:
            matrix_latex = matrix_latex.rstrip(" \\\\ \n") + "\\end{pmatrix}$$"

        with open(matrix_math_representation_path, "w") as f_latex:
            f_latex.write(f"```latex\n{matrix_latex}\n```")

        # This part would typically be handled by an external tool like manus-render-diagram
        # For a standalone script, you'd need a LaTeX to image converter or similar.
        # Since manus-render-diagram is a tool, we'll simulate its output for the script.
        # In a real scenario, you'd call a system command here.
        # Example: subprocess.run(['manus-render-diagram', matrix_math_representation_path, rigidity_matrix_image_path])
        # For this script, we'll just note that the image generation is an external step.

        f.write("\n## Matrice de Rigidité (Visualisation Mathématique)\n\n")
        f.write("Voici une représentation visuelle de la matrice de rigidité, affichée sous forme mathématique pour une meilleure lisibilité. (L'image est générée séparément)\n\n")
        f.write(f"![Matrice de Rigidité]({rigidity_matrix_image_path})\n")

        f.write("## Conclusion et Recommandations\n\n")
        f.write("Cette analyse préliminaire met en lumière les aspects clés de la performance structurelle. Les zones identifiées avec des moments maximaux élevés et des déplacements significatifs devraient faire l'objet d'une étude plus approfondie. Il est recommandé de consulter un ingénieur structure pour une interprétation détaillée de ces résultats et pour toute décision de conception ou de renforcement.\n\n")
        f.write("--- \n\n*Note : Ce document est une synthèse et ne remplace pas une note de calcul complète et détaillée réalisée par un professionnel qualifié.*\n")

    print(f"Rapport Markdown généré: {report_path}")
    print(f"Pour générer le PDF, utilisez: manus-md-to-pdf {report_path} {os.path.join(output_dir, 'structural_calculation_note_business_final.pdf')}")
    print(f"Pour générer l'image de la matrice: manus-render-diagram {matrix_math_representation_path} {rigidity_matrix_image_path}")

if __name__ == "__main__":
    generate_report()


