from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('toggle/<int:id>/', views.toggle_status, name='toggle_status'),
    path('report/', views.generate_pdf, name='generate_pdf'),
]