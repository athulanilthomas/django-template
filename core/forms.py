from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'Paypal')
)

ISSUE_CHOICES = (
    ('DMG', 'Damaged product received'),
    ('WRG', 'Wrong item received'),
    ('NRA', 'Not received all products'),
    ('DPL', 'Duplicate item received'),
    ('OTH', 'Other')
)


class CheckoutForm(forms.Form):
    first_name = forms.CharField(
        max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control'}))

    street_address = forms.CharField(
        max_length=500, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address'}))

    apartment_address = forms.CharField(
        required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apartment, suite, unit etc. (optional)'}))

    country = CountryField(blank_label='(select country)').formfield(
        widget=CountrySelectWidget(attrs={'class': 'form-control'}))

    state = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control'}))

    pincode = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Areas pincode'}))

    phone = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Phone number'}))

    # same_billing_address = forms.BooleanField(
    #     widget=forms.CheckboxInput(attrs={'class': 'form-control'}))

    # save_info = forms.BooleanField(
    #     widget=forms.CheckboxInput(attrs={'class': 'form-control'}))

    payment_options = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'class': 'form-control'}), choices=PAYMENT_CHOICES)


class RequestRefundForm(forms.Form):
    ref_code = forms.CharField(required=True, max_length=20, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your order refference id'}))
    issue = forms.ChoiceField(choices=ISSUE_CHOICES,
                              widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Please select issue'}), initial='DMG')
    issue_description = forms.CharField(required=True, max_length=500, widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Description of your request', 'rows': 4}))
