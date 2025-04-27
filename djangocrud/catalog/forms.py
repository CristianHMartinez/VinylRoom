from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
from .models import Address


# User registration form
class UserRegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'UserInput', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'UserInput', 'placeholder': 'Email'}),
            'password1': forms.PasswordInput(attrs={'class': 'UserInput', 'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'class': 'UserInput', 'placeholder': 'Confirm password'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'UserInput', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'UserInput', 'placeholder': 'Confirm password'})
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('A user with this email already exists.'))
        return email

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if username and User.objects.filter(username=username).exists():
            self.add_error('username', _('A user with this username already exists.'))

        if email and User.objects.filter(email=email).exists():
            self.add_error('email', _('A user with this email already exists.'))

        return cleaned_data

# Authentication form
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'UserInput',
            'placeholder': 'Username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'UserInput',
            'placeholder': 'Password'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(self.request, username=username, password=password)
            if user is None:
                raise forms.ValidationError(_('Invalid username or password.'))
            if not user.is_active:
                raise forms.ValidationError(_('This account is inactive.'))
            
        if username and not User.objects.filter(username=username).exists():
            self.add_error('username', _('A user with this username does not exist.'))

        return cleaned_data
    

# Address form
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street_address', 'city', 'state', 'zip_code', 'country']

class SelectAddressForm(forms.Form):
    address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        widget=forms.RadioSelect,
        required=True,
        label="Elige una dirección de envío"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['address'].queryset = Address.objects.filter(user=user)

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'UserInput', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'UserInput', 'placeholder': 'Email'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(UserProfileUpdateForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError(_('A user with this email already exists.'))
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError(_('A user with this username already exists.'))
        return username
    

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'UserInput',
            'placeholder': 'Current Password'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'UserInput',
            'placeholder': 'New Password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'UserInput',
            'placeholder': 'Confirm New Password'
        })