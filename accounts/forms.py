from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

from .models import Profile

User = get_user_model()


class RegistrationForm(forms.Form):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    college_id = forms.CharField(max_length=50)
    phone_number = forms.CharField(max_length=15, required=False, help_text="Your contact number")
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            self.add_error("password2", "Passwords do not match.")
        return cleaned_data

    def save(self):
        email = self.cleaned_data["email"].lower()
        user = User.objects.create_user(
            username=email,
            email=email,
            password=self.cleaned_data["password1"],
            first_name=self.cleaned_data["full_name"],
        )
        Profile.objects.create(
            user=user,
            role=Profile.ROLE_COLLEGE_USER,
            college_id=self.cleaned_data["college_id"],
            phone_number=self.cleaned_data.get("phone_number", ""),
        )
        return user


class ShopOwnerRegistrationForm(forms.Form):
    """Combined form for shop owner account and shop creation"""
    # Owner details
    owner_name = forms.CharField(max_length=150, label="Owner Name")
    email = forms.EmailField(label="Email Address")
    phone_number = forms.CharField(max_length=15, label="Contact Number")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    
    # Shop details
    shop_name = forms.CharField(max_length=150, label="Shop Name")
    shop_description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label="Shop Description")
    shop_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False, label="Shop Address")
    shop_phone = forms.CharField(max_length=15, required=False, label="Shop Contact Number")
    shop_email = forms.EmailField(required=False, label="Shop Email")
    opening_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Opening Time")
    closing_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Closing Time")
    max_orders_per_slot = forms.IntegerField(initial=5, min_value=1, label="Max Orders per 15-min Slot")
    
    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            self.add_error("password2", "Passwords do not match.")
        return cleaned_data
    
    def save(self):
        from shops.models import Shop
        
        email = self.cleaned_data["email"].lower()
        # Create user account
        user = User.objects.create_user(
            username=email,
            email=email,
            password=self.cleaned_data["password1"],
            first_name=self.cleaned_data["owner_name"],
        )
        
        # Create shop owner profile
        Profile.objects.create(
            user=user,
            role=Profile.ROLE_SHOP_OWNER,
            phone_number=self.cleaned_data["phone_number"],
        )
        
        # Create shop
        Shop.objects.create(
            name=self.cleaned_data["shop_name"],
            description=self.cleaned_data.get("shop_description", ""),
            address=self.cleaned_data.get("shop_address", ""),
            phone_number=self.cleaned_data.get("shop_phone", ""),
            email=self.cleaned_data.get("shop_email", ""),
            owner=user,
            opening_time=self.cleaned_data["opening_time"],
            closing_time=self.cleaned_data["closing_time"],
            max_orders_per_slot=self.cleaned_data["max_orders_per_slot"],
        )
        
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")
