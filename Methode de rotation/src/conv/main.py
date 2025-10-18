from oda import * 
from lecture import * 
from typing import Dict, List, Tuple
import sys 
import json
import os 

#try:
    # chemin_path = os.getcwd() + "/chemin.json"
    # CHEMIN = chemin_path[-1]
    # with open(chemin_path, "+r") as f:
    #     a = json.load(f)
    # DWG_PATH = a["input"]  
    # DXF_PATH = a["output"]
    # print("\nLenceman de Argument\n")

#except:
CHEMIN = "C:\\Users\\TSARALOHA Christinot\\Desktop\\Methode-de-rotation-cpp\\chemin.json"
with open(CHEMIN, "+r") as f:
    a = json.load(f)
DWG_PATH = a["input"]  
DXF_PATH = a["output"]
print("\nLancement de chemin Par defaut \n") 



# Constants
PRECISION = 2  # Tolerance for coordinate comparison

class CADProcessor:
    """Class to handle CAD file processing and coordinate extraction."""
    
    def __init__(self, output_dir = "data/coordinates", DWG_path = DWG_PATH, DXF_path = DXF_PATH):
        """Initialize CAD processor with file paths and type."""

        self.dwg_path = DWG_path 
        self.dxf_path = DXF_path 
        self.output_dir = output_dir

        self.dwg_files = [f for f in os.listdir(self.dwg_path) if f.lower().endswith('.dwg')]
        self.file_names = [i.split(".")[0] for i in self.dwg_files]
        self.cad_path, self.file_type = self._get_cad_file()

    @staticmethod
    def is_duplicate_line(line1: List[float], line2: List[float], precision: int) -> bool:
        """
        Check if two lines are identical within specified precision.
        
        Args:
            line1: First line coordinates
            line2: Second line coordinates
            precision: Decimal precision for comparison
            
        Returns:
            bool: True if lines are duplicates, False otherwise
        """
        return all(round(line1[i], precision) == round(line2[i], precision) for i in range(6))

    def _get_cad_file(self) -> Tuple[str, str]:
        """
        Get the path and type of CAD file (.dwg or .dxf).
        
        Returns:
            Tuple[str, str]: Path to CAD file and file type
            
        Raises:
            FileNotFoundError: If no CAD files are found
        """

        if os.path.exists(self.dxf_path):
            return self.dxf_path, "dxf"
        elif os.path.exists(self.dwg_path): 
            return self.dwg_path, "dwg"
        else:
            raise FileNotFoundError("No .dwg or .dxf files found in DWG or DXF folders.")

    def _process_coordinates(self, coordinates: List[List[float]]) -> List[List[float]]:
        """
        Process coordinates to remove duplicates.
        
        Args:
            coordinates: List of line coordinates
            
        Returns:
            List[List[float]]: List of unique coordinates
        """
        unique_coordinates = []
        for coord in coordinates:
            if not any(self.is_duplicate_line(coord, unique_coord, PRECISION) 
                      for unique_coord in unique_coordinates):
                unique_coordinates.append(coord)
        return unique_coordinates

    def _create_coordinate_dict(self, unique_coordinates: List[List[float]], 
                              circles: List[List[float]], 
                              ellipse: List[List[float]], 
                              rectangle :  List[List[float]]) -> Dict:
        """
        Create dictionary with unique coordinates and circles.
        
        Args:
            unique_coordinates: List of unique line coordinates
            circles: List of circle coordinates
            
        Returns:
            Dict: Dictionary containing all coordinates
        """
        dico = {}
        
        # Add lines
        for a, coo in enumerate(unique_coordinates):
            dico[f"ln_{a}"] = {
                "nd_1": {
                    "x": round(coo[0], PRECISION),
                    "y": round(coo[1], PRECISION),
                    "z": round(coo[2], PRECISION)
                },
                "nd_2": {
                    "x": round(coo[3], PRECISION),
                    "y": round(coo[4], PRECISION),
                    "z": round(coo[5], PRECISION)
                }
            }

        # Add circles
        for i, circle_coord in enumerate(circles):
            dico[f"circle_{i}"] = {
                "center": {
                    "x": round(circle_coord[0], PRECISION),
                    "y": round(circle_coord[1], PRECISION),
                    "z": round(circle_coord[2], PRECISION)
                },
                "propriete":{ 
                     "radius" : round(circle_coord[3], PRECISION) 
                    }
            }
        
        # Add ellipse
        for i, ellipse_coord in enumerate(ellipse):
            dico[f"ellipse_{i}"] = { 
                "center": {
                    "x": round(ellipse_coord[0], PRECISION),
                    "y": round(ellipse_coord[1], PRECISION),
                    "z": round(ellipse_coord[2], PRECISION)
                },
                "propriete" : {
                    "major_radiusius": round(ellipse_coord[3], PRECISION),
                    "minor_radius_radiusius": round(ellipse_coord[4], PRECISION),
                    "angle": round(ellipse_coord[5], PRECISION)
                    }
                }

        for i, rectangle_coo in enumerate(rectangle):
            dico[f"rectangle_{i}"] = {
                    "nd_1" : {"x" : rectangle_coo[0][0], "y" : rectangle_coo[0][1], "z" : rectangle_coo[0][2]},
                    "nd_2" : {"x" : rectangle_coo[1][0], "y" : rectangle_coo[1][1], "z" : rectangle_coo[1][2]},
                    "nd_3" : {"x" : rectangle_coo[2][0], "y" : rectangle_coo[2][1], "z" : rectangle_coo[2][2]},
                    "nd_4" : {"x" : rectangle_coo[3][0], "y" : rectangle_coo[3][1], "z" : rectangle_coo[3][2]},
                    "hauteur": {"valeur" : rectangle_coo[4]},
                    "largeur": {"valeur" : rectangle_coo[5]},
                    "G" : {"x":rectangle_coo[6][0],"y":rectangle_coo[6][1], "z":rectangle_coo[6][2] },
            }
        dico["nombre"] = { 
            "propriete" : {
                "ligne" : len(unique_coordinates),
                "cercle" : len(circles),
                "ellipse" : len(ellipse),
                "rectangle" : len(rectangle) 
                }
            }

        return dico

    def _save_coordinates(self, dico: Dict, name: str) -> None:
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        output_path = f"{self.output_dir}/{name}.json"

        a = self.neoud(dico) 
        dico["nombre"]["propriete"]["noeuds"] = a 
        with open(output_path, "w+", encoding="utf-8") as f:
            json.dump(dico, f, ensure_ascii=False, indent=4)

    def neoud(self, data):
        # R�cup�rer les coordonn�es des n�uds
        noeuds = []
        for index in range(data["nombre"]["propriete"]["ligne"]):
            noeud1 = {k: v for k, v in data[f"ln_{index}"]["nd_1"].items() if k in ["x", "y", "z"]}
            noeud2 = {k: v for k, v in data[f"ln_{index}"]["nd_2"].items() if k in ["x", "y", "z"]}
            noeuds.append(noeud1)
            noeuds.append(noeud2)

        # Supprimer les doublons
        noeuds = list({tuple(sorted(n.items())): n for n in noeuds}.values())

        # Trier les n�uds par coordonn�es x et y et ajout ses types 
        noeuds.sort(key=lambda x: (x["x"], x["y"]))

        data["noeuds"] = {}
        for index, noeud in enumerate(noeuds):
            data["noeuds"][f"nd_{index}"] =  noeud 

        return len(noeuds)   

    def process_file(self, name: str) -> None:
        """
        Process a single CAD file.
        
        Args:
            name: Name of the file to process
        """
        try:
            print(f"\nAttempting to open file: {self.dxf_path}\\{name}.dxf")
            
        
            self.cad_path = self.dxf_path + rf"\{name}.dxf"
            self.json_path = self.dxf_path + rf"\{name}.json"
            coordinates, circles, ellipse, rectangle = get_dxf_coordinates(self.cad_path)

            unique_coordinates = self._process_coordinates(coordinates)
            dico = self._create_coordinate_dict(unique_coordinates, circles, ellipse, rectangle)  
            self._save_coordinates(dico, name)
            """
            # Print results
            print(f"\nUnique line coordinates found in {name}.dxf:")
            print("Format: (x1, y1, z1, x2, y2, z2)")
            print(f"Total unique lines: {len(unique_coordinates)}")
            print(f"Total circles: {len(circles)}")
            print(f"Total ellipse: {len(ellipse)}") 
            print(f"Total rectangle: {len(rectangle)}") 
            """

        except FileNotFoundError as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            sys.exit(1)

convert_all(a["input"], a["output"], a["ODA"]) 
"""Main function to process all CAD files."""

processor = CADProcessor(output_dir=a["output"])
compteur = 0
for file_name in processor.file_names:
    processor.process_file(file_name)

    a["portique_" + str(compteur)] = processor.json_path
    a["folder_name_"+ str(compteur)] = f"{file_name}" 
    compteur+=1
    a["nombre_courbe"] = compteur
    with open(CHEMIN , "w+") as f:
        json.dump(a,f, ensure_ascii=False, indent=4) 
    
