
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class AddGS(forms.Form):
    GSBrand = forms.CharField(label="GS Brand Name", max_length=100)
    GSConcentration = forms.DecimalField(label="GS Concentration (mg/mL)", max_digits=4, decimal_places=2)
    GSPrice = forms.DecimalField(label="GS Price ($/unit)", max_digits=5, decimal_places=2)
    

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
    
    def clean(self):
        
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email exists")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username has already been registered")
        return self.cleaned_data