from django.urls import path
from . import views

urlpatterns = [
    path('ask/', views.ask_view, name='ask_question'),
]
