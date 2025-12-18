# 🏎️ BetKarting

BetKarting est une plateforme de paris sportifs fictifs sur des courses de karting générées dynamiquement. L'application offre une expérience immersive grâce à un compte à rebours en temps réel, des animations vidéo lors des paris et des résultats injectés dynamiquement via AJAX.



## ✨ Fonctionnalités

- **Courses Dynamiques** : Création automatique de courses dans différentes villes avec génération aléatoire de pilotes et calcul de probabilités de victoire.
- **Système de Paris Optimisé** : 
  - Interface simplifiée avec boutons de sélection fixe (Montants : 100€, 300€, 1000€ | Cotes : x2, x5, x8).
  - Animation vidéo plein écran déclenchée instantanément lors de la validation du pari.
- **Résultats en Temps Réel** : Modale "Racing" avec effet Glassmorphism (flou d'arrière-plan) s'affichant automatiquement à la fin du timer.
- **Profil Pilote Complet** :
  - Gestion du solde (Précision `Decimal`) avec système de ravitaillement de crédits gratuit.
  - Historique des paris avec **pagination** (affichage des 10 derniers paris par page).
- **Design Immersif** : Interface conçue avec **Tailwind CSS**, incluant un thème sombre, des accents `primary-green` et un arrière-plan personnalisé.

## 🚀 Installation et Configuration

### 1. Environnement
```bash
# Entrer dans le dossier du projet
cd betkarting_project

# Créer l'environnement virtuel
python -m venv venv_betkarting

# Activer l'environnement (Windows)
venv_betkarting\Scripts\activate