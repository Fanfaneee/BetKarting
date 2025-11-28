from django.contrib import admin
from .models import Pilote, Course, Pari, CustomUser, Participation
from django.db import models # Importé pour la référence de models.ManyToManyField


# Enregistrement du modèle utilisateur personnalisé
admin.site.register(CustomUser)


@admin.register(Pilote)
class PiloteAdmin(admin.ModelAdmin):
    # Colonnes visibles dans la liste
    list_display = ('prenom', 'nom', 'equipe') 
    # Barre de recherche
    search_fields = ('nom', 'prenom', 'equipe') 
    # Filtres latéraux
    list_filter = ('equipe',)


# Modèle Inline pour gérer les Participations dans l'interface de Course
class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 1  # Nombre de formulaires vides à afficher


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    # Colonnes visibles dans la liste
    list_display = ('ville', 'record')
    # Filtres latéraux
    list_filter = ('ville',)
    # Ajoute les Participations pour modifier les pilotes de la course
    inlines = [ParticipationInline] 
    # Déplace le champ `pilotes` qui est géré via `ParticipationInline`
    exclude = ('pilotes',)


@admin.register(Pari)
class PariAdmin(admin.ModelAdmin):
    # Colonnes visibles dans la liste
    list_display = ('user', 'course', 'pilote_choisi', 'montant', 'multiplicateur', 'resultat', 'date')
    # Barre de recherche
    search_fields = ('user__username', 'pilote_choisi__nom', 'course__ville')
    # Filtres latéraux
    list_filter = ('resultat', 'course', 'date')
    # Champs en lecture seule
    readonly_fields = ('date',)