from django.urls import path
from . import views
from .models import Skill,Candidate,Job

urlpatterns = [
    path('',views.index,name='index'),
    path('matcher',views.matcher,name='matcher')
]