from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns =[
    path('',views.home ,name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='betkarting_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('parier/<int:course_id>/', views.parier, name='parier'),
    
    path('terminer_pari_et_preparer_suivant/<int:course_id>/', views.terminer_pari_et_preparer_suivant, name='terminer_pari_et_preparer_suivant'),
    
    # Nouvelle API pour le contenu HTML de la modale
    path('api/resultats_html/<int:course_id>/', views.get_resultats_html, name='api_resultats_html'),
    

    
]
