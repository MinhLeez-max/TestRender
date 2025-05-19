from django.contrib import admin
from .models import BusCompany, BusStation, BusRoute, BusTrip, Seat, Booking

@admin.register(BusCompany)
class BusCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'rating')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('rating',)

@admin.register(BusStation)
class BusStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'address', 'phone')
    search_fields = ('name', 'city', 'address')
    list_filter = ('city',)

@admin.register(BusRoute)
class BusRouteAdmin(admin.ModelAdmin):
    list_display = ('departure_station', 'arrival_station', 'distance', 'duration')
    search_fields = ('departure_station__name', 'arrival_station__name')
    list_filter = ('departure_station__city', 'arrival_station__city')

class SeatInline(admin.TabularInline):
    model = Seat
    extra = 0

@admin.register(BusTrip)
class BusTripAdmin(admin.ModelAdmin):
    list_display = ('route', 'company', 'departure_time', 'arrival_time', 'price', 'bus_type', 'available_seats')
    search_fields = ('route__departure_station__name', 'route__arrival_station__name', 'company__name')
    list_filter = ('departure_time', 'bus_type', 'company')
    date_hierarchy = 'departure_time'
    inlines = [SeatInline]

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('trip', 'seat_number', 'is_booked')
    search_fields = ('trip__route__departure_station__name', 'trip__route__arrival_station__name')
    list_filter = ('is_booked', 'trip__company')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'trip', 'booking_time', 'passenger_name', 'passenger_phone', 'status')
    search_fields = ('user__username', 'user__email', 'passenger_name', 'passenger_phone')
    list_filter = ('booking_time', 'status', 'trip__company')
    date_hierarchy = 'booking_time'
