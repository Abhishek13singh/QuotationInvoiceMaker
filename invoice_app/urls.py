from django.urls import path
from . import views

urlpatterns = [
    path('', views.letterhead_list, name='letterhead_list'),
    path('create/', views.create_invoice, name='create_invoice'),
    path('invoice/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoice/<int:pk>/pdf/', views.generate_pdf, name='generate_pdf'),
    path('invoice/<int:pk>/word/', views.generate_word, name='generate_word'),
]