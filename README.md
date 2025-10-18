# Méthode de Rotation - Analyse Structurelle

## 📋 Vue d'ensemble

Ce projet implémente une méthode de rotation pour l'analyse structurelle en C++. Il traite des données géométriques et mécaniques depuis des fichiers JSON, calcule les propriétés pour les lignes, nœuds, rectangles, et détermine les moments et forces pour divers éléments structurels.

## 🏗️ Architecture du Projet

### Structure des Dossiers
```
Methode de rotation/
├── headers/                    # Définitions des classes
│   ├── Application.h          # Utilitaires JSON et fonctions globales
│   ├── line.h                # Classe Line pour les éléments linéaires
│   ├── node.h                # Classe Node pour les nœuds
│   ├── MomentEncastrement.h  # Calculs des moments d'encastrement
│   ├── constante.h           # Constantes mécaniques et géométriques
│   ├── Inertie.h            # Calculs d'inertie
│   └── matrix.h             # Classe Matrix pour calculs matriciels
├── src/
│   ├── Application.cpp       # Point d'entrée principal
│   └── logic/               # Implémentations des classes
│       ├── line.cpp
│       ├── node.cpp
│       ├── MomentEncastrement.cpp
│       ├── constante.cpp
│       ├── Inertie.cpp
│       └── matrix.cpp
├── conv/                    # Scripts Python pour conversion CAD
│   ├── main.py             # Script principal de conversion
│   ├── lecture.py          # Lecture des fichiers DXF
│   └── oda.py             # Interface avec ODA File Converter
├── dwg/                    # Fichiers CAD source (.dwg)
├── output/                 # Fichiers JSON générés
├── ODA/                    # Outils de conversion ODA
└── chemin.json             # Configuration des chemins
```

## 🔧 Classes Principales

### 1. Classe `Line`
**Fichier:** `headers/line.h` | `src/logic/line.cpp`

Représente un élément linéaire (poutre, colonne) dans la structure.

#### Propriétés Principales:
```cpp
class Line {
public:
    unordered_map<string, float> node_1, node_2;  // Coordonnées des nœuds
    float length;                                  // Longueur de l'élément
    bool is_column, is_beam, is_inclined;         // Type d'élément
    float inclination_angle;                       // Angle d'inclinaison
    SectionLine forme;                            // Section de l'élément
    float charge;                                 // Charge appliquée
    string type_force;                           // Type de force
};
```

#### Méthodes Clés:
- `Line(int id, data, angle_tolerance, scale)` - Constructeur
- `check_is_consol()` - Vérifie si l'élément est en console
- `is_column_type()` - Détermine si c'est une colonne
- `section()` - Calcule les propriétés de section
- `force()` - Calcule les forces appliquées

### 2. Classe `Node`
**Fichier:** `headers/node.h` | `src/logic/node.cpp`

Représente un nœud de connexion dans la structure.

#### Propriétés:
```cpp
class Node {
public:
    int id;                                      // Identifiant du nœud
    string type;                                 // Type de nœud
    unordered_map<string, float> coordinates;   // Coordonnées (x, y, z)
};
```

### 3. Classe `MomemtEncastrement`
**Fichier:** `headers/MomentEncastrement.h` | `src/logic/MomentEncastrement.cpp`

Calcule les moments d'encastrement parfait pour les éléments.

#### Propriétés:
```cpp
class MomemtEncastrement : public ConstanteLine {
public:
    int i, j;                                    // Nœuds de début et fin
    unordered_map<string, float> M;              // Moments
    unordered_map<string, float> Tork;           // Torques
};
```

#### Méthodes de Calcul:
- `rectangular()` - Calcul pour sections rectangulaires
- `Rotation(Gamma T)` - Calcul des rotations
- `To(Gamma T)` - Calcul des torques

### 4. Classe `Matrix`
**Fichier:** `headers/matrix.h` | `src/logic/matrix.cpp`

Gère les calculs matriciels et la rigidité de la structure.

#### Propriétés:
```cpp
class Matrix {
public:
    unordered_map<string, vector<string>> floor;     // Groupement par étages
    unordered_map<string, vector<string>> section;   // Groupement par sections
    int RigidityMatrixSize;                          // Taille de la matrice de rigidité
    Eigen::MatrixXd RigidityMatrix();                // Matrice de rigidité
private:
    std::unique_ptr<unordered_map<string, std::unique_ptr<Node>>> ND;
    std::unique_ptr<unordered_map<string, std::unique_ptr<MomemtEncastrement>>> LINE;
    bool With_Wind;                                  // Prise en compte du vent
    string Direction;                                // Direction du vent
    float E;                                         // Module de Young
    float I_equi;                                    // Inertie équivalente
};
```

#### Méthodes Clés:
- `Ignored_nodes()` - Retourne les nœuds ignorés
- `MovingNodes()` - Retourne les nœuds mobiles
- `GetMoveColumn(string node_name)` - Obtient la colonne mobile
- `GetBeamChoce(string node_name, string PreviousBeam)` - Sélectionne la poutre
- `GetAllMoveColumn(string node_name)` - Obtient toutes les colonnes mobiles

### 5. Classe `ConstanteLine`
**Fichier:** `headers/constante.h` | `src/logic/constante.cpp`

Gère les constantes mécaniques et géométriques des éléments.

#### Propriétés:
```cpp
class ConstanteLine : public Line {
public:
    float E;                    // Module de Young
    float I_equivalent;         // Inertie équivalente
    float I;                    // Inertie réelle
    float alpha;                // Rapport inertie/inertie équivalente
    float K;                    // Constante de rigidité
    float a, b, c;             // Coefficients de calcul
    vector<Gamma> GAMMA;        // Valeurs gamma pour calculs
};
```

## 🔄 Pipeline de Traitement

### 1. Conversion CAD → JSON
**Script:** `src/conv/main.py`

```python
# Conversion automatique DWG → DXF → JSON
processor = CADProcessor(output_dir="output")
processor.process_file("Eleonor")  # Génère Eleonor.json
```

### 2. Traitement C++
**Fichier:** `src/Application.cpp`

```cpp
// Chargement des données JSON
json data = loadJsonFromFile("output/Eleonor.json");

// Création des objets structurels
Node node = Node(0, jsonToNestedMap(data));
Line line = Line(0, jsonToNestedMap(data), 5.0f, 50);
MomemtEncastrement moment = MomemtEncastrement(0, jsonToNestedMap(data));

// Calculs matriciels
Matrix matrix = Matrix(jsonToNestedMap(data), true, "right", 50, 5.0f);

// Affichage des résultats
std::cout << "Type de ligne: " << (line.is_consol ? "Console" : "Simple") << std::endl;
std::cout << "Module de Young: " << moment.E << std::endl;
std::cout << "Constante de rigidité: " << moment.K << std::endl;
```

## 📊 Format JSON

### Structure des Données
```json
{
  "ln_0": {
    "nd_1": {"x": 0.0, "y": 0.0, "z": 0.0},
    "nd_2": {"x": 5.0, "y": 0.0, "z": 0.0}
  },
  "rectangle_0": {
    "nd_1": {"x": 0.0, "y": 0.0, "z": 0.0},
    "nd_2": {"x": 1.0, "y": 0.0, "z": 0.0},
    "nd_3": {"x": 1.0, "y": 1.0, "z": 0.0},
    "nd_4": {"x": 0.0, "y": 1.0, "z": 0.0},
    "hauteur": {"valeur": 0.3},
    "largeur": {"valeur": 0.2},
    "G": {"x": 0.5, "y": 0.5, "z": 0.0}
  },
  "circle_{i}" : {
    "center": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
    },
    "propriete":{ 
          "radius" : 5.2 
        }
  },
  "nombre": {
    "propriete": {
      "ligne": 10,
      "cercle": 2,
      "ellipse": 1,
      "rectangle": 3,
      "neouds": 15
    }
  }
}
```

## 🛠️ Installation et Configuration

### Prérequis
- **Visual Studio 2022** avec support C++20
- **Python 3.8+** avec modules: `json`, `pathlib`, `typing`
- **ODA File Converter** (inclus dans le projet)
- **nlohmann/json** (via NuGet)
- **Eigen 3.4.0** (inclus dans le projet)

### Configuration

1. **Chemins de fichiers** - Éditer `chemin.json`:
```json
{
  "input": "C:\\Users\\votre_user\\Desktop\\MatriceOne\\Methode de rotation\\dwg",
  "ODA": "C:\\Users\\votre_user\\Desktop\\MatriceOne\\Methode de rotation\\ODA\\ODAFileConverter.exe",
  "output": "C:\\Users\\votre_user\\Desktop\\MatriceOne\\Methode de rotation\\output"
}
```

2. **Compilation Visual Studio:**
   - Ouvrir `Methode de rotation.sln`
   - Restaurer les packages NuGet
   - Configurer en Release x64
   - Compiler le projet

### Workflow de Développement

1. **Préparation des données:**
```bash
# Placer vos fichiers .dwg dans le dossier dwg/
# Exécuter la conversion automatique
python src/conv/main.py
```

2. **Compilation et exécution:**
```bash
# Dans Visual Studio
Build → Build Solution (Ctrl+Shift+B)
Debug → Start Debugging (F5)
```

3. **Résultats:**
   - Fichiers JSON générés dans `output/`
   - Sortie console avec calculs structurels
   - Logs détaillés des propriétés mécaniques

## 🔍 Développement et Extension

### Ajout de Nouveaux Types d'Éléments

1. **Créer une nouvelle classe:**
```cpp
// headers/NewElement.h
class NewElement : public Line {
public:
    NewElement(int id, data_map data);
    void calculateSpecificProperties();
private:
    float specific_parameter;
};
```

2. **Implémenter les méthodes:**
```cpp
// src/logic/NewElement.cpp
NewElement::NewElement(int id, data_map data) : Line(id, data) {
    calculateSpecificProperties();
}

void NewElement::calculateSpecificProperties() {
    // Logique spécifique
}
```

### Modification des Calculs de Moments

1. **Étendre la classe MomentEncastrement:**
```cpp
class CustomMoment : public MomemtEncastrement {
public:
    CustomMoment(int id, data_map data);
    unordered_map<string, float> customCalculation();
};
```

### Ajout de Nouveaux Types de Sections

1. **Étendre la structure SectionLine:**
```cpp
struct SectionLine {
    string type;           // "rectangular", "circular", "custom"
    string dimensions;     // Format spécifique au type
    int id;
    // Ajouter de nouveaux champs selon besoin
};
```

## 🧪 Tests et Validation

### Tests Unitaires Recommandés

```cpp
// Test de la classe Line
void testLineProperties() {
    Line line(0, test_data);
    assert(line.length > 0);
    assert(line.is_column || line.is_beam);
}

// Test des calculs de moments
void testMomentCalculations() {
    MomemtEncastrement moment(0, test_data);
    assert(moment.K > 0);
    assert(moment.E > 0);
}

// Test de la classe Matrix
void testMatrixCalculations() {
    Matrix matrix(test_data, true);
    assert(matrix.RigidityMatrixSize > 0);
}
```

### Validation des Résultats

1. **Vérification géométrique:**
   - Longueurs des éléments
   - Angles d'inclinaison
   - Connexions entre nœuds

2. **Validation mécanique:**
   - Cohérence des modules de Young
   - Inerties positives
   - Moments d'encastrement réalistes

3. **Validation matricielle:**
   - Taille de la matrice de rigidité
   - Symétrie de la matrice
   - Déterminant non nul

## 📈 Optimisations Possibles

### Performance
- **Parallélisation:** Utiliser `std::async` pour les calculs indépendants
- **Cache:** Mémoriser les résultats de calculs coûteux
- **Allocation:** Utiliser des pools d'objets pour les structures fréquentes

### Mémoire
- **Smart pointers:** Remplacer les raw pointers par `std::unique_ptr`
- **Move semantics:** Optimiser les transferts de données
- **Reserve:** Pré-allouer les vecteurs selon les besoins

### Architecture
- **Pattern Observer:** Pour les mises à jour automatiques
- **Factory Pattern:** Pour la création d'éléments
- **Strategy Pattern:** Pour les différents algorithmes de calcul

## 🐛 Débogage

### Points de Contrôle Courants

1. **Problèmes de conversion JSON:**
```cpp
// Vérifier la structure des données
std::cout << "JSON structure: " << data.dump(2) << std::endl;
```

2. **Erreurs de calcul:**
```cpp
// Valider les paramètres d'entrée
assert(E > 0 && "Module de Young doit être positif");
assert(I > 0 && "Inertie doit être positive");
```

3. **Problèmes de géométrie:**
```cpp
// Vérifier les coordonnées
std::cout << "Node 1: (" << node_1["x"] << ", " << node_1["y"] << ")" << std::endl;
std::cout << "Node 2: (" << node_2["x"] << ", " << node_2["y"] << ")" << std::endl;
```

4. **Problèmes matriciels:**
```cpp
// Vérifier la matrice de rigidité
std::cout << "Taille matrice: " << matrix.RigidityMatrixSize << std::endl;
std::cout << "Nœuds mobiles: " << matrix.MovingNodes().size() << std::endl;
```

## 📚 Documentation Technique

### Constantes Physiques
- **Module de Young (E):** 210 GPa pour l'acier, 30 GPa pour le béton
- **Inertie équivalente:** Calculée selon les normes en vigueur
- **Coefficients alpha, K:** Dépendent de la géométrie et du matériau

### Algorithmes Implémentés
- **Méthode de rotation:** Calcul des moments d'encastrement
- **Détermination des types:** Colonnes, poutres, consoles
- **Calculs géométriques:** Longueurs, angles, sections
- **Calculs matriciels:** Matrice de rigidité avec Eigen

### Extensions Futures
- Support pour les charges réparties
- Calculs de déformations
- Interface graphique
- Export vers des formats CAO
- Analyse dynamique
- Optimisation topologique

## 🤝 Contribution

### Standards de Code
- **Nommage:** PascalCase pour les classes, camelCase pour les méthodes
- **Documentation:** Commentaires Doxygen pour les méthodes publiques
- **Tests:** Tests unitaires pour chaque nouvelle fonctionnalité

### Workflow Git
1. Créer une branche feature: `git checkout -b feature/nouvelle-fonctionnalite`
2. Développer et tester
3. Commit avec message descriptif: `git commit -m "feat: ajout calcul déformations"`
4. Pull request vers main

## 📋 Changelog

### Version 1.1.0 (2025-01-03)
- ✅ Ajout de la classe `Matrix` pour calculs matriciels
- ✅ Intégration d'Eigen pour calculs matriciels avancés
- ✅ Support pour l'analyse du vent
- ✅ Amélioration de la gestion des nœuds mobiles
- ✅ Optimisation des calculs de rigidité

### Version 1.0.0 (2024-12-01)
- ✅ Implémentation des classes de base (Line, Node, MomentEncastrement)
- ✅ Système de conversion CAD → JSON
- ✅ Calculs de moments d'encastrement
- ✅ Support des sections rectangulaires

---

**Auteur:** TSARALOHA Nomenjanahary Christnot Léonnel Calixte  
**Version:** 1.1.0  
**Dernière mise à jour:** 03/01/2025 
