import os
import sys
from pathlib import Path

# Assure que le projet est dans le path
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'betkarting_project.settings')

import django
from django.utils import timezone

django.setup()

from betkarting_app.models import Course, Participation, Pari

now = timezone.now()
print('now:', now)

courses = list(Course.objects.all())
print('courses:')
for c in courses:
    print(' ', c.id, c.ville, 'date_fin_paris=', c.date_fin_paris)

print('\nparticipations:')
for p in Participation.objects.all():
    print(' ', p.id, 'course_id=', p.course_id, 'pilote_id=', p.pilote_id, 'proba=', p.proba)

print('\nparis:')
for pa in Pari.objects.all():
    print(' ', pa.id, 'course_id=', pa.course_id, 'user_id=', pa.user_id, 'montant=', pa.montant, 'multiplicateur=', pa.multiplicateur, 'resultat=', pa.resultat)
