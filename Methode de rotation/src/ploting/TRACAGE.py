import json
from re import X 
import matplotlib.pyplot as plt 
from scipy.interpolate import make_interp_spline
import numpy as np

with open("C:/Users/Tsaraloha Christinot/Desktop/Methode-de-rotation-cpp/chemin.json", "+r") as file: 
    ch = json.load(file)


colors = ["r", "k", "b", "g", "y", "c", "m"]

def max_par_index(lists):
    # Trouver la longueur maximale parmi toutes les sous-listes
    max_len = max(len(sublist) for sublist in lists)
    # Pour chaque index, trouver la valeur de plus grande valeur absolue, mais garder son signe d'origine
    result = []
    for i in range(max_len):
        valeurs = [sublist[i] for sublist in lists if i < len(sublist)]
        if valeurs:
            # Trouver la valeur avec la plus grande valeur absolue
            max_val = max(valeurs, key=lambda x: abs(x))
            result.append(max_val)
    return result

def min_par_index(lists):
    # Trouver la longueur maximale parmi toutes les sous-listes
    max_len = max(len(sublist) for sublist in lists)
    # Pour chaque index, trouver la valeur de plus petite valeur absolue, mais garder son signe d'origine
    result = []
    for i in range(max_len):
        valeurs = [sublist[i] for sublist in lists if i < len(sublist)]
        if valeurs:
            # Trouver la valeur avec la plus petite valeur absolue, mais garder son signe
            min_val = min(valeurs, key=lambda x: abs(x))
            result.append(min_val)
    return result

def spline_interpolation(points, num=100):
    """
    Génère une interpolation spline à partir d'une liste de points.
    :param points: liste de tuples (x, y)
    :param num: nombre de points interpolés à générer
    :return: (x_new, y_new) listes des abscisses et ordonnées interpolées
    """
    if len(points) < 2:
        raise ValueError("Au moins deux points sont nécessaires pour l'interpolation spline.")
    # Séparer les abscisses et ordonnées
    x, y = zip(*points)
    # Importer ici pour éviter les problèmes d'import global
    x = np.array(x)
    y = np.array(y)
    # Générer de nouveaux x pour interpolation
    x_new = np.linspace(x.min(), x.max(), num)
    # Créer la spline
    spline = make_interp_spline(x, y, k=3 if len(points) > 3 else 1)
    y_new = spline(x_new)
    return x_new, y_new


class CourbeEnvellope:
    def __init__(self, nom_de_dossier = None , numero = 0 , courbe = "MF", couleur = "k", hachure = True):
        self.folder = nom_de_dossier
        self.numero = numero
        self.courbe = courbe
        self.couleur = couleur
        self.hachure = hachure

        self.type_courbe = courbe

        if self.courbe == "MF":
            self.courbe = "MomentFlechissant.json"
            self.absisse = "X_MF.json"

        elif self.courbe == "ET":
            self.courbe = "EffortTranchant.json"
            self.absisse = "X_ET.json"

        self.chemin_output = f"{ch["output"]}\\{ch["folder_name_"+str(self.numero)]}\\"
        self.line_properties = self.chemin_output + "line_properties.json"

        self.load()
            
    def load(self):
        with open(self.chemin_output + self.courbe , "+r") as file:
            self.curves = json.load(file)

        with open(self.chemin_output + self.absisse , "+r") as file:
            self.X_curves = json.load(file)
                
        with open(f"{ch["portique_"+str(self.numero)]}" , "+r") as file:
            self.data = json.load(file)
        
        with open(self.line_properties, "+r") as file:
            self.line_properties = json.load(file)
        
    
    def trace(self, axe):
        for key, v in self.line_properties.items():
            nd_1 = self.data["noeuds"][f"nd_{int(self.line_properties[key]['noeud_i'])}"]
            nd_2 = self.data["noeuds"][f"nd_{int(self.line_properties[key]['noeud_j'])}"]

            ii = int(self.line_properties[key]['noeud_i'])
            jj = int(self.line_properties[key]['noeud_j'])

            # Tracer la courbe principale
            axe.plot(self.X_curves[key], self.curves[key], self.couleur)

            x_curve = self.X_curves[key]
            y_curve = self.curves[key]
            x0, x1 = x_curve[0], x_curve[-1]
            y0, y1 = y_curve[0], y_curve[-1]

            # Calculer la droite de base (ligne entre les extrémités)
            if x1 != x0:
                y_base = [y0 + (y1 - y0) * (x - x0) / (x1 - x0) for x in x_curve]
            else:
                y_base = [y0 for _ in x_curve]

            if self.hachure:
                # Pour is_beam: colorer haut/bas
                if self.line_properties["ln_" + key.split("_")[-1]]["is_beam"]:
                    # Partie supérieure (courbe au-dessus de la ligne)
                    axe.fill_between(
                        x_curve, y_curve, y_base,
                        where=[yc > yb for yc, yb in zip(y_curve, y_base)],
                        color="r", alpha=0.5, interpolate=True, label='_nolegend_'
                    )
                    # Partie inférieure (courbe en-dessous de la ligne)
                    axe.fill_between(
                        x_curve, y_curve, y_base,
                        where=[yc < yb for yc, yb in zip(y_curve, y_base)],
                        color='blue', alpha=0.5, interpolate=True, label='_nolegend_'
                    )
                # Pour is_column: colorer droite/gauche
                elif self.line_properties["ln_" + key.split("_")[-1]]["is_column"]:
                    # Pour chaque point, calculer la droite verticale passant par la ligne
                    # On suppose que la ligne est verticale (x0==x1), mais on généralise
                    # Pour chaque y de la courbe, calculer la valeur sur la droite de base
                    if y1 != y0:
                        x_base = [x0 + (x1 - x0) * (y - y0) / (y1 - y0) for y in y_curve]
                    else:
                        x_base = [x0 for _ in y_curve]
                    # Partie droite (courbe à droite de la ligne)
                    axe.fill_betweenx(
                        y_curve, x_curve, x_base,
                        where=[xc > xb for xc, xb in zip(x_curve, x_base)],
                        color="r", alpha=0.5, interpolate=True, label='_nolegend_'
                    )
                    # Partie gauche (courbe à gauche de la ligne)
                    axe.fill_betweenx(
                        y_curve, x_curve, x_base,
                        where=[xc < xb for xc, xb in zip(x_curve, x_base)],
                        color='b', alpha=0.5, interpolate=True, label='_nolegend_'
                    )
            
            # Tracage de portique
            axe.plot([nd_1["x"], nd_2["x"]], [nd_1["y"], nd_2["y"]], "k-")

            # Afficher la valeur de la courbe juste après le début et juste avant la fin de chaque ligne
            x_curve = self.X_curves[key]
            y_curve = self.curves[key]
            
            if self.line_properties["ln_" + key.split("_")[-1]]["is_beam"]:
                # Juste après le début (index 1)
                if self.type_courbe == "MF":
                    axe.text(x_curve[1], y_curve[1], f"{self.line_properties[key]["M_"+str(ii)]:.3f}", color="k", fontsize=8, ha="left", va="bottom")
                    # Juste avant la fin (index -2)
                    axe.text(x_curve[-2], y_curve[-2], f"{self.line_properties[key]["M_"+str(jj)]:.3f}", color="k", fontsize=8, ha="right", va="bottom")
                elif self.type_courbe == "ET":
                    axe.text(x_curve[1], y_curve[1], f"{self.line_properties[key]["ET_i"]:.3f}", color="k", fontsize=8, ha="left", va="bottom")
                    # Juste avant la fin (index -2)
                    axe.text(x_curve[-2], y_curve[-2], f"{self.line_properties[key]["ET_j"]:.3f}", color="k", fontsize=8, ha="right", va="bottom")
                    
                # Au valeur max en travee
                if self.line_properties[key]["M_en_travee_max"] != 0 and self.type_courbe == "MF":
                    axe.text(self.line_properties[key]["coo_X"] , self.line_properties[key]["coo_y"] , f"{self.line_properties[key]["M_en_travee_max"]:.3f}", color="k", ha="right", va="bottom")
        
            elif self.line_properties["ln_" + key.split("_")[-1]]["is_column"]:
                # Juste après le début (index 1)
                if self.type_courbe == "MF":
                    axe.text(x_curve[1], y_curve[1], f"{self.line_properties[key]["M_"+str(ii)]:.3f}", color="k", fontsize=8, ha="left", va="bottom")
                    # Juste avant la fin (index -2)
                    axe.text(x_curve[-2], y_curve[-2], f"{self.line_properties[key]["M_"+str(jj)]:.3f}", color="k", fontsize=8, ha="right", va="bottom")
                elif self.type_courbe == "ET":
                    axe.text(x_curve[1], y_curve[1], f"{self.line_properties[key]["ET_i"]:.3f}", color="k", fontsize=8, ha="left", va="bottom")
                    # Juste avant la fin (index -2)
                    axe.text(x_curve[-2], y_curve[-2], f"{self.line_properties[key]["ET_j"]:.3f}", color="k", fontsize=8, ha="right", va="bottom")
                
                # Au valeur max en travee
                if self.line_properties[key]["M_en_travee_max"] != 0 and self.type_courbe == "MF":
                    axe.text(self.line_properties[key]["coo_X"] , self.line_properties[key]["coo_y"] , f"{self.line_properties[key]["M_en_travee_max"]:.3f}", color="k", ha="right", va="bottom")
        
        axe.axis("equal")

    def Words(self, filename="CourbeEnvellope.docx"):
        """
        Exporte la figure matplotlib de la courbe dans un fichier Word (.docx)
        """
        from docx import Document
        from docx.shared import Inches
        import matplotlib.pyplot as plt
        import io

        # Créer un document Word
        doc = Document()
        doc.add_heading('Courbe d\'Enveloppe', 0)

        # Sauvegarder la figure courante dans un fichier temporaire, puis l'ajouter au document Word
        import tempfile
        # Version simplifiée : on utilise plt.savefig directement sans ajuster la taille ni les marges
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            # Agrandir l'image : on choisit une taille de figure plus grande
            fig, axe = plt.subplots(figsize=(12, 12))  # Par exemple, 12 pouces x 12 pouces
            self.trace(axe=axe)
            fig.savefig(tmpfile.name, dpi=300)  # dpi augmenté pour meilleure qualité
            plt.close(fig)
            # Ajouter l'image centrée dans le document Word
            from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
            paragraph = doc.add_paragraph()
            run = paragraph.add_run()
            run.add_picture(tmpfile.name, width=Inches(7))  # Largeur augmentée à 8 pouces
            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        doc.add_paragraph('Figure : Courbe d\'enveloppe générée automatiquement.')

        # Sauvegarder le document
        doc.save(filename)
    
fig, ax = plt.subplots(figsize = (8,3))
# B = CourbeEnvellope(numero = 0,courbe="MF", couleur=colors[1])
# B.trace(axe=ax)
# plt.show()
def All_Curves(axe = ax):
    for i in range(ch["nombre_courbe"]):
        B = CourbeEnvellope(numero=i, courbe="MF", couleur=colors[i], hachure=True)
        B.Words()  

All_Curves()
ax.set_aspect('equal', adjustable='box')
plt.show()

# courbe envelloppe
MF_MAX = {}
MF_MIN = {}

ET_MAX = {}
ET_MIN = {}

Mement_envellope = {} 

portique = []
for i in range(ch["nombre_courbe"]):
    portique.append(CourbeEnvellope(i, i, "MF", colors[i])) 

M_maximum = 0 
for k,v in portique[0].curves.items():
    kil = []
    for i in range(ch["nombre_courbe"]):
        kil.append(portique[i].curves[k])
    MF_MAX[k] = max_par_index(kil) 
    MF_MIN[k] = min_par_index(kil) 
    M_maximum = max(MF_MAX[k])

def CurveIntervalle():
    # Amélioration de l'affichage et ajout de légendes

    # Tracer les courbes d'enveloppe max et min avec légendes
    first_max = True
    first_min = True
    for k, v in MF_MAX.items():
        label = "Enveloppe Max MF" if first_max else None
        plt.plot(portique[0].X_curves[k], v, "m--", label=label)
        first_max = False
        nd_1 = portique[0].data["noeuds"][f"nd_{int(portique[0].node_ij[k]['i'])}"]
        nd_2 = portique[0].data["noeuds"][f"nd_{int(portique[0].node_ij[k]['j'])}"]
        plt.plot([nd_1["x"], nd_2["x"]], [nd_1["y"], nd_2["y"]], "k-", label="Barre" if k == list(MF_MAX.keys())[0] else None)

    for k, v in MF_MIN.items():
        label = "Enveloppe Min MF" if first_min else None
        plt.plot(portique[0].X_curves[k], v, "r--", label=label)
        first_min = False

    plt.xlabel("Abscisse (m)")
    plt.ylabel("Moment fléchissant (kN.m)")
    plt.title("Enveloppe des moments fléchissants (MF)")
    plt.axis("equal")
    plt.grid(True, which='both', linestyle=':', linewidth=0.5, alpha=0.7)
    plt.legend(loc="best", fontsize=9)


