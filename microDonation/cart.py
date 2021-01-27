# REFERENCES
# Title: Simple Ecommerce
# Author: overiq
# Date Published: Dec 8, 2018
# Date Accessed: Oct 18, 2020
# Code version: commit 704596f
# URL: https://github.com/overiq/simple_ecommerce
# Software License: MIT License

from .models import CartItem, Cause
from django.shortcuts import get_object_or_404, get_list_or_404

def _cart_id(request):
    if 'cart_id' not in request.session:
        request.session['cart_id'] = _generate_cart_id()

    return request.session['cart_id']

def _generate_cart_id(): # Creates a random 10-character-long string
    import string, random # Although extremely unlikely, it does check for duplicates
    cartID = ''
    while True:
        cartID = ''
        for i in range(0,10):
            cartID = cartID.join(random.choice(string.ascii_letters + string.digits))
        if CartItem.objects.filter(cart_id=cartID).count() == 0:
            return cartID

def get_all_cart_items(request):
    return CartItem.objects.filter(cart_id = _cart_id(request))

def add_item_to_cart(request):
    print("attempting to add item to cart ", flush=True)
    cart_id = _cart_id(request)
    cause_id = request.form_data['cause_id']

    value = request.form_data['value']

    cause = get_object_or_404(Cause, id=cause_id)

    item_in_cart = False
    print("before cart_items", flush=True)
    cart_items = get_all_cart_items(request)
    for cart_item in cart_items:
        if cart_item.cause == cause:
            cart_item.update_value(value)
            item_in_cart = True
    if not item_in_cart:
        item = CartItem(
                cart_id = _cart_id(request),
                value = value,
                cause = cause,
        )

        item.save()
    print("end of function", flush=True)

def item_count(request):
    return get_all_cart_items(request).count()

def subtotal(request):
    cart_item = get_all_cart_items(request)
    sub_total = 0
    for item in cart_item:
        sub_total += item.value
    return sub_total

def remove_item(request):
    cause_id = request.POST.get('cause_id')
    ci = get_object_or_404(CartItem, id=cause_id)
    ci.delete()

def update_item(request):
    cause_id = request.POST.get('cause_id')
    value = request.POST.get('value')
    ci = get_object_or_404(CartItem, id=cause_id)
    ci.value = value
    ci.save()

def clear(request):
    cart_items = get_all_cart_items(request)
    cart_items.delete()
