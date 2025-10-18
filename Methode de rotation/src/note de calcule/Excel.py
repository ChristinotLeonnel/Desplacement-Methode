import json
import pandas as pd
import os
from pathlib import Path
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference, Series
from openpyxl.chart.axis import DateAxis
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def apply_excel_formatting(worksheet, df, sheet_name):
    """
    Applique un formatage professionnel à une feuille Excel
    
    Args:
        worksheet: Feuille de calcul openpyxl
        df: DataFrame pandas
        sheet_name: Nom de la feuille
    """
    # Définir les styles
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    data_font = Font(size=10)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Couleurs pour différents types d'éléments
    beam_fill = PatternFill(start_color="E7F3FF", end_color="E7F3FF", fill_type="solid")
    column_fill = PatternFill(start_color="FFF2E7", end_color="FFF2E7", fill_type="solid")
    consol_fill = PatternFill(start_color="F0F8E7", end_color="F0F8E7", fill_type="solid")
    
    # Couleurs spéciales pour la matrice de rigidité
    node_fill = PatternFill(start_color="E8F4FD", end_color="E8F4FD", fill_type="solid")
    element_fill = PatternFill(start_color="FFF8DC", end_color="FFF8DC", fill_type="solid")
    diagonal_fill = PatternFill(start_color="FFE4E1", end_color="FFE4E1", fill_type="solid")  # Rouge clair pour la diagonale
    
    # Appliquer le formatage à l'en-tête
    for col_num, column_title in enumerate(df.columns, 1):
        cell = worksheet.cell(row=1, column=col_num)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = border
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Appliquer le formatage aux données
    for row_num in range(2, len(df) + 2):
        for col_num in range(1, len(df.columns) + 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.font = data_font
            cell.border = border
            cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Appliquer des couleurs selon le type d'élément
            if sheet_name == 'Poutres' and 'is_beam' in df.columns:
                cell.fill = beam_fill
            elif sheet_name == 'Colonnes' and 'is_column' in df.columns:
                cell.fill = column_fill
            elif sheet_name == 'Consoles' and 'is_consol' in df.columns:
                cell.fill = consol_fill
            elif sheet_name in ['Nœuds_Rigidité', 'Matrice_Rigidité_Complète']:
                # Colorer différemment selon le type dans la matrice combinée
                if sheet_name == 'Matrice_Rigidité_Complète' and 'Type' in df.columns:
                    if df.iloc[row_num-2]['Type'] == 'Nœud':
                        cell.fill = node_fill
                    elif df.iloc[row_num-2]['Type'] == 'Élément':
                        cell.fill = element_fill
                else:
                    cell.fill = node_fill
                
                # Colorer la diagonale (ligne = colonne)
                if col_num > 1:  # Ignorer la première colonne (ID/Type)
                    # Trouver l'index de la colonne dans les noms de nœuds
                    column_name = df.columns[col_num-1]
                    row_id = df.iloc[row_num-2]['ID'] if 'ID' in df.columns else df.iloc[row_num-2]['Nœud']
                    
                    # Si c'est la diagonale (même nœud en ligne et colonne)
                    if column_name == row_id:
                        cell.fill = diagonal_fill
                        
            elif sheet_name == 'Éléments_Rigidité':
                cell.fill = element_fill
                
                # Colorer la diagonale pour les éléments aussi
                if col_num > 1:  # Ignorer la première colonne (Élément)
                    column_name = df.columns[col_num-1]
                    row_id = df.iloc[row_num-2]['Élément']
                    
                    # Si c'est la diagonale (même élément en ligne et colonne)
                    if column_name == row_id:
                        cell.fill = diagonal_fill
    
    # Ajuster la largeur des colonnes
    for column in worksheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        
        # Ajuster la largeur selon le type de feuille
        if 'Rigidité' in sheet_name:
            adjusted_width = min(max_length + 2, 15)  # Plus étroit pour les coefficients
        else:
            adjusted_width = min(max_length + 2, 20)
        
        worksheet.column_dimensions[column_letter].width = adjusted_width

def print_progress_info(step, total_steps, message):
    """
    Affiche les informations de progression de manière formatée
    
    Args:
        step: Étape actuelle
        total_steps: Nombre total d'étapes
        message: Message à afficher
    """
    progress = (step / total_steps) * 100
    print(f"[{step}/{total_steps}] ({progress:.1f}%) {message}")

def print_section_header(title):
    """
    Affiche un en-tête de section formaté
    
    Args:
        title: Titre de la section
    """
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_data_summary(df, element_type=""):
    """
    Affiche un résumé des données de manière formatée
    
    Args:
        df: DataFrame à analyser
        element_type: Type d'élément (Poutres, Colonnes, etc.)
    """
    if df.empty:
        print(f"  Aucun élément de type '{element_type}' trouvé.")
        return
    
    print(f"\n  📊 Résumé pour {element_type}:")
    print(f"     • Nombre d'éléments: {len(df)}")
    
    # Statistiques sur les moments
    if 'M_i' in df.columns and 'M_j' in df.columns:
        max_moment = max(df['M_i'].abs().max(), df['M_j'].abs().max())
        print(f"     • Moment maximum: {max_moment:.2f} kN.m")
    
    if 'M_en_travee_max' in df.columns:
        max_travee = df['M_en_travee_max'].abs().max()
        print(f"     • Moment en travée max: {max_travee:.2f} kN.m")
    
    # Statistiques sur les efforts tranchants
    if 'ET_i' in df.columns and 'ET_j' in df.columns:
        max_effort = max(df['ET_i'].abs().max(), df['ET_j'].abs().max())
        print(f"     • Effort tranchant max: {max_effort:.2f} kN")

def process_stiffness_matrix(json_file_path):
    """
    Traite la matrice de rigidité depuis un fichier JSON
    
    Args:
        json_file_path (str): Chemin vers le fichier MatriceDeRigidite.json
    
    Returns:
        dict: Dictionnaire contenant les données de la matrice de rigidité
    """
    try:
        print_progress_info(1, 4, "Lecture de la matrice de rigidité...")
        
        with open(json_file_path, 'r', encoding='utf-8') as file:
            stiffness_data = json.load(file)
        
        print(f"  ✅ Matrice de rigidité lue avec succès")
        print(f"  📊 Nombre de nœuds/éléments: {len(stiffness_data)}")
        
        print_progress_info(2, 4, "Séparation des nœuds et éléments...")
        
        # Séparer les nœuds (nd_) et les éléments (H_)
        nodes_data = {}
        elements_data = {}
        
        for key, value in stiffness_data.items():
            if key.startswith('nd_'):
                nodes_data[key] = value
            elif key.startswith('H_'):
                elements_data[key] = value
        
        print(f"  📍 Nœuds trouvés: {len(nodes_data)}")
        print(f"  🔗 Éléments trouvés: {len(elements_data)}")
        
        print_progress_info(3, 4, "Traitement des données de rigidité...")
        
        # Obtenir tous les noms de nœuds et éléments pour créer les colonnes
        all_nodes = sorted(nodes_data.keys(), key=lambda x: int(x.split('_')[1]) if '_' in x else 0)
        all_elements = sorted(elements_data.keys(), key=lambda x: int(x.split('_')[1]) if '_' in x else 0)
        
        # Créer un DataFrame pour les nœuds
        nodes_rows = []
        for node_id in all_nodes:
            stiffness_vector = nodes_data[node_id]
            row = {'Nœud': node_id}
            # Colonnes: d'abord tous les nd_, puis tous les H_
            for i, nd_name in enumerate(all_nodes):
                row[nd_name] = stiffness_vector[i] if i < len(stiffness_vector) else None
            for j, h_name in enumerate(all_elements):
                idx = len(all_nodes) + j
                row[h_name] = stiffness_vector[idx] if idx < len(stiffness_vector) else None
            nodes_rows.append(row)
        
        nodes_df = pd.DataFrame(nodes_rows)

        # Créer un DataFrame pour les éléments
        elements_rows = []
        for element_id in all_elements:
            stiffness_vector = elements_data[element_id]
            row = {'Élément': element_id}
            # Colonnes: d'abord tous les nd_, puis tous les H_
            for i, nd_name in enumerate(all_nodes):
                row[nd_name] = stiffness_vector[i] if i < len(stiffness_vector) else None
            for j, h_name in enumerate(all_elements):
                idx = len(all_nodes) + j
                row[h_name] = stiffness_vector[idx] if idx < len(stiffness_vector) else None
            elements_rows.append(row)
        
        elements_df = pd.DataFrame(elements_rows)

        # Créer un DataFrame combiné avec type d'identification
        combined_rows = []
        for node_id in all_nodes:
            stiffness_vector = nodes_data[node_id]
            row = {'ID': node_id, 'Type': 'Nœud'}
            for i, nd_name in enumerate(all_nodes):
                row[nd_name] = stiffness_vector[i] if i < len(stiffness_vector) else None
            for j, h_name in enumerate(all_elements):
                idx = len(all_nodes) + j
                row[h_name] = stiffness_vector[idx] if idx < len(stiffness_vector) else None
            combined_rows.append(row)
        
        for element_id in all_elements:
            stiffness_vector = elements_data[element_id]
            row = {'ID': element_id, 'Type': 'Élément'}
            for i, nd_name in enumerate(all_nodes):
                row[nd_name] = stiffness_vector[i] if i < len(stiffness_vector) else None
            for j, h_name in enumerate(all_elements):
                idx = len(all_nodes) + j
                row[h_name] = stiffness_vector[idx] if idx < len(stiffness_vector) else None
            combined_rows.append(row)
        
        combined_df = pd.DataFrame(combined_rows)
        
        print(f"  ✅ Données de rigidité traitées: {len(combined_df)} lignes")
        
        print_progress_info(4, 4, "Création du résumé de rigidité...")
        
        # Créer un résumé statistique séparé pour nœuds et éléments
        summary_rows = []
        
        # Statistiques pour les nœuds
        if nodes_data:
            for i, node_name in enumerate(all_nodes):
                coeff_values = [nodes_data[node][i] for node in all_nodes if i < len(nodes_data[node])]
                if coeff_values:
                    summary_rows.append({
                        'Type': 'Nœud',
                        'Coefficient': node_name,
                        'Min': min(coeff_values),
                        'Max': max(coeff_values),
                        'Moyenne': np.mean(coeff_values),
                        'Écart_type': np.std(coeff_values),
                        'Valeurs_non_nulles': sum(1 for v in coeff_values if v != 0),
                        'Total_éléments': len(coeff_values)
                    })
        
        # Statistiques pour les éléments
        if elements_data:
            for i, node_name in enumerate(all_nodes):
                coeff_values = [elements_data[element][i] for element in all_elements if i < len(elements_data[element])]
                if coeff_values:
                    summary_rows.append({
                        'Type': 'Élément',
                        'Coefficient': node_name,
                        'Min': min(coeff_values),
                        'Max': max(coeff_values),
                        'Moyenne': np.mean(coeff_values),
                        'Écart_type': np.std(coeff_values),
                        'Valeurs_non_nulles': sum(1 for v in coeff_values if v != 0),
                        'Total_éléments': len(coeff_values)
                    })
        
        summary_df = pd.DataFrame(summary_rows)
        
        print(f"  ✅ Résumé de rigidité créé")
        
        return {
            'nodes_df': nodes_df,
            'elements_df': elements_df,
            'combined_df': combined_df,
            'summary_df': summary_df,
            'raw_data': stiffness_data
        }
        
    except FileNotFoundError:
        print(f"  ❌ Fichier de matrice de rigidité non trouvé: {json_file_path}")
        return None
    except Exception as e:
        print(f"  ❌ Erreur lors du traitement de la matrice de rigidité: {e}")
        return None

def json_to_excel(json_file_path, excel_output_path, stiffness_matrix_path=None, moment_max_path=None, x_mf_path=None, mf_path=None):
    """
    Convertit un fichier JSON de propriétés de lignes en fichier Excel
    
    Args:
        json_file_path (str): Chemin vers le fichier JSON
        excel_output_path (str): Chemin de sortie pour le fichier Excel
        stiffness_matrix_path (str): Chemin vers le fichier MatriceDeRigidite.json (optionnel)
    """
    
    try:
        print_section_header("CONVERSION JSON VERS EXCEL")
        print_progress_info(1, 7, "Lecture du fichier JSON...")
        
        # Lire le fichier JSON
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        print(f"  ✅ Fichier JSON lu avec succès")
        print(f"  📁 Nombre d'éléments à traiter: {len(data)}")
        
        # Traiter la matrice de rigidité si fournie
        stiffness_data = None
        if stiffness_matrix_path and os.path.exists(stiffness_matrix_path):
            print_progress_info(2, 7, "Traitement de la matrice de rigidité...")
            stiffness_data = process_stiffness_matrix(stiffness_matrix_path)
        else:
            print_progress_info(2, 7, "Matrice de rigidité non fournie ou introuvable...")

        # Charger MomentMax.json si fourni
        moment_max_data = None
        moment_max_df = None
        if moment_max_path and os.path.exists(moment_max_path):
            try:
                with open(moment_max_path, 'r', encoding='utf-8') as fmm:
                    moment_max_data = json.load(fmm)
                # Créer un DataFrame à une ligne pour export
                moment_max_df = pd.DataFrame([moment_max_data])
                print("  📋 Fichier 'MomentMax.json' chargé")
            except Exception as e:
                print(f"  ❌ Erreur lors de la lecture de MomentMax.json: {e}")

        # Charger X_MF.json et MomentFlechissant.json si fournis
        x_mf_data = None
        mf_data = None
        if x_mf_path and os.path.exists(x_mf_path):
            try:
                with open(x_mf_path, 'r', encoding='utf-8') as fx:
                    x_mf_data = json.load(fx)
                print("  📋 Fichier 'X_MF.json' chargé")
            except Exception as e:
                print(f"  ❌ Erreur lors de la lecture de X_MF.json: {e}")
        if mf_path and os.path.exists(mf_path):
            try:
                with open(mf_path, 'r', encoding='utf-8') as fm:
                    mf_data = json.load(fm)
                print("  📋 Fichier 'MomentFlechissant.json' chargé")
            except Exception as e:
                print(f"  ❌ Erreur lors de la lecture de MomentFlechissant.json: {e}")
        
        # Préparer les données de courbe pour la ligne max si disponibles
        ligne_max_curve_df = None
        if moment_max_data is not None and isinstance(moment_max_data, dict):
            try:
                ligne_max_id = moment_max_data.get('ligne_max')
                if ligne_max_id:
                    # Priorité: utiliser X_MF + MomentFlechissant si disponibles
                    if x_mf_data and mf_data and ligne_max_id in x_mf_data and ligne_max_id in mf_data:
                        x_vals = x_mf_data.get(ligne_max_id, [])
                        mf_vals = mf_data.get(ligne_max_id, [])
                        # Assurer tailles cohérentes
                        n = min(len(x_vals), len(mf_vals))
                        if n > 0:
                            ligne_max_curve_df = pd.DataFrame({
                                'Ligne': [ligne_max_id]*n,
                                'X': x_vals[:n],
                                'MF': mf_vals[:n]
                            })
                    # Sinon: fallback sur extraction M_* depuis line_properties
                    if ligne_max_curve_df is None and ligne_max_id in data:
                        max_line_payload = data[ligne_max_id]
                        series_points = []
                        for k, v in max_line_payload.items():
                            if isinstance(k, str) and k.startswith('M_') and k != 'M_en_travee_max':
                                try:
                                    idx = int(k.split('_')[1])
                                    if isinstance(v, (int, float)):
                                        series_points.append((idx, float(v)))
                                except Exception:
                                    continue
                        series_points.sort(key=lambda t: t[0])
                        if series_points:
                            ligne_max_curve_df = pd.DataFrame(series_points, columns=['Indice', 'Moment'])
                            ligne_max_curve_df.insert(0, 'Ligne', ligne_max_id)
            except Exception as e:
                print(f"  ❌ Erreur lors de la préparation de la courbe de la ligne max: {e}")
        
        print_progress_info(3, 7, "Traitement des données...")
        
        # Créer une liste pour stocker toutes les données
        rows = []
        
        # Parcourir chaque ligne et extraire ses propriétés
        for line_id, line_data in data.items():
            # Créer une ligne avec l'ID de la ligne et toutes ses propriétés
            row = {'ID_Ligne': line_id}
            
            # Copier toutes les propriétés sauf les moments individuels
            for key, value in line_data.items():
                if not key.startswith('M_'):
                    row[key] = value
            R = row.copy()
            for key, value in R.items():
                if key.startswith('m_'):
                    row.pop(key)

            # Extraire seulement M_i et M_j (moments aux extrémités)
            node_i = int(line_data.get('noeud_i', 0))
            node_j = int(line_data.get('noeud_j', 0))
            
            # Chercher les moments correspondants aux nœuds i et j
            M_i_key = f'M_{int(node_i)}'
            M_j_key = f'M_{int(node_j)}'

            m_i_key = f'm_{int(node_i)}'
            m_j_key = f'm_{int(node_j)}'
            
            # Ajouter M_i et M_j
            row['M_i'] = line_data.get(M_i_key, 0.0)
            row['M_j'] = line_data.get(M_j_key, 0.0)

            row['m_i'] = line_data.get(m_i_key, 0.0)
            row['m_j'] = line_data.get(m_j_key, 0.0)

            row["M_en_travee_max"] = line_data.get("M_en_travee_max", 0.0)
            
            rows.append(row)
        
        print(f"  ✅ Données traitées: {len(rows)} lignes créées")
        
        print_progress_info(4, 7, "Création du DataFrame...")
        
        # Créer un DataFrame pandas
        df = pd.DataFrame(rows)
        
        # Réorganiser les colonnes pour une meilleure lisibilité
        # Mettre les colonnes d'identification en premier, puis les moments
        id_columns = ['ID_Ligne','noeud_i', 'noeud_j']
        moment_columns = ['M_i', 'M_j', "m_i", 'm_j']
        other_columns = [col for col in df.columns if col not in id_columns and col not in moment_columns]
        df = df[id_columns + moment_columns + other_columns]
        
        print(f"  ✅ DataFrame créé avec {len(df.columns)} colonnes")
        
        print_progress_info(5, 7, "Création des onglets Excel...")
        
        # Créer un writer Excel avec plusieurs onglets
        with pd.ExcelWriter(excel_output_path, engine='openpyxl') as writer:
            # Onglet principal avec toutes les données
            df.to_excel(writer, sheet_name='Toutes_Lignes', index=False)
            print("  📋 Onglet 'Toutes_Lignes' créé")
            
            # Onglet avec seulement les poutres
            beam_df = df[df['is_beam'] == 1.0]
            if not beam_df.empty:
                beam_df.to_excel(writer, sheet_name='Poutres', index=False)
                print("  📋 Onglet 'Poutres' créé")
            
            # Onglet avec seulement les colonnes
            column_df = df[df['is_column'] == 1.0]
            if not column_df.empty:
                column_df.to_excel(writer, sheet_name='Colonnes', index=False)
                print("  📋 Onglet 'Colonnes' créé")
            
            # Onglet avec seulement les consoles
            consol_df = df[df['is_consol'] == 1.0]
            if not consol_df.empty:
                consol_df.to_excel(writer, sheet_name='Consoles', index=False)
                print("  📋 Onglet 'Consoles' créé")
            
            # Onglet de résumé statistique
            summary_data = []
            for col in df.select_dtypes(include=['number']).columns:
                if col != 'i' and col != 'j' and col != 'node_i' and col != 'node_j':
                    summary_data.append({
                        'Propriété': col,
                        'Min': df[col].abs().min(),
                        'Max': df[col].abs().max(),
                        'Moyenne': df[col].mean(),
                        'Écart_type': df[col].std()
                    })
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Résumé_Statistique', index=False)
            print("  📋 Onglet 'Résumé_Statistique' créé")
            
            # Ajouter les onglets de matrice de rigidité si disponibles
            if stiffness_data:
                # Onglet avec tous les nœuds et éléments combinés
                stiffness_data['combined_df'].to_excel(writer, sheet_name='Matrice_Rigidité_Complète', index=False)
                print("  📋 Onglet 'Matrice_Rigidité_Complète' créé")
                
                # Onglet avec seulement les nœuds
                if not stiffness_data['nodes_df'].empty:
                    stiffness_data['nodes_df'].to_excel(writer, sheet_name='Nœuds_Rigidité', index=False)
                    print("  📋 Onglet 'Nœuds_Rigidité' créé")
                
                # Onglet avec seulement les éléments
                if not stiffness_data['elements_df'].empty:
                    stiffness_data['elements_df'].to_excel(writer, sheet_name='Éléments_Rigidité', index=False)
                    print("  📋 Onglet 'Éléments_Rigidité' créé")
                
                # Onglet avec le résumé de la matrice de rigidité
                stiffness_data['summary_df'].to_excel(writer, sheet_name='Résumé_Rigidité', index=False)
                print("  📋 Onglet 'Résumé_Rigidité' créé")

            # Ajouter l'onglet des moments maximums si disponible
            if moment_max_df is not None:
                moment_max_df.to_excel(writer, sheet_name='MomentMax', index=False)
                print("  📋 Onglet 'MomentMax' créé")
            
            # Ajouter l'onglet de courbe pour la ligne max et insérer un graphique
            if ligne_max_curve_df is not None and not ligne_max_curve_df.empty:
                sheet_name_curve = 'Courbe_Ligne_Max'
                ligne_max_curve_df.to_excel(writer, sheet_name=sheet_name_curve, index=False)
                print(f"  📋 Onglet '{sheet_name_curve}' créé")
                try:
                    ws_curve = writer.book[sheet_name_curve]
                    chart = LineChart()
                    chart.title = f"Courbe des moments - {ligne_max_curve_df.iloc[0]['Ligne']}"
                    chart.style = 2
                    chart.y_axis.title = "Moment (kN.m)"
                    # Utiliser X si présent, sinon Indice
                    if 'X' in ligne_max_curve_df.columns and 'MF' in ligne_max_curve_df.columns:
                        chart.x_axis.title = "X"
                        max_row = len(ligne_max_curve_df) + 1
                        data_ref = Reference(ws_curve, min_col=3, min_row=1, max_col=3, max_row=max_row)  # MF
                        cats_ref = Reference(ws_curve, min_col=2, min_row=2, max_row=max_row)  # X
                    else:
                        chart.x_axis.title = "Indice"
                        max_row = len(ligne_max_curve_df) + 1
                        data_ref = Reference(ws_curve, min_col=3, min_row=1, max_col=3, max_row=max_row)  # Moment
                        cats_ref = Reference(ws_curve, min_col=2, min_row=2, max_row=max_row)  # Indice
                    series = Series(data_ref, title_from_data=True)
                    chart.append(series)
                    chart.set_categories(cats_ref)
                    ws_curve.add_chart(chart, "E2")
                    print("  📈 Graphique de la ligne max inséré")
                except Exception as e:
                    print(f"  ⚠️ Impossible d'insérer le graphique: {e}")
            
            # Créer un onglet de documentation
            doc_data = [
                {'Propriété': 'ID_Ligne', 'Description': 'Identifiant unique de la ligne/élément'},
                {'Propriété': 'noeud_i', 'Description': 'Numéro du nœud de départ'},
                {'Propriété': 'noeud_j', 'Description': 'Numéro du nœud d\'arrivée'},
                {'Propriété': 'M_i', 'Description': 'Moment fléchissant au nœud i (kN.m)'},
                {'Propriété': 'M_j', 'Description': 'Moment fléchissant au nœud j (kN.m)'},
                {'Propriété': 'm_i', 'Description': 'Moment transmis au nœud i (kN.m)'},
                {'Propriété': 'm_j', 'Description': 'Moment transmis au nœud j (kN.m)'},
                {'Propriété': 'M_en_travee_max', 'Description': 'Moment maximum en travée (kN.m)'},
                {'Propriété': 'ET_i', 'Description': 'Effort tranchant au nœud i (kN)'},
                {'Propriété': 'ET_j', 'Description': 'Effort tranchant au nœud j (kN)'},
                {'Propriété': 'L', 'Description': 'Longueur de l\'élément (m)'},
                {'Propriété': 'E', 'Description': 'Module d\'élasticité (MPa)'},
                {'Propriété': 'I', 'Description': 'Moment d\'inertie (m⁴)'},
                {'Propriété': 'K', 'Description': 'Rigidité de l\'élément'},
                {'Propriété': 'is_beam', 'Description': '1 si poutre, 0 sinon'},
                {'Propriété': 'is_column', 'Description': '1 si colonne, 0 sinon'},
                {'Propriété': 'is_consol', 'Description': '1 si console, 0 sinon'},
                {'Propriété': 'charge', 'Description': 'Charge appliquée (kN/m)'},
                {'Propriété': 'coo_X', 'Description': 'Coordonnée X du centre de l\'élément'},
                {'Propriété': 'coo_y', 'Description': 'Coordonnée Y du centre de l\'élément'}
            ]
            
            doc_df = pd.DataFrame(doc_data)
            doc_df.to_excel(writer, sheet_name='Documentation', index=False)
            print("  📋 Onglet 'Documentation' créé")
            
            print_progress_info(6, 7, "Application du formatage...")
            
            # Appliquer le formatage à chaque feuille
            workbook = writer.book
            
            # Formatage pour toutes les feuilles
            for sheet_name in workbook.sheetnames:
                worksheet = workbook[sheet_name]
                # Obtenir le DataFrame correspondant à cette feuille
                if sheet_name == 'Toutes_Lignes':
                    sheet_df = df
                elif sheet_name == 'Poutres':
                    sheet_df = beam_df
                elif sheet_name == 'Colonnes':
                    sheet_df = column_df
                elif sheet_name == 'Consoles':
                    sheet_df = consol_df
                elif sheet_name == 'Résumé_Statistique':
                    sheet_df = summary_df
                elif sheet_name == 'Matrice_Rigidité_Complète':
                    sheet_df = stiffness_data['combined_df'] if stiffness_data else df
                elif sheet_name == 'Nœuds_Rigidité':
                    sheet_df = stiffness_data['nodes_df'] if stiffness_data else df
                elif sheet_name == 'Éléments_Rigidité':
                    sheet_df = stiffness_data['elements_df'] if stiffness_data else df
                elif sheet_name == 'Résumé_Rigidité':
                    sheet_df = stiffness_data['summary_df'] if stiffness_data else df
                elif sheet_name == 'Documentation':
                    sheet_df = doc_df
                elif sheet_name == 'MomentMax' and moment_max_df is not None:
                    sheet_df = moment_max_df
                elif sheet_name == 'Courbe_Ligne_Max' and ligne_max_curve_df is not None:
                    sheet_df = ligne_max_curve_df
                else:
                    sheet_df = df
                
                apply_excel_formatting(worksheet, sheet_df, sheet_name)
                print(f"  🎨 Formatage appliqué à '{sheet_name}'")
        
        print_progress_info(7, 7, "Finalisation...")
        
        print_section_header("RÉSULTATS DE LA CONVERSION")
        print(f"  ✅ Fichier Excel créé avec succès: {excel_output_path}")
        print(f"  📊 Nombre total de lignes traitées: {len(df)}")
        
        # Afficher les résumés détaillés
        print_data_summary(df, "Tous les éléments")
        print_data_summary(beam_df, "Poutres")
        print_data_summary(column_df, "Colonnes")
        print_data_summary(consol_df, "Consoles")
        
        # Afficher le résumé de la matrice de rigidité si disponible
        if stiffness_data:
            print(f"\n  📊 Résumé de la matrice de rigidité:")
            print(f"     • Nombre total d'entités: {len(stiffness_data['combined_df'])}")
            print(f"     • Nombre de nœuds (nd_): {len(stiffness_data['nodes_df'])}")
            print(f"     • Nombre d'éléments (H_): {len(stiffness_data['elements_df'])}")
            print(f"     • Nombre de colonnes (nœuds): {len(stiffness_data['combined_df'].columns) - 2}")
            
            # Calculer les valeurs non nulles par type
            nodes_non_zero = sum(stiffness_data['summary_df'][stiffness_data['summary_df']['Type'] == 'Nœud']['Valeurs_non_nulles'])
            elements_non_zero = sum(stiffness_data['summary_df'][stiffness_data['summary_df']['Type'] == 'Élément']['Valeurs_non_nulles'])
            print(f"     • Valeurs non nulles (nœuds): {nodes_non_zero}")
            print(f"     • Valeurs non nulles (éléments): {elements_non_zero}")
            
            # Afficher l'ordre des colonnes
            column_names = [col for col in stiffness_data['combined_df'].columns if col not in ['ID', 'Type']]
            print(f"     • Colonnes (ordre croissant): {', '.join(column_names[:5])}{'...' if len(column_names) > 5 else ''}")
        
        # Afficher un résumé des moments maximums si disponible
        if moment_max_data:
            print(f"\n  📊 Moments extrêmes:")
            try:
                print(f"     • M_MAX: {moment_max_data.get('M_MAX', 'NA')}")
                print(f"     • M_MIN: {moment_max_data.get('M_MIN', 'NA')}")
                print(f"     • M_TRAVEE_MAX: {moment_max_data.get('M_TRAVEE_MAX', 'NA')}")
                print(f"     • M_TRAVEE_MIN: {moment_max_data.get('M_TRAVEE_MIN', 'NA')}")
                print(f"     • Ligne max: {moment_max_data.get('ligne_max', 'NA')} ({moment_max_data.get('key_max', 'NA')})")
                print(f"     • Ligne min: {moment_max_data.get('ligne_min', 'NA')} ({moment_max_data.get('key_min', 'NA')})")
                print(f"     • Ligne travée max: {moment_max_data.get('ligne_travee_max', 'NA')}")
                print(f"     • Ligne travée min: {moment_max_data.get('ligne_travee_min', 'NA')}")
            except Exception:
                pass
        
        print_section_header("CONVERSION TERMINÉE")
        print("  🎉 Le fichier Excel a été généré avec succès!")
        print(f"  📁 Emplacement: {excel_output_path}")
        
        return True
        
    except FileNotFoundError:
        print(f"Erreur: Fichier JSON non trouvé: {json_file_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"Erreur: Fichier JSON invalide: {e}")
        return False
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        return False

def main(Nom_dossier):
    """
    Fonction principale pour exécuter la conversion
    """
    print_section_header("CONVERTISSEUR JSON VERS EXCEL")
    print("  🔧 Méthode de Rotation - Analyse des Structures")
    print("  📊 Conversion des propriétés de lignes en format Excel")
    
    # Chemin vers le fichier JSON (relatif au répertoire de travail)
    json_file = f"{Nom_dossier}/line_properties.json"
    
    # Chemin vers la matrice de rigidité
    stiffness_matrix_file = f"{Nom_dossier}/MatriceDeRigidite.json"
    
    # Chemin de sortie pour le fichier Excel
    excel_output = f"{Nom_dossier}/line_properties.xlsx"
    # Chemin vers MomentMax.json
    moment_max_file = f"{Nom_dossier}/MomentMax.json"
    # Chemin vers X_MF.json et MomentFlechissant.json
    x_mf_file = f"{Nom_dossier}/X_MF.json"
    mf_file = f"{Nom_dossier}/MomentFlechissant.json"
    
    print(f"\n  📁 Fichier source: {json_file}")
    print(f"  📁 Matrice de rigidité: {stiffness_matrix_file}")
    print(f"  📁 Fichier de sortie: {excel_output}")
    if os.path.exists(moment_max_file):
        print(f"  📁 Moments extrêmes: {moment_max_file}")
    else:
        print(f"  ⚠️ Moments extrêmes non trouvés: {moment_max_file}")
    print(f"  📁 X_MF: {'OK' if os.path.exists(x_mf_file) else 'Manquant'} -> {x_mf_file}")
    print(f"  📁 MomentFlechissant: {'OK' if os.path.exists(mf_file) else 'Manquant'} -> {mf_file}")
    
    # Vérifier si le fichier JSON existe
    if not os.path.exists(json_file):
        print_section_header("ERREUR")
        print(f"  ❌ Fichier JSON non trouvé: {json_file}")
        print("  💡 Vérifiez le chemin du fichier.")
        return
    
    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(os.path.dirname(excel_output), exist_ok=True)
    print(f"  ✅ Répertoire de sortie vérifié")
    
    # Convertir le JSON en Excel avec la matrice de rigidité, MomentMax et X/MF
    success = json_to_excel(
        json_file,
        excel_output,
        stiffness_matrix_file,
        moment_max_file if os.path.exists(moment_max_file) else None,
        x_mf_file if os.path.exists(x_mf_file) else None,
        mf_file if os.path.exists(mf_file) else None
    )
    
    if not success:
        print_section_header("ÉCHEC DE LA CONVERSION")
        print("  ❌ La conversion a échoué.")
        print("  💡 Vérifiez les messages d'erreur ci-dessus.")

if __name__ == "__main__":
    with open("C:/Users/Tsaraloha Christinot/Desktop/Methode-de-rotation-cpp/chemin.json", "+r") as file: 
        ch = json.load(file)
    for i in range(ch["nombre_courbe"]):
        chemin = ch["output"] + "\\" + ch[f"folder_name_{i}"]
        main(chemin) 
