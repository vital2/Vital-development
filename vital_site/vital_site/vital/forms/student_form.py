from django import forms


class Course_Registration_Form(forms.Form):
    course_registration_code = forms.CharField(widget=forms.TextInput())
