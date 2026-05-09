from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('screening/', views.screening, name='screening'),
    
    # Admin response URLs
    path('admin/send-response/<int:consultation_id>/', views.send_response_form, name='send_response'),
    path('admin/send-whatsapp/<int:consultation_id>/', views.send_whatsapp_manual, name='send_whatsapp'),
]