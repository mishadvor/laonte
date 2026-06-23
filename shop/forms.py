from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox


class ContactForm(forms.Form):
    name = forms.CharField(label="Имя", max_length=100)
    phone = forms.CharField(label="Телефон", max_length=20)
    message = forms.CharField(label="Сообщение", widget=forms.Textarea, required=False)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
