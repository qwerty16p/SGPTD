from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from gestion import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("ingresar/", LoginView.as_view(template_name="login.html"), name="login"),
    path("salir/", LogoutView.as_view(), name="logout"),
    path("gestion/<slug:tipo>/", views.lista, name="lista"),
    path("gestion/<slug:tipo>/crear/", views.editar, name="crear"),
    path("gestion/<slug:tipo>/<int:pk>/", views.detalle, name="detalle"),
    path("gestion/<slug:tipo>/<int:pk>/editar/", views.editar, name="editar"),
    path("gestion/<slug:tipo>/<int:pk>/asociar/", views.asociar, name="asociar"),
    path("departamentos/<int:pk>/quitar/<int:app>/", views.quitar, name="quitar"),
    path("aplicaciones/<int:pk>/eliminar/", views.eliminar, name="eliminar"),
]
