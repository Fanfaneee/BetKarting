from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=10000)

    def __str__(self):
        return self.username

    def add_balance(self, amount):
        self.balance += amount
        self.save()

    def remove_balance(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False

    def total_paris(self):
        return sum(
            bet.montant * bet.multiplicateur if bet.resultat=="gagné" else -bet.montant
            for bet in self.pari_set.all()
        )

class Course(models.Model):
    ville = models.CharField(max_length=100)
    record = models.FloatField()
    pilotes = models.ManyToManyField('Pilote', through='Participation')
    date_fin_paris = models.DateTimeField(null=True, blank=True)
    date_debut = models.DateTimeField(default=timezone.now) # Ajout
    resultat_calcule = models.BooleanField(default=False) # Ajout
    gagnant = models.ForeignKey('Pilote', on_delete=models.SET_NULL, null=True, blank=True,related_name='gagnant_des_courses')

    def __str__(self):
        return f"Course à {self.ville}"
    def is_betting_open(self):
        # La course est ouverte si la date_fin_paris n'est pas passée ET si les résultats n'ont pas encore été calculés
        if self.date_fin_paris:
            return self.date_fin_paris > timezone.now() and not self.pari_set.filter(resultat__isnull=False).exists()
        return False
    
    def pilote_probabilities(self):
        return {pilote: pilote.proba for pilote in self.pilotes.all()}


class Pilote(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    equipe = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.equipe}"

class Participation(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    pilote = models.ForeignKey(Pilote, on_delete=models.CASCADE)
    proba = models.FloatField(help_text="Probabilité du pilote pour cette course (en %)")

    class Meta:
        unique_together = ('course', 'pilote')



class Pari(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    pilote_choisi = models.ForeignKey(Pilote, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    multiplicateur = models.FloatField(default=1.0)
    resultat = models.CharField(max_length=20, null=True, blank=True)  # "gagné", "perdu"
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pari de {self.user.username} sur {self.pilote_choisi} ({self.course})"

    def full_name(self):
        return f"{self.pilote_choisi.prenom} {self.pilote_choisi.nom}"

    def calcul_gain(self):
        return float(self.montant) * self.multiplicateur if self.resultat == "gagné" else 0
