import os
import sys
import django
import csv

# Ajouter le dossier parent (racine du projet) pour que Django trouve betkarting_app
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Définir la variable d'environnement pour Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'betkarting_project.settings')
django.setup()

from betkarting_app.models import Pilote

# Chemin vers le fichier CSV
csv_file_path = os.path.join(BASE_DIR, "data", "pilotes.csv")

with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        prenom = row['Prénom']
        nom = row['Nom']
        equipe = row['Equipe']
        
        pilote, created = Pilote.objects.get_or_create(
            prenom=prenom,
            nom=nom,
            defaults={'equipe': equipe}
        )
        if created:
            print(f"Pilote créé : {pilote}")
        else:
            print(f"Pilote existant : {pilote}")
