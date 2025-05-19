from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.ketquatimkiem, name='ketquatimkiem'),
    path('trip/<int:trip_id>/', views.chitietchuyendi, name='chitietchuyendi'),
    path('trip/<int:trip_id>/book/<int:seat_id>/', views.confirm_booking, name='confirm_booking'),
    path('booking/<int:booking_id>/confirmation/', views.xacnhandatphong, name='xacnhandatphong'),
    path('bookings/', views.lichsudatve, name='lichsudatve'),
    path('booking/<int:booking_id>/cancel/', views.huydatve, name='huydatve'),
    path('profile/', views.infonguoidung, name='infonguoidung'),
    path('register/', views.register, name='register'),
    path('companies/', views.nhaxe, name='nhaxe'),
    path('ben/', views.ben, name='ben'),
    
]
