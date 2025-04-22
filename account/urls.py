from django.urls import path
from .views import Register, Login, UserProfile, Logout

urlpatterns = [
    path('register/', Register, name='register'),
    path('login/', Login, name='login'),
    path('profile/', UserProfile, name='profile'),
    path('logout/', Logout, name='logout'),
] 