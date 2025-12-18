# 🏎️ BetKarting

BetKarting est une plateforme **fictive** de paris sportifs sur des courses de karting générées dynamiquement. L'application propose une expérience immersive grâce à un compte à rebours en temps réel, des animations vidéo plein écran lors des paris, possibilités de jouer à plusieurs sur le même pari.

---

##  Fonctionnalités

###  Courses Dynamiques
- Création automatique de courses dans des villes aléatoires.
- Génération dynamique des pilotes.
- Calcul automatique des probabilités de victoire.

###  Système de Paris Optimisé
- Interface de pari simplifiée avec sélections fixes :
  - **Montants** : 100€, 300€, 1000€
  - **Cotes** : x2, x5, x8

###  Résultats en Temps Réel
- Modale "Racing" affichée automatiquement à la fin du timer.

---

##  Installation et Configuration Complète

### 1 Création de l’Environnement Virtuel

```bash
# Entrer dans le dossier du projet
cd betkarting_project

# Créer l'environnement virtuel
python -m venv venv_betkarting

# Activer l'environnement (Windows)
venv_betkarting\Scripts\activate
```

---

### 2 Installation des Dépendances

```bash
# Mise à jour de pip
python -m pip install --upgrade pip

# Installation des packages nécessaires
pip install -r requirements.txt
```

---

### 3 Initialisation de la Base de Données

```bash
# Création des tables dans SQLite
python manage.py migrate
```

---

### 4 Importation des Pilotes (Étape Obligatoire ⚠️)

Avant de lancer le site, vous devez **impérativement** peupler la base de données avec les pilotes.
Sans cette étape, le système ne pourra **pas générer de courses**.

```bash
python betkarting_app/import_pilotes.py
```

---

### 5 Lancer le Serveur

```bash
python manage.py runserver
```

Puis rendez-vous sur :

http://127.0.0.1:8000/

---

## Screenshots 
![Page Home](/betkarting_project/betkarting_app/static/img/page_home.png)


## Architecture des Données

Le projet repose sur une architecture relationnelle Django robuste :

- **CustomUser**  
  Gère l’authentification et le solde financier (`balance`).

- **Course & Participation**  
  Définissent le lieu de la course, les pilotes engagés et leurs probabilités respectives.

- **Pari**  
  Enregistre les mises et calcule les gains de manière sécurisée (`Decimal * Float`).

---

##  Stack Technique

- **Backend** : Django 5.2 (Python 3.13)
- **Frontend** : Tailwind CSS, JavaScript (Vanilla ES6+)
- **Précision Numérique** : Librairie `Decimal` pour la sécurité des calculs monétaires

---

##  Contexte Académique

Projet développé dans le cadre du **MMI3 – BetKarting**.

> ⚠️ Ce projet est **strictement fictif** et n’implique aucun pari réel ou financier.
