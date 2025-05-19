from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class BusCompany(models.Model):
    name = models.CharField(max_length=100, verbose_name='Tên nhà xe')
    description = models.TextField(verbose_name='Mô tả', blank=True)
    logo = models.URLField(verbose_name='Logo URL', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Số điện thoại')
    email = models.EmailField(verbose_name='Email', blank=True)
    website = models.URLField(verbose_name='Website', blank=True)
    rating = models.FloatField(verbose_name='Đánh giá', default=0, blank=True)
    
    class Meta:
        verbose_name = 'Nhà xe'
        verbose_name_plural = 'Nhà xe'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class BusStation(models.Model):
    name = models.CharField(max_length=100, verbose_name='Tên bến xe')
    city = models.CharField(max_length=50, verbose_name='Thành phố')
    address = models.CharField(max_length=200, verbose_name='Địa chỉ')
    description = models.TextField(verbose_name='Mô tả', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Số điện thoại', blank=True)
    
    class Meta:
        verbose_name = 'Bến xe'
        verbose_name_plural = 'Bến xe'
        ordering = ['city', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.city}"

class BusRoute(models.Model):
    departure_station = models.ForeignKey(BusStation, on_delete=models.CASCADE, 
                                          related_name='departure_routes', 
                                          verbose_name='Bến đi')
    arrival_station = models.ForeignKey(BusStation, on_delete=models.CASCADE, 
                                        related_name='arrival_routes', 
                                        verbose_name='Bến đến')
    distance = models.PositiveIntegerField(verbose_name='Khoảng cách (km)')
    duration = models.PositiveIntegerField(verbose_name='Thời gian di chuyển (phút)')
    
    class Meta:
        verbose_name = 'Tuyến đường'
        verbose_name_plural = 'Tuyến đường'
        unique_together = ['departure_station', 'arrival_station']
    
    def __str__(self):
        return f"{self.departure_station.name} → {self.arrival_station.name}"

class BusTrip(models.Model):
    BUS_TYPES = [
        ('limousine', 'Limousine'),
        ('sleeper', 'Giường nằm'),
        ('seater', 'Ghế ngồi'),
        ('express', 'Xe khách'),
    ]
    
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, 
                             related_name='trips', verbose_name='Tuyến đường')
    company = models.ForeignKey(BusCompany, on_delete=models.CASCADE, 
                               related_name='trips', verbose_name='Nhà xe')
    departure_time = models.DateTimeField(verbose_name='Giờ khởi hành')
    arrival_time = models.DateTimeField(verbose_name='Giờ đến')
    price = models.PositiveIntegerField(verbose_name='Giá vé (VNĐ)')
    bus_type = models.CharField(max_length=20, choices=BUS_TYPES, verbose_name='Loại xe')
    total_seats = models.PositiveSmallIntegerField(verbose_name='Tổng số ghế')
    amenities = models.TextField(verbose_name='Tiện ích', blank=True)
    
    class Meta:
        verbose_name = 'Chuyến xe'
        verbose_name_plural = 'Chuyến xe'
        ordering = ['departure_time']
    
    def __str__(self):
        return f"{self.company.name}: {self.route} - {self.departure_time.strftime('%d/%m/%Y %H:%M')}"
    
    def available_seats(self):
        return self.total_seats - self.seats.filter(is_booked=True).count()
    available_seats.short_description = 'Số ghế còn trống'
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Tạo chỗ ngồi khi chuyến đi được tạo lần đầu.
        if is_new:
            for i in range(1, self.total_seats + 1):
                Seat.objects.create(trip=self, seat_number=i)

class Seat(models.Model):
    trip = models.ForeignKey(BusTrip, on_delete=models.CASCADE, 
                            related_name='seats', verbose_name='Chuyến xe')
    seat_number = models.PositiveSmallIntegerField(verbose_name='Số ghế')
    is_booked = models.BooleanField(default=False, verbose_name='Đã đặt')
    
    class Meta:
        verbose_name = 'Ghế'
        verbose_name_plural = 'Ghế'
        unique_together = ['trip', 'seat_number']
    
    def __str__(self):
        return f"Ghế {self.seat_number} - {self.trip}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ thanh toán'),
        ('confirmed', 'Đã xác nhận'),
        ('cancelled', 'Đã hủy'),
        ('completed', 'Đã hoàn thành'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                            related_name='bookings', verbose_name='Người dùng')
    trip = models.ForeignKey(BusTrip, on_delete=models.CASCADE, 
                            related_name='bookings', verbose_name='Chuyến xe')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, 
                           related_name='bookings', verbose_name='Ghế')
    booking_time = models.DateTimeField(default=timezone.now, verbose_name='Thời gian đặt')
    passenger_name = models.CharField(max_length=100, verbose_name='Tên hành khách')
    passenger_phone = models.CharField(max_length=20, verbose_name='SĐT hành khách')
    passenger_email = models.EmailField(verbose_name='Email hành khách', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                             default='pending', verbose_name='Trạng thái')
    note = models.TextField(verbose_name='Ghi chú', blank=True)
    
    class Meta:
        verbose_name = 'Đặt vé'
        verbose_name_plural = 'Đặt vé'
        ordering = ['-booking_time']
    
    def __str__(self):
        return f"{self.passenger_name} - {self.trip} - Ghế {self.seat.seat_number}"
    
    def save(self, *args, **kwargs):
        # Đánh dấu chỗ ngồi là đã đặt khi việc đặt chỗ được tạo.
        if self.pk is None and self.status in ['pending', 'confirmed']:
            self.seat.is_booked = True
            self.seat.save()
        
        # Cập nhật trạng thái đặt chỗ khi trạng thái đặt chỗ thay đổi.
        if self.pk is not None:
            old_booking = Booking.objects.get(pk=self.pk)
            if old_booking.status != self.status:
                if self.status in ['cancelled']:
                    self.seat.is_booked = False
                    self.seat.save()
                elif self.status in ['confirmed', 'pending'] and not self.seat.is_booked:
                    self.seat.is_booked = True
                    self.seat.save()
        
        super().save(*args, **kwargs)
