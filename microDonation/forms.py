from django import forms
from address.forms import AddressField
from .models import Order, CharityOrg, Cause, User

class CartForm(forms.Form):
    value = forms.DecimalField(initial='1.00')
    cause_id = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(CartForm, self).__init__(*args, **kwargs)

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ('paid','order_id','charities')

class CharityForm(forms.ModelForm):
    authorized_users = forms.CharField(required=False)
    charity_image = forms.FileField(required=True)
    class Meta:
        model = CharityOrg
        fields = [
                'name',
                'description',
                'contact_email',
                'paypal_email',
                'tags',
                'authorized_users',
                'charity_image',
        ]

class CauseForm(forms.ModelForm):
    cause_image = forms.FileField(required=True)
    class Meta:
        model = Cause
        fields = [
                'name',
                'description',
                'tags',
                'cause_image',
        ]

class DeleteForm(forms.Form):
    delete = forms.BooleanField(initial=False, required=False)

class BasicSearchForm(forms.Form):
    search_val = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Search and Explore'}))

class CharitySearchForm(forms.Form):
    search_types = [
            ('name', 'charity name'),
            ('min_causes', 'at least _ causes'),
            ('tags', 'containing one or more tags'),
    ]
    search_type = forms.CharField(label="What should be used to search for the charity?", widget=forms.Select(choices=search_types))
    search_value = forms.CharField(max_length=255)
