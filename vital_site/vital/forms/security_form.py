from django.forms import ModelForm, TextInput
from django import forms
from ..models import VLAB_User
from captcha.fields import CaptchaField
from passwords.fields import PasswordField


class Registration_Form(ModelForm):

    cleaned_data = {}
    # password = forms.CharField(widget=forms.PasswordInput)
    password = PasswordField(label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    captcha = CaptchaField()

    class Meta:
        model = VLAB_User
        fields = ['email', 'first_name', 'last_name', 'password', 'confirm_password', 'admitted_on', 'department',
                  'phone', 'captcha']

    def clean(self):
        cleaned_data = super(Registration_Form, self).clean()
        if 'password' in self.cleaned_data and 'confirm_password' in self.cleaned_data:
            if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
                raise forms.ValidationError("Passwords don't match. Please enter both fields again.")
        return self.cleaned_data


class Forgot_Password_Form(forms.Form):
    email = forms.EmailField(widget=forms.widgets.TextInput)
    captcha = CaptchaField()


class User_Activation_Form(forms.Form):
    code = forms.CharField(widget=TextInput())
    user_email = forms.CharField(widget=forms.HiddenInput())


class Authentication_Form(forms.Form):
    email = forms.EmailField(widget=forms.widgets.TextInput)
    password = forms.CharField(widget=forms.widgets.PasswordInput)

    class Meta:
        fields = ['email', 'password']


class Reset_Password_Form(forms.Form):
    password = PasswordField(label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    user_email = forms.CharField(widget=forms.HiddenInput())
    activation_code = forms.CharField(widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super(Reset_Password_Form, self).clean()
        if 'password' in self.cleaned_data and 'confirm_password' in self.cleaned_data:
            if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
                raise forms.ValidationError("Passwords don't match. Please enter both fields again.")
        return self.cleaned_data