from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import BusStation, Booking

class SearchForm(forms.Form):
    departure_city = forms.ModelChoiceField(
        queryset=BusStation.objects.values_list('city', flat=True).distinct(),
        to_field_name='city',
        empty_label="-- Chọn thành phố đi --",
        label="Thành phố đi",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    arrival_city = forms.ModelChoiceField(
        queryset=BusStation.objects.values_list('city', flat=True).distinct(),
        to_field_name='city',
        empty_label="-- Chọn thành phố đến --",
        label="Thành phố đến",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    departure_date = forms.DateField(
        label="Ngày đi",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        departure_city = cleaned_data.get('departure_city')
        arrival_city = cleaned_data.get('arrival_city')
        
        if departure_city and arrival_city and departure_city == arrival_city:
            raise forms.ValidationError("Thành phố đi và đến không được trùng nhau.")
        
        return cleaned_data

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email", 
                            widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, label="Họ", 
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, label="Tên", 
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add bootstrap classes to the default fields
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['passenger_name', 'passenger_phone', 'passenger_email', 'note']
        widgets = {
            'passenger_name': forms.TextInput(attrs={'class': 'form-control'}),
            'passenger_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'passenger_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
