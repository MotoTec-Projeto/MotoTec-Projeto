from django.urls import path
from . import views
from .views import CustomLogoutView

urlpatterns = [
    path('', views.splash_view, name='splash'),
    path('principal/', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('tendencias/', views.tendencias_view, name='tendencias'),
    path('restaurantes/', views.restaurantes_view, name='lista_restaurantes'),
    path('mapa/', views.mapa_view, name='mapa'),
    path('api/demanda/', views.demanda_view, name='demanda'),
    path('recuperar-senha/', views.recuperar_senha_view, name='password_reset'),
    path('definir-nova-senha/', views.definir_nova_senha_view, name='definir_nova_senha'),
    path('api/pedidos_por_restaurante/', views.pedidos_por_restaurante, name='pedidos_por_restaurante'),
    path('teste/', views.pagina_de_teste, name='pagina_de_teste'),
]
