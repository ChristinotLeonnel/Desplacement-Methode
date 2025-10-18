import ezdxf 
import math 

def get_dxf_coordinates(dxf_path):
    
    try:
        # Ouvrir le fichier DXF
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()
        
        # Initialiser les listes
        line_coordinates = []
        circle_coordinates = []
        ellipse_coordinates = []
        
        # Lire les lignes
        for line in msp.query('LINE'):
            start = line.dxf.start
            end = line.dxf.end
            line_coordinates.append((
                start[0],  # x1
                start[1],  # y1
                start[2],  # z1
                end[0],    # x2
                end[1],    # y2
                end[2]     # z2
            ))
        
        # Lire les cercles
        for circle in msp.query('CIRCLE'):
            center = circle.dxf.center
            radius = circle.dxf.radius
            circle_coordinates.append((
                center[0],  # centre_x
                center[1],  # centre_y
                center[2],  # centre_z
                radius     # rayon
            ))
        
        # Lire les ellipses
        for ellipse in msp.query('ELLIPSE'):
            center = ellipse.dxf.center
            major_axis = ellipse.dxf.major_axis
            ratio = ellipse.dxf.ratio
            
            # Calculer le rayon majeur (longueur du vecteur major_axis)
            major_radius = math.sqrt(major_axis[0]**2 + major_axis[1]**2 + major_axis[2]**2)
            # Calculer le rayon mineur
            minor_radius = major_radius * ratio
            
            # Calculer l'angle de rotation
            angle = math.atan2(major_axis[1], major_axis[0])
            
            ellipse_coordinates.append((
                center[0],      # centre_x
                center[1],      # centre_y
                center[2],      # centre_z
                major_radius,   # rayon_majeur
                minor_radius,   # rayon_mineur
                angle          # angle de rotation
            ))
        
        
        rectangle_coordinates = []

        # Lire les polylignes
        for polyline in msp.query('LWPOLYLINE'):
            # V�rifier si la polyligne est ferm�e
            if not polyline.closed:
                continue
                
            # Obtenir les points de la polyligne
            points = list(polyline.get_points())
            
            # V�rifier si nous avons exactement 4 points
            if len(points) != 4:
                continue
                
            # V�rifier si les angles sont droits
            is_rectangle = True
            for i in range(4):
                p1 = points[i]
                p2 = points[(i + 1) % 4]
                p3 = points[(i + 2) % 4]
                
                # Calculer les vecteurs
                v1 = (p2[0] - p1[0], p2[1] - p1[1])
                v2 = (p3[0] - p2[0], p3[1] - p2[1])
                
                # Calculer le produit scalaire
                dot_product = v1[0] * v2[0] + v1[1] * v2[1]
                
                # Si le produit scalaire n'est pas proche de 0, l'angle n'est pas droit
                if abs(dot_product) > 1e-6:
                    is_rectangle = False
                    break
            A = {"x":points[0][0], "y":points[0][1], "z":points[0][2]}
            B = {"x":points[1][0], "y":points[1][1], "z":points[1][2]}
            C = {"x":points[2][0], "y":points[2][1], "z":points[2][2]}
            D = {"x":points[3][0], "y":points[3][1], "z":points[3][2]}

            a_0 =  (C["y"] - A["y"]) / (C["x"] - A["x"]) 
            a_1 =  (B["y"] - D["y"]) / (B["x"] - D["x"])

            p_0 = C["y"] - a_0*C["x"]
            p_1 = B["y"] - a_1*B["x"] 

            G_x = round((p_0 - p_1) / (a_1 - a_0), 3)
            G_y = round(a_0*G_x + p_0, 3) 
            
            if is_rectangle:
                # Ajouter les coordonn�es du rectangle
                rectangle_coordinates.append((
                    [round(points[0][0],2), round(points[0][1],2), round(points[0][2],2)],  # x1, y1, z1
                    [round(points[1][0],2), round(points[1][1],2), round(points[1][2],2)],  # x2, y2, z2
                    [round(points[2][0],2), round(points[2][1],2), round(points[2][2],2)],  # x3, y3, z3
                    [round(points[3][0],2), round(points[3][1],2), round(points[3][2],2)],  # x4, y4, z4
                    round (points[0][1] - points[3][1],5), # hauteur 
                    round(points[1][0] - points[0][0],5), # largeur 
                    [G_x , G_y, 0] # Centre de graviter
                ))

        return line_coordinates, circle_coordinates, ellipse_coordinates, rectangle_coordinates
        
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier DXF: {str(e)}")
        return [], [], [], []

