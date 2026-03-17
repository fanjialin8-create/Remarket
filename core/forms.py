"""
Remarket Forms
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from .models import Item


class CustomPasswordResetForm(PasswordResetForm):
    """Password reset form - use with CustomPasswordResetView for error handling"""


class RegistrationForm(UserCreationForm):
    """User registration"""
    email = forms.EmailField(max_length=254, required=True, label='Email')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email


class LoginForm(forms.Form):
    """User login"""
    username = forms.CharField(max_length=150, label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return single_file_clean(data, initial)


class ItemForm(forms.ModelForm):
    """Post/Edit item"""
    images = MultipleFileField(required=True)

    class Meta:
        model = Item
        fields = ('title', 'description', 'price', 'condition', 'location', 'category')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Item title', 'class': 'form-control auth-input'}),
            'description': forms.Textarea(attrs={'placeholder': 'Item description', 'rows': 4, 'class': 'form-control auth-input'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Price', 'step': '0.01', 'class': 'form-control auth-input'}),
            'condition': forms.Select(attrs={'class': 'form-select auth-input'}),
            'location': forms.TextInput(attrs={'placeholder': 'Pickup location', 'class': 'form-control auth-input'}),
            'category': forms.Select(attrs={'class': 'form-select auth-input'}),
        }