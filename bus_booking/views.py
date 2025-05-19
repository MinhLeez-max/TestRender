from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta

from .models import BusCompany, BusStation, BusRoute, BusTrip, Seat, Booking
from .forms import SearchForm, UserRegistrationForm, BookingForm, UserProfileForm

def home(request):
    """Trang chủ với form tìm kiếm và thông tin nhà xe nổi bật"""
    search_form = SearchForm()
    
    # Lấy các nhà xe nổi bật (rating cao)
    featured_companies = BusCompany.objects.order_by('-rating')[:6]
    
    # Lấy các tuyến đường phổ biến
    popular_routes = BusRoute.objects.all()[:6]
    
    return render(request, 'home.html', {
        'search_form': search_form,
        'featured_companies': featured_companies,
        'popular_routes': popular_routes,
    })

def ketquatimkiem(request):
    """Hiển thị kết quả tìm kiếm chuyến xe"""
    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            departure_city = form.cleaned_data['departure_city']
            arrival_city = form.cleaned_data['arrival_city']
            departure_date = form.cleaned_data['departure_date']
            
            # Lấy các bến xe tại thành phố đi và đến
            departure_ben = BusStation.objects.filter(city=departure_city)
            arrival_ben = BusStation.objects.filter(city=arrival_city)
            
            # Tìm các tuyến đường phù hợp
            routes = BusRoute.objects.filter(
                departure_station__in=departure_ben,
                arrival_station__in=arrival_ben
            )
            
            # Tìm các chuyến xe trong ngày đã chọn
            start_date = datetime.combine(departure_date, datetime.min.time())
            end_date = datetime.combine(departure_date, datetime.max.time())
            
            trips = BusTrip.objects.filter(
                route__in=routes,
                departure_time__range=(start_date, end_date)
            ).order_by('departure_time')
            
            return render(request, 'ketquatimkiem.html', {
                'form': form,
                'trips': trips,
                'departure_city': departure_city,
                'arrival_city': arrival_city,
                'departure_date': departure_date,
            })
    else:
        form = SearchForm()
    
    return render(request, 'ketquatimkiem.html', {'form': form})

def chitietchuyendi(request, trip_id):
    """Hiển thị chi tiết chuyến xe và form đặt vé"""
    trip = get_object_or_404(BusTrip, id=trip_id)
    available_seats = trip.seats.filter(is_booked=False)
    
    if request.method == 'POST' and request.user.is_authenticated:
        seat_id = request.POST.get('seat_id')
        if seat_id:
            seat = get_object_or_404(Seat, id=seat_id, trip=trip)
            if not seat.is_booked:
                return redirect('confirm_booking', trip_id=trip.id, seat_id=seat.id)
            else:
                messages.error(request, "Ghế này đã được đặt. Vui lòng chọn ghế khác.")
    
    return render(request, 'chitietchuyendi.html', {
        'trip': trip,
        'available_seats': available_seats,
    })

@login_required
def confirm_booking(request, trip_id, seat_id):
    """Xác nhận thông tin đặt vé"""
    trip = get_object_or_404(BusTrip, id=trip_id)
    seat = get_object_or_404(Seat, id=seat_id, trip=trip)
    
    if seat.is_booked:
        messages.error(request, "Ghế này đã được đặt. Vui lòng chọn ghế khác.")
        return redirect('chitietchuyendi', trip_id=trip.id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.trip = trip
            booking.seat = seat
            booking.status = 'confirmed'  # Đơn giản hóa, trong thực tế có thể là 'pending' và chờ thanh toán
            booking.save()
            
            messages.success(request, "Đặt vé thành công!")
            return redirect('xacnhandatphong', booking_id=booking.id)
    else:
        # Tự động điền thông tin người dùng
        initial_data = {
            'passenger_name': f"{request.user.first_name} {request.user.last_name}",
            'passenger_email': request.user.email,
        }
        form = BookingForm(initial=initial_data)
    
    return render(request, 'xacnhandatphong.html', {
        'form': form,
        'trip': trip,
        'seat': seat,
    })

@login_required
def xacnhandatphong(request, booking_id):
    """Hiển thị thông tin xác nhận đặt vé"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    trip = booking.trip
    
    return render(request, 'xacnhandatphong.html', {
        'booking': booking,
        'trip': trip,
        'seat': booking.seat,
        'is_confirmed': True,
    })

@login_required
def lichsudatve(request):
    """Hiển thị lịch sử đặt vé của người dùng"""
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_time')
    
    # Lọc theo trạng thái nếu có
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    return render(request, 'lichsudatve.html', {
        'bookings': bookings,
        'status_filter': status_filter,
    })

@login_required
def huydatve(request, booking_id):
    """Hủy đặt vé"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Kiểm tra xem có thể hủy không (ví dụ: chuyến đi chưa khởi hành)
    if booking.trip.departure_time <= timezone.now():
        messages.error(request, "Không thể hủy đặt vé cho chuyến đã khởi hành.")
        return redirect('lichsudatve')
    
    # Kiểm tra thời gian hủy (ví dụ: phải hủy trước 24 giờ)
    cancel_deadline = booking.trip.departure_time - timedelta(hours=24)
    if timezone.now() > cancel_deadline:
        messages.error(request, "Đã quá thời gian cho phép hủy vé (24 giờ trước khi khởi hành).")
        return redirect('lichsudatve')
    
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, "Đã hủy đặt vé thành công.")
        return redirect('lichsudatve')
    
    return render(request, 'huydatve.html', {'booking': booking})

@login_required
def infonguoidung(request):
    """Quản lý thông tin cá nhân"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật thông tin thành công!")
            return redirect('infonguoidung')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'infonguoidung.html', {'form': form})

def register(request):
    """Đăng ký tài khoản mới"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Đăng ký tài khoản thành công!")
            return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def nhaxe(request):
    """Hiển thị danh sách nhà xe"""
    companies = BusCompany.objects.all().order_by('-rating')
    
    return render(request, 'nhaxe.html', {'companies': companies})

def ben(request):
    """Hiển thị danh sách bến xe"""
    # Nhóm các bến xe theo thành phố
    cities = BusStation.objects.values_list('city', flat=True).distinct().order_by('city')
    city_ben = {}
    
    for city in cities:
        city_ben[city] = BusStation.objects.filter(city=city).order_by('name')
    
    return render(request, 'ben.html', {'city_ben': city_ben})
