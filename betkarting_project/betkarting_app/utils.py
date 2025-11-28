# betkarting_app/utils.py

import csv
import os
import random

# --- NOUVELLE MÉTHODE POUR CONSTRUIRE LE CHEMIN RELATIF ---

# Base du projet (le dossier betkarting_project)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Chemin vers le dossier data
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Chemin FINAL du fichier CSV
CSV_FILE_PATH = os.path.join(DATA_DIR, 'courses_villes.csv')

# ---------------------------------------------------------

def get_random_city_from_csv():
    cities = []
    
    # AJOUT DE CETTE VÉRIFICATION POUR AIDER AU DÉBOGAGE
    if not os.path.exists(CSV_FILE_PATH):
        print(f"Erreur CRITIQUE: Le fichier CSV n'existe PAS à : {CSV_FILE_PATH}")
        return None
    
    try:
        # Lire le fichier en utilisant le chemin calculé
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # La colonne s'appelle 'City' dans votre CSV
                if 'City' in row and row['City'].strip():
                    cities.append(row['City'].strip())

    except Exception as e:
        print(f"Une erreur est survenue lors de la lecture du CSV: {e}")
        return None

    if cities:
        return random.choice(cities)
    else:
        print("Avertissement: Le fichier CSV a été lu, mais il est vide ou le format est incorrect (colonnes manquantes).")
        return None