from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from django.urls import reverse
# Assurez-vous que les imports des modèles et des utilitaires sont corrects
from .models import Course, Pilote, Pari, CustomUser, Participation
from .forms import CustomUserCreationForm
import random
from .utils import get_random_city_from_csv
from django.http import JsonResponse
from django.template.loader import render_to_string
from decimal import Decimal, InvalidOperation 
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.core.paginator import Paginator
from django.shortcuts import render

# Durée d'un pari 
PARI_DURATION_MINUTES = 2

# --- FONCTION UTILITAIRE POUR LA CRÉATION DES PARTICIPATIONS (NON MODIFIÉE) ---
def _creer_participations_pour_course(course):
    """ Sélectionne 10 pilotes et génère leurs probabilités pour la course donnée. """
    pilotes = Pilote.objects.all().order_by('?')[:10]
    
    # 1. Générer les poids et le total
    poids = [random.randint(1, 100) for _ in pilotes]
    total_poids = sum(poids)

    if total_poids == 0:
        return # Aucun pilote disponible

    # 2. Créer les objets Participation avec probabilités
    for pilote, p in zip(pilotes, poids):
        proba = round((p / total_poids) * 100, 2)
        Participation.objects.create(course=course, pilote=pilote, proba=proba)

    # 3. Ajuster la dernière probabilité pour garantir un total de 100%
    participations = Participation.objects.filter(course=course).order_by('id')
    current_sum = sum([p.proba for p in participations])
    diff = 100 - current_sum
    
    if participations.exists():
        last_participation = participations.last()
        last_participation.proba = round(last_participation.proba + diff, 2)
        last_participation.save()
# --- FIN DE LA FONCTION UTILITAIRE ---


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'betkarting_app/register.html', {'form': form})

def profile(request):
    # 1. On récupère tous les paris de l'utilisateur, du plus récent au plus ancien
    pari_list = request.user.pari_set.all().order_by('-date')
    
    # 2. Configuration de la pagination : 10 éléments par page
    paginator = Paginator(pari_list, 10)
    
    # 3. Récupération de la page actuelle depuis l'URL
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 4. On envoie l'utilisateur (pour le solde) ET l'objet page (pour le tableau)
    context = {
        'user': request.user,
        'page_obj': page_obj
    }
    
    return render(request, 'betkarting_app/profile.html', context)

@login_required
def reglement(request):
    return render(request, 'betkarting_app/reglement.html')

@login_required
def home(request):
    """
    Page d'accueil / affichage du pari en cours avec probabilités correctes.
    """
    # Tente de trouver la course non terminée la plus récente
    course = Course.objects.filter(resultat_calcule=False).order_by('-date_debut').first()
    
    if course:
        # Si le temps est écoulé, redirige vers la vue de fin de pari
        if timezone.now() > course.date_debut + timedelta(minutes=PARI_DURATION_MINUTES):
            return redirect('terminer_pari_et_preparer_suivant', course_id=course.id)
    
    # Si 'course' est None, on crée la nouvelle course et ses participations
    if not course:
        # 1. Créer une course
        ville = get_random_city_from_csv()
        course = Course.objects.create(ville=ville, record=round(random.uniform(100.0, 150.0), 2), resultat_calcule=False)
        
        # 2. Générer les participations/probabilités
        _creer_participations_pour_course(course)

    # On récupère les participations
    participations = Participation.objects.filter(course=course).select_related('pilote') 
    
    # Vérifie si l'utilisateur a déjà un pari sur la course actuelle.
    pari_utilisateur_actuel = Pari.objects.filter(user=request.user, course=course).first()

    # Calculer le temps restant
    temps_restant = (course.date_debut + timedelta(minutes=PARI_DURATION_MINUTES)) - timezone.now()
    
    # --- DÉBUT DES AJOUTS POUR L'ACTUALISATION AUTOMATIQUE ---
    
    # Calculer l'heure d'expiration en millisecondes depuis l'époque UNIX pour le JS
    date_expiration = course.date_debut + timedelta(minutes=PARI_DURATION_MINUTES)
    date_expiration_ms = int(date_expiration.timestamp() * 1000)

    # URL de la fonction pour terminer le pari (utilisée par le JS)
    url_terminer_pari = reverse('terminer_pari_et_preparer_suivant', kwargs={'course_id': course.id})

    # --- FIN DES AJOUTS POUR L'ACTUALISATION AUTOMATIQUE ---
    
    context = {
        "course": course,
        "participations": participations,
        "temps_restant": temps_restant,
        "pari_utilisateur": pari_utilisateur_actuel,
        "date_expiration_ms": date_expiration_ms,
        "url_terminer_pari": url_terminer_pari,
    }
    return render(request, "betkarting_app/home.html", context)

@login_required
def parier(request, course_id):
    user = request.user
    
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return redirect("home") 

    participations = Participation.objects.filter(course=course)
    pari_existant = Pari.objects.filter(user=user, course=course).exists()

    if pari_existant:
        error_message = "Vous avez déjà placé un pari pour cette course."
        pari_utilisateur_actuel = Pari.objects.get(user=user, course=course) 
        
        # Le temps restant est nécessaire pour rendre la page home correcte
        temps_restant = (course.date_debut + timedelta(minutes=PARI_DURATION_MINUTES)) - timezone.now()

        # AJOUT pour contexte complet en cas d'erreur de pari
        date_expiration = course.date_debut + timedelta(minutes=PARI_DURATION_MINUTES)
        date_expiration_ms = int(date_expiration.timestamp() * 1000)
        url_terminer_pari = reverse('terminer_pari_et_preparer_suivant', kwargs={'course_id': course.id})
        
        return render(request, "betkarting_app/home.html", {
            "course": course,
            "participations": participations,
            "error": error_message,
            "pari_utilisateur": pari_utilisateur_actuel,
            "temps_restant": temps_restant, 
            "date_expiration_ms": date_expiration_ms,
            "url_terminer_pari": url_terminer_pari,
        })

    if request.method == "POST":
        
        # Vérification d'expiration du temps de pari
        if timezone.now() > course.date_debut + timedelta(minutes=PARI_DURATION_MINUTES):
            error_message = "Le temps des paris est écoulé pour cette course."
            
            # AJOUT pour contexte complet en cas d'erreur
            date_expiration = course.date_debut + timedelta(minutes=PARI_DURATION_MINUTES)
            date_expiration_ms = int(date_expiration.timestamp() * 1000)
            url_terminer_pari = reverse('terminer_pari_et_preparer_suivant', kwargs={'course_id': course.id})
            
            return render(request, "betkarting_app/home.html", {
                "course": course,
                "participations": participations,
                "error": error_message,
                "date_expiration_ms": date_expiration_ms,
                "url_terminer_pari": url_terminer_pari,
            })
            
        try:
            pilote_id = request.POST.get("pilote_id")
            montant = Decimal(request.POST.get("montant", "0"))
            multiplicateur = Decimal(request.POST.get("multiplicateur", "1")) # IMPORTANT: Le multiplicateur est lu ici en Decimal !
        except:
            error_message = "Erreur de format pour le montant ou le multiplicateur."
            
            # AJOUT pour contexte complet en cas d'erreur
            date_expiration = course.date_debut + timedelta(minutes=PARI_DURATION_MINUTES)
            date_expiration_ms = int(date_expiration.timestamp() * 1000)
            url_terminer_pari = reverse('terminer_pari_et_preparer_suivant', kwargs={'course_id': course.id})
            
            return render(request, "betkarting_app/home.html", {
                "course": course, 
                "participations": participations, 
                "error": error_message,
                "date_expiration_ms": date_expiration_ms,
                "url_terminer_pari": url_terminer_pari,
            })

        if montant <= 0:
            error_message = "Le montant misé doit être supérieur à zéro."

            # AJOUT pour contexte complet en cas d'erreur
            date_expiration = course.date_debut + timedelta(minutes=PARI_DURATION_MINUTES)
            date_expiration_ms = int(date_expiration.timestamp() * 1000)
            url_terminer_pari = reverse('terminer_pari_et_preparer_suivant', kwargs={'course_id': course.id})
            
            return render(request, "betkarting_app/home.html", {
                "course": course, 
                "participations": participations, 
                "error": error_message,
                "date_expiration_ms": date_expiration_ms,
                "url_terminer_pari": url_terminer_pari,
            })

        pilote = Pilote.objects.get(id=pilote_id)

        if user.balance >= montant:
            # Opérations : retirer le solde et créer le pari
            user.remove_balance(montant)
            Pari.objects.create(
                user=user,
                course=course,
                pilote_choisi=pilote,
                montant=montant,
                multiplicateur=multiplicateur # Multiplicateur est stocké comme Decimal
            )
            return redirect("home")
        else:
            # Erreur : Solde insuffisant
            
            # AJOUT pour contexte complet en cas d'erreur
            date_expiration = course.date_debut + timedelta(minutes=PARI_DURATION_MINUTES)
            date_expiration_ms = int(date_expiration.timestamp() * 1000)
            url_terminer_pari = reverse('terminer_pari_et_preparer_suivant', kwargs={'course_id': course.id})
            
            return render(request, "betkarting_app/home.html", {
                "course": course,
                "participations": participations,
                "error": "Solde insuffisant.",
                "date_expiration_ms": date_expiration_ms,
                "url_terminer_pari": url_terminer_pari,
            })

    return redirect("home")

@login_required
def terminer_pari_et_preparer_suivant(request, course_id):
    """
    Termine le pari de la course donnée, calcule les résultats,
    et déclenche la préparation de la prochaine course.
    Renvoie un JSON si c'est une requête AJAX.
    """
    # Détecter si la requête vient de JavaScript (nécessite l'en-tête 'X-Requested-With')
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'Course not found.'}, status=404)
        return redirect("home")

    if course.resultat_calcule:
        # Si déjà calculé, on retourne juste l'ID de la course
        if is_ajax:
            return JsonResponse({'success': True, 'course_id': course.id, 'already_calculated': True})
        return redirect('resultats', course_id=course.id)

    # --- LOGIQUE DE CALCUL ---
    participations = Participation.objects.filter(course=course)
    pilotes = [p.pilote for p in participations]
    probabilites = [p.proba for p in participations]
    
    gagnant = random.choices(pilotes, weights=probabilites, k=1)[0]
    
    # Mise à jour des paris et des balances utilisateurs
    paris = Pari.objects.filter(course=course)
    for pari in paris:
        # CORRECTION n°1: Comparer par ID pour éviter les problèmes d'objets en mémoire
        if pari.pilote_choisi.id == gagnant.id:
            pari.resultat = "gagné"
            
            # CORRECTION n°2: Résoudre le TypeError (Decimal * float)
            # Puisque le modèle Pari définit 'multiplicateur' comme FloatField (float),
            # nous devons le convertir en Decimal pour la multiplication avec pari.montant (Decimal).
            multiplicateur_decimal = Decimal(str(pari.multiplicateur))
            
            # Le calcul est maintenant Decimal * Decimal
            pari.user.add_balance(pari.montant * multiplicateur_decimal)
        else:
            pari.resultat = "perdu"
        pari.save()
    
    # Marquer la course comme terminée
    course.resultat_calcule = True
    course.gagnant = gagnant 
    course.save()

    # LOGIQUE DE CRÉATION DU NOUVEAU PARI
    ville = get_random_city_from_csv()
    nouvelle_course = Course.objects.create(ville=ville, record=round(random.uniform(100.0, 150.0), 2), resultat_calcule=False)
    _creer_participations_pour_course(nouvelle_course) 

    # --- MODIFICATION CLÉ ---
    if is_ajax:
        # Renvoyer l'ID de la course terminée au JavaScript
        return JsonResponse({'success': True, 'course_id': course.id})

    return redirect("home") 

@login_required
def add_credit(request):
    if request.method == 'POST':
        amount_raw = request.POST.get('amount', '0')
        try:
            # On convertit en Decimal au lieu de float
            amount = Decimal(amount_raw)
            
            if amount > 0:
                user = request.user
                # Maintenant les deux types sont compatibles (Decimal + Decimal)
                user.balance += amount
                user.save()
                messages.success(request, f"{amount} € ont été ajoutés à votre compte !")
            else:
                messages.error(request, "Le montant doit être supérieur à 0.")
        except (InvalidOperation, ValueError):
            messages.error(request, "Montant invalide. Veuillez entrer un nombre correct.")
            
    return redirect('profile')


@login_required
def get_resultats_html(request, course_id):
    """
    Récupère les résultats d'une course et les rend en HTML pour l'injection dans la modale.
    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return JsonResponse({'error': 'Course not found.'}, status=404)
        
    if not course.resultat_calcule:
        return JsonResponse({'error': 'Results not yet calculated.'}, status=400)
    
    # Filtrer les paris pour l'utilisateur connecté
    paris_utilisateur = Pari.objects.filter(course=course, user=request.user)
    # Le gagnant est un objet Pilote ou None
    gagnant = course.gagnant if course.gagnant else None
    
    context = {
        "course": course,
        "gagnant": gagnant,
        "paris": paris_utilisateur, 
    }
    
    # Rendre le template en tant que string
    html_content = render_to_string("betkarting_app/resultats.html", context, request=request)
    
    return JsonResponse({'success': True, 'html': html_content})

