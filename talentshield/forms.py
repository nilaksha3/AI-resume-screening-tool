from django import forms
from django.contrib.auth.forms import UserCreationForm
from talentshield.models import CustomUser  # Ensure this is CustomUser, NOT User

from django import forms
from django.contrib.auth.forms import UserCreationForm
from talentshield.models import CustomUser

class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2", "role"]  # Include role


#profile and edit profile
# forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserForm(forms.ModelForm):
    """
    Form for updating user information.
    """
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileForm(forms.ModelForm):
    """
    Form for updating profile information.
    """
    job_title = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-input', 'id': 'id_profile_image', 'style': 'display:none;'})
    )
    
    class Meta:
        model = Profile
        fields = ('job_title', 'phone', 'location', 'profile_image')


