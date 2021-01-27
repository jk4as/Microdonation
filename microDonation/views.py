# REFERENCES
# Title: Simple Ecommerce
# Author: overiq
# Date Published: Dec 8, 2018
# Date Accessed: Oct 18, 2020
# Code version: commit 704596f
# URL: https://github.com/overiq/simple_ecommerce
# Software License: MIT License

from django.shortcuts import render, HttpResponse, redirect, get_object_or_404, reverse
from django.contrib import messages
from django.conf import settings
from django.template.defaultfilters import slugify
from decimal import Decimal
from paypal.standard.forms import PayPalPaymentsForm
from django.views.decorators.csrf import csrf_exempt
from .models import CharityOrg, Cause, Order, LineItem, User
from .forms import CartForm, CheckoutForm, CharityForm, CauseForm, DeleteForm, CharitySearchForm, BasicSearchForm
from . import cart
from taggit.models import Tag
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from django.db.models import Count
from django.template import RequestContext

# Create your views here.

def index(request):
    return render(request, 'microDonation/index.html', {})

def not_authorized(request):
    return render(request, 'microDonation/login.html', {})

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(request, email=user.email, password=raw_password)
            if user is not None:
                login(request, user)
            else:
                print("user is not authenticated")
            return redirect('microDonation/')
    else:
        form = SignupForm()
    return render(request, 'microDonation/login.html', {'form': form})

def about(request):
    return render(request, 'microDonation/about.html', {})

def login(request):
    return render(request, 'microDonation/login.html', {'all_charities': CharityOrg.objects.filter(is_deleted = False)})



@login_required
def logout(request):
    django_logout(request)
    return render(request, 'microDonation/login.html')

# hey bradley, am I correctly passing in the list of charities?
def charities(request):
    return render(request,'microDonation/charities.html', {'all_charities': CharityOrg.objects.filter(is_deleted = False)}
)

def show_charity(request, charity_id):
    charityOrg = get_object_or_404(CharityOrg, id=charity_id)
    charity_causes = Cause.objects.filter(charity=charityOrg.pk).filter(is_deleted=False)
    charity_orders = charityOrg.charity_orders.all()
    charity_dict = {}
    for o in charity_orders:
        charity_dict[o] = o.charity_cost(charityOrg)
    print("charity orders")
    print(charity_orders)
    if charityOrg.is_deleted:
        return redirect('charities')
    else:
        return render(request, 'microDonation/charity_detail.html', {'charity': charityOrg,
        'causes': charity_causes,
        'orders': charity_dict,
        })

@login_required
def create_charity(request):
    if request.method == 'POST':
        form = CharityForm(request.POST, request.FILES)
        print(form['authorized_users'], flush=True)
        if form.is_valid():
            authorized_users = form.cleaned_data.get('authorized_users').split(',')
            authenticated_users = []
            for user in authorized_users:
                if User.objects.filter(email=user).exists():
                    authenticated_users.append(User.objects.get(email=user))
            if authenticated_users == []:
                authenticated_users.append(request.user)
            newCharity = form.save(commit=False)
            newCharity.slug = slugify(newCharity.name)
            newCharity.save()
            form.save_m2m()
            newCharity.authenticated_users.set(authenticated_users)
            newCharity.save()
            return redirect('charities')
    form = CharityForm(initial={'authorized_users': request.user.email})
    return render(request, 'microDonation/create_charity.html', {
        'form': form
        })

@login_required
def update_charity(request, charity_id):
    charityorg = CharityOrg.objects.get(id=charity_id)
    if charityorg.is_deleted:
        return redirect('charities')
    if charityorg.authenticated_users.filter(id=request.user.id).exists():
        if request.method == 'POST':
            updateform = CharityForm(request.POST, request.FILES, instance=charityorg)
            if updateform.is_valid():
                authorized_users = updateform.cleaned_data.get('authorized_users').split(',')
                authenticated_users = []
                for user in authorized_users:
                    if User.objects.filter(email=user).exists():
                        authenticated_users.append(User.objects.get(email=user))
                if authenticated_users == []:
                    authenticated_users.append(request.user)
                charityorg = updateform.save(commit=False)
                charityorg.slug = slugify(charityorg.name)
                charityorg.save()
                updateform.save_m2m()
                charityorg.authenticated_users.set(authenticated_users)
                charityorg.save()
            return redirect('charities')
        else:
            authenticated_users = charityorg.authenticated_users.all()
            authorized_users = ""
            for user in authenticated_users:
                authorized_users = authorized_users + user.email + ","
            form = CharityForm(initial={'authorized_users': authorized_users},instance=charityorg)
            return render(request, 'microDonation/update_charity.html', {
                'form': form,
            })
    else:
        return redirect('not_authorized')

@login_required
def delete_charity(request, charity_id):
    charityorg = CharityOrg.objects.get(id=charity_id)
    if charityorg.is_deleted:
        return redirect('charities')
    if charityorg.authenticated_users.filter(id=request.user.id).exists():
        if request.method == 'POST':
            deleteform = DeleteForm(request.POST)
            if deleteform.is_valid():
                print("Form is valid!")
                charityorg.is_deleted = deleteform.cleaned_data['delete']
                charityorg.save()
            else:
                print("Form is invalid!")
                print(deleteform.errors)
            return redirect('charities')
        else:
            form = DeleteForm(request)
            return render(request, 'microDonation/delete_charity.html', {
                'form': form,
                'charity': charityorg,
            })
    else:
        return redirect('not_authorized')

def show_cause(request, cause_id):
    cause = get_object_or_404(Cause, id=cause_id)
    if cause.is_deleted:
        return redirect('show_charity', cause.charity.pk)
    if request.method == 'POST':
        cartform = CartForm(request, request.POST)
        if cartform.is_valid():
            request.form_data = cartform.cleaned_data
            cart.add_item_to_cart(request)
            return redirect('show_cart')

    form = CartForm(request, initial={'cause_id': cause.id})
    return render(request, 'microDonation/cause_detail.html', {
        'cause': cause,
        'form': form,
        })

@login_required
def create_cause(request, charity_id):
    charity = get_object_or_404(CharityOrg, id=charity_id)
    if charity.authenticated_users.filter(id=request.user.id).exists():
        if request.method == 'POST':
            form = CauseForm(request.POST, request.FILES)
            if form.is_valid():
                newCause = form.save(commit=False)
                newCause.slug = slugify(newCause.name)
                newCause.charity = charity
                newCause.save()
                form.save_m2m()
                return redirect('show_charity', charity.pk)
        form = CauseForm(data={'charity':charity})
        return render(request, 'microDonation/create_cause.html', {
            'form': form,
            })
    else:
        return redirect('not_authorized')

@login_required
def update_cause(request, cause_id):
    cause = Cause.objects.get(id=cause_id)
    if cause.is_deleted:
        return redirect('show_charity', cause.charity.pk)
    if cause.charity.authenticated_users.filter(id=request.user.id).exists():
        if request.method == 'POST':
            updateform = CauseForm(request.POST, request.FILES, instance=cause)
            if updateform.is_valid():
                cause = updateform.save(commit=False)
                cause.slug = slugify(cause.name)
                cause.save()
                updateform.save_m2m()
            return redirect('show_charity', cause.charity.pk)
        else:
            form = CauseForm(instance=cause)
            return render(request, 'microDonation/update_cause.html', {
                'form': form,
            })
    else:
        return redirect('not_authorized')

@login_required
def delete_cause(request, cause_id):
    cause = Cause.objects.get(id=cause_id)
    if cause.is_deleted:
        return redirect('show_charity', cause.charity.pk)
    if cause.charity.authenticated_users.filter(id=request.user.id).exists():
        if request.method == 'POST':
            deleteform = DeleteForm(request.POST)
            if deleteform.is_valid():
                print("Form is valid!")
                cause.is_deleted = deleteform.cleaned_data['delete']
                cause.save()
            else:
                print("Form is invalid!")
                print(deleteform.errors)
            return redirect('show_charity', cause.charity.pk)
        else:
            form = DeleteForm(request)
            return render(request, 'microDonation/delete_cause.html', {
                'form': form,
            })
    else:
        return redirect('not_authorized')

def show_cart(request):
    print("attempting to show cart ", flush=True)
    if request.method == 'POST':
        if request.POST.get('submit') == 'Update':
            cart.update_item(request)
        if request.POST.get('submit') == 'Remove':
            cart.remove_item(request)
    cart_items = cart.get_all_cart_items(request)
    cart_subtotal = cart.subtotal(request)
    print("attempting to render page ", flush=True)
    return render(request, 'microDonation/cart.html', {'cart_items': cart_items,
        'cart_subtotal': cart_subtotal,
    })

def search_charity(request):
    form = CharitySearchForm()
    results = []
    if request.method == 'POST':
        form = BasicSearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            cForm = CharitySearchForm({'search_type': 'name', 'search_value': form.cleaned_data.get("search_val")})
            results = list(CharityOrg.objects.filter(name__icontains=data.get('search_val')).filter(is_deleted = False))
            return render(request, 'microDonation/charity_search.html', {'form': cForm, 'results': results})
        form = CharitySearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if data.get('search_type') == 'name':
                results = list(CharityOrg.objects.filter(name__icontains=data.get('search_value')).filter(is_deleted = False))
            elif data.get('search_type') == 'min_causes':
                min_value = data.get('search_value')
                obj_to_count = CharityOrg.objects.annotate(Count('cause'))
                for i in range(len(obj_to_count)):
                    if obj_to_count[i].cause__count >= int(min_value):
                        charity = CharityOrg.objects.get(id=obj_to_count[i].id)
                        if getattr(charity, 'is_deleted') == False:
                            results.append(charity)
            elif data.get('search_type') == 'tags':
                tags = [tag.strip() for tag in data.get('search_value').split(',')]
                results = CharityOrg.objects.filter(tags__name__in=tags).filter(is_deleted = False).distinct()
            else:
                print("search type is invalid")
                pass
        else:
            print("form is not valid")
    return render(request, 'microDonation/charity_search.html', {
        'form': form,
        'results': results,
    })

def _generate_order_id(): # Creates a random 10-character-long string
    import string, random # Although extremely unlikely, it does check for duplicates
    orderID = ''
    while True:
        orderID = ''
        for i in range(0,10):
            orderID = orderID.join(random.choice(string.ascii_letters + string.digits))
        if Order.objects.filter(order_id=orderID).count() == 0:
            return orderID

def process_payment(request):
    order_id = request.session.get('order_id')
    print("ORDER ID")
    print(order_id)
    order = get_object_or_404(Order, id=order_id)
    host = request.get_host()

    paypal_dict = {
            
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': '%.2f' % Decimal(order.total_cost()).quantize(
                Decimal('.01')),
            'item_name': 'Order {}'.format(order.order_id),
            'invoice': str(order.order_id),
            'currency_code': 'USD',
            'notify_url': 'http://{}{}'.format(host,
                reverse('paypal-ipn')),
            'return_url': 'http://{}{}'.format(host,
                reverse('payment_done')),
            'cancel_return': 'http://{}{}'.format(host,
                reverse('payment_cancelled')),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'microDonation/process_payment.html', {'order': order, 'form': form})

@csrf_exempt
def payment_done(request):
    return render(request, 'microDonation/payment_done.html')

@csrf_exempt
def payment_cancelled(request):
    return render(request, 'microDonation/payment_cancelled.html')

def checkout(request):
    cart_subtotal = cart.subtotal(request)
    all_items = cart.get_all_cart_items(request)
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            order_charities = set()
            for cart_item in all_items:
                order_charities.add(CharityOrg.objects.get(id=Cause.objects.get(id=cart_item.cause_id).charity.id))
            o = form.save(commit=False)
            o.save()
            form.save_m2m()
            o.charities.set(list(order_charities))
            o.save()
            
            for cart_item in all_items:
                li = LineItem(
                        cause_id = cart_item.cause_id,
                        value = cart_item.value,
                        order_id = o.id
                )
                li.save()

            cart.clear(request)
            request.session['order_id'] = o.id
            print("ORDER ID 1")
            print(request.session['order_id'])
            return redirect('process_payment')
    else:
        form = CheckoutForm()
        return render(request, 'microDonation/checkout.html', locals())
