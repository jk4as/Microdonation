from django.conf.urls import url
from django.urls import path

from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
        path('', views.index, name='index'),
        path('not-authorized/', views.not_authorized, name='not_authorized'),
        path('charity/<int:charity_id>/', views.show_charity, name='show_charity'),
        path('charity/create/', views.create_charity, name='create_charity'),
        path('charity/<int:charity_id>/update/', views.update_charity, name='update_charity'),
        path('charity/<int:charity_id>/delete/', views.delete_charity, name='delete_charity'),
        path('charity/search/', views.search_charity, name='search_charity'),
        path('cause/<int:cause_id>/', views.show_cause, name='show_cause'),
        path('charity/<int:charity_id>/create/', views.create_cause, name='create_cause'),
        path('cause/<int:cause_id>/update/', views.update_cause, name='update_cause'),
        path('cause/<int:cause_id>/delete/', views.delete_cause, name='delete_cause'),
        path('cart/', views.show_cart, name='show_cart'),
        path('checkout/', views.checkout, name='checkout'),
        path('process-payment/', views.process_payment, name='process_payment'),
        path('payment-done/', views.payment_done, name='payment_done'),
        path('payment-cancelled/', views.payment_cancelled, name='payment_cancelled'),
        path('about/', views.about, name='about'),
        path('login/', views.login, name='login'),
        path('logout/', views.logout, name='logout'),
        path('charities/', views.charities, name='charities'),
        path('sign-up/', views.signup, name='signup')
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)