from django.urls import path
from . import views

app_name = 'WebDemo'
urlpatterns = [
    path('',views.index,name="index")
]