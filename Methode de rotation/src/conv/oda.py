import os
import subprocess
from pathlib import Path
import json 

CHEMIN = "C:\\Users\\TSARALOHA Christinot\\Desktop\\Methode-de-rotation-cpp\\chemin.json"

def convert_dwg_to_dxf(input_file, output_file=None, path_ODA_exe = CHEMIN):
    """
    Convertit un fichier DWG en DXF en utilisant ODA File Converter.
    
    Args:
        input_file (str): Chemin du fichier DWG � convertir
        output_file (str, optional): Chemin du fichier DXF de sortie. Si non sp�cifi�,
                                   le fichier de sortie aura le m�me nom que l'entr�e
                                   mais avec l'extension .dxf
    
    Returns:
        bool: True si la conversion a r�ussi, False sinon
    """
    # V�rifier si le fichier d'entr�e existe
    if not os.path.exists(input_file):
        print(f"Erreur : Le fichier '{input_file}' n'existe pas.")
        return False
    
    # D�finir le chemin de sortie si non sp�cifi�
    if output_file is None:
        output_file = str(Path(input_file).with_suffix('.dxf'))
    
    # Chemin vers l'ex�cutable ODA File Converter
    # Note: Ajustez ce chemin selon votre installation
    oda_converter = path_ODA_exe
    
    if not os.path.exists(oda_converter):
        print("Erreur : ODA File Converter n'est pas install� ou le chemin est incorrect.")
        print("Veuillez installer ODA File Converter ou ajuster le chemin dans le script.")
        return False
    
    try:
        # Pr�parer les arguments pour la commande
        input_dir = os.path.dirname(input_file)
        output_dir = os.path.dirname(output_file)
        
        # Cr�er les r�pertoires de sortie s'ils n'existent pas
        os.makedirs(output_dir, exist_ok=True)
        
        # Construire la commande
        command = [
            oda_converter,
            input_dir,  # R�pertoire d'entr�e
            output_dir,  # R�pertoire de sortie
            "ACAD2018",  # Version de sortie
            "DXF",      # Format de sortie
            "0",        # Mode de r�cursion (0 = non r�cursif)
            "1"         # Mode de conversion (1 = convertir)
        ]
        # Ex�cuter la commande
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Conversion r�ussie : {input_file} -> {output_file}")
            return True
        else:
            print(f"Erreur lors de la conversion : {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Erreur inattendue : {str(e)}")
        return False


def convert_all(input_dir = "DWG", output_dir = "DXF", ODA_path = None):
    # Créer le dossier de sortie s'il n'existe pas
    print("output_dir : ", output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Parcourir tous les fichiers DWG dans le dossier source
    # Récupérer tous les fichiers .dwg
    dwg_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.dwg')]

    # Convertir chaque fichier
    for dwg_file in dwg_files:
        input_path = os.path.join(input_dir, dwg_file)
        output_path = os.path.join(output_dir, os.path.splitext(dwg_file)[0] + '.dxf')

        print(f"\nConversion de {dwg_file}...")
    success = convert_dwg_to_dxf(input_path, output_path, ODA_path)
    if not success:
        print(f"Échec de la conversion de {dwg_file}\n")
