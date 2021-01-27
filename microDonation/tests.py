from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import datetime
from .models import Cause
from .models import CharityOrg
from .models import Order
from .models import LineItem
from .models import CartItem
from .models import User
from .models import UserManager
from .forms import CheckoutForm
from .forms import CartForm
from .forms import CharityForm
from .forms import CauseForm
from .forms import DeleteForm
from .forms import CharitySearchForm
from taggit.managers import TaggableManager
from django.http import HttpRequest
from .cart import subtotal, get_all_cart_items

# Model Unit Test
class CharityOrgTestCase(TestCase):
    def setUp(self):
        CharityOrg.objects.create(name="BLM",description="Black Lives Matter",contact_email="blm@example.com",paypal_email="blm@example.com")
    def test_charityOrg_name(self):
        chorg=CharityOrg.objects.get(name="BLM")
        self.assertEqual("BLM",chorg.name)
    def test_charityOrg_description(self):
        chorg=CharityOrg.objects.get(description="Black Lives Matter")
        self.assertFalse(chorg.description=="np")
    def test_charityOrg_paypalEmail(self):
        chorg=CharityOrg.objects.get(paypal_email="blm@example.com")
        self.assertEqual("blm@example.com",chorg.paypal_email)

# Login Test
class LoginTestCase(TestCase):
    def test_loginFail(self):
        c=Client()
        user=User.objects.create_user(username='temp',email="footling@gmail.com",password='tempy')
        user.set_password('temphy')
        user.save()
        user=authenticate(username='temp',password='temphy')
        login=c.login(username='temp',password='tempy')
        self.assertFalse(login)

class AboutPageTestCase(TestCase):
    def test_about(self):
        response=self.client.get(reverse('about'))
        self.assertEqual(response.status_code,200)
        self.assertFalse('username' in response.context)

class NotAuthorizedTestCase(TestCase):
    def test_notAuthorized(self):
        response=self.client.get(reverse('not_authorized'))
        self.assertEqual(response.status_code,200)

class CharityCauseTestCase(TestCase):
    def setUp(self):
        testChorg=CharityOrg.objects.create(name="testChorg",description="example",contact_email="test@example.com",paypal_email="test@example.com")
        testCause=Cause.objects.create(name="testCause",description="example",charity=testChorg)
        testChorg.save()
        testCause.save()
    def test_chooseCharity(self):
        response=self.client.get(reverse('show_charity', kwargs={'charity_id': 1}))
        url=reverse('show_charity',kwargs={'charity_id':1})
        self.assertEqual(response.status_code,200)
        self.assertEqual(url,'/microDonation/charity/1/')
    def test_chooseCause(self):
        response=self.client.get(reverse('show_cause',kwargs={'cause_id': 1}))
        url=reverse('show_cause',kwargs={'cause_id':1})
        self.assertTrue(response.status_code,200)
        self.assertEqual(url,'/microDonation/cause/1/')
    def test_chtocHTML(self):
        response=self.client.get(reverse('show_cause',kwargs={'cause_id': 1}))
        self.assertTemplateUsed(response,'microDonation/cause_detail.html')

class AddToCartTestCase(TestCase):
    def setUp(self):
        testChorg=CharityOrg.objects.create(name="testChorg",description="example",contact_email="test@example.com",paypal_email="test@example.com")
        testCause=Cause.objects.create(name="testCause",description="example",charity=testChorg)
        testChorg.save()
        testCause.save()
        testCartItem=CartItem.objects.create(cart_id="1",value=20,cause=testCause)
        testCartItemTwo=CartItem.objects.create(cart_id="2",value=20,cause=testCause)
        testCartItem.save()
        testCartItemTwo.save()
    def test_updateCartItem(self):
        testChorg=CharityOrg.objects.create(name="testChorg",description="example",contact_email="test@example.com",paypal_email="test@example.com")
        testCause=Cause.objects.create(name="testCause",description="example",charity=testChorg)
        testCartItem=CartItem.objects.create(cart_id="1",value=20,cause=testCause)
        testCartItem.save()
        testCartItem.update_value(30)
        self.assertEqual(testCartItem.value,30)
    def test_buttonAddToCart(self):
        url=reverse('show_cart')
        self.assertEqual(url,'/microDonation/cart/')
    def test_addCartValue(self):
        testChorg=CharityOrg.objects.create(name="testChorg",description="example",contact_email="test@example.com",paypal_email="test@example.com")
        testCause=Cause.objects.create(name="testCause",description="example",charity=testChorg)
        testCartItem=CartItem.objects.create(cart_id="1",value=20,cause=testCause)
        testCartItemTwo=CartItem.objects.create(cart_id="2",value=20,cause=testCause)
        testCartItem.save()
        testCartItemTwo.save()
        testOrder=Order.objects.create(contact_email="test@example.com",date= datetime.date.today,paid=True,address="")
        testOrder.save()
        sum=testCartItem.value+testCartItemTwo.value
        self.assertEqual(sum,40)
    def test_charityCauseMatchUp(self):
        testChorg=CharityOrg.objects.create(name="testChorg",description="example",contact_email="test@example.com",paypal_email="test@example.com")
        testCause=Cause.objects.create(name="testCause",description="example",charity=testChorg)
        testCartItem=CartItem.objects.create(cart_id="1",value=20,cause=testCause)
        testChorg.save()
        testCause.save()
        testCartItem.save()
        url=reverse('show_cart')
        response=self.client.post('/cause/',data={'contact_email':"a@example.com",'paypal_email':"a@example.com"})
        self.assertNotContains(self.client.get(url),"testCHORG:testCAUSE")

class CheckOutPageTestCase(TestCase):
    def test_invalidEmail(self):
        form=CheckoutForm(data={'contact_email':"a",'paypal_email':"a"})
        self.assertFalse(form.is_valid())

class ProcessPaymentPageTestCase(TestCase):
    def test_PPHTMLRedirect(self):
        response=self.client.get(reverse('process_payment'))
        self.assertTrue(response.status_code,200)
        
# Payment Processed or done Test Cases

class PaymentDoneTestCase(TestCase):
    def test_paymentDoneHTML(self):
        response=self.client.get(reverse('payment_done'))
        url=reverse('payment_done')
        self.assertTrue(response.status_code,200)
        self.assertTemplateUsed(response,'microDonation/payment_done.html')

class PaymentCancelledTestCase(TestCase):
    def test_paymentCancelledHTML(self):
        response=self.client.get(reverse('payment_cancelled'))
        url=reverse('payment_cancelled')
        self.assertTrue(response.status_code,200)
        self.assertTemplateUsed(response,'microDonation/payment_cancelled.html')

#Create/Update/Delete Testing

class CreateCharityTestCase(TestCase):
    def test_createCharityHTML(self):
        response=self.client.get(reverse('create_charity'))
        url=reverse('create_charity')
        self.assertTrue(response.status_code,200)
    def test_authorizedCreateCharity(self):
        response=self.client.get(reverse('create_charity'))
        self.assertRedirects(response, '/accounts/login/?next=/microDonation/charity/create/')
        
class UpdateCharityTestCase(TestCase):
    def test_updateCharityHTML(self):
        response=self.client.get(reverse('update_charity',kwargs={'charity_id': 1}))
        url=reverse('update_charity',kwargs={'charity_id': 1})
        self.assertTrue(response.status_code,200)
    def test_authorizedUpdateCharity(self):
        response=self.client.get(reverse('update_charity',kwargs={'charity_id': 1}))
        self.assertRedirects(response, '/accounts/login/?next=/microDonation/charity/1/update/')

class DeleteCharityTestCase(TestCase):
    def test_deleteCharityHTML(self):
        response=self.client.get(reverse('delete_charity',kwargs={'charity_id': 1}))
        url=reverse('delete_charity',kwargs={'charity_id': 1})
        self.assertTrue(response.status_code,200)
    def test_authorizedDeleteCharity(self):
        response=self.client.get(reverse('delete_charity',kwargs={'charity_id': 1}))
        self.assertRedirects(response, '/accounts/login/?next=/microDonation/charity/1/delete/')

class CreateCauseTestCase(TestCase):
    def test_createCauseHTML(self):
        response=self.client.get(reverse('create_cause',kwargs={'charity_id': 1}))
        url=reverse('create_cause',kwargs={'charity_id':1})
        self.assertTrue(response.status_code,200)
    def test_authorizedCreateCause(self):
        response=self.client.get(reverse('create_cause',kwargs={'charity_id':1}))
        self.assertRedirects(response, '/accounts/login/?next=/microDonation/charity/1/create/')
        
class UpdateCauseTestCase(TestCase):
    def test_updateCauseHTML(self):
        response=self.client.get(reverse('update_cause',kwargs={'cause_id': 1}))
        url=reverse('update_cause',kwargs={'cause_id': 1})
        self.assertTrue(response.status_code,200)
    def test_authorizedUpdateCause(self):
        response=self.client.get(reverse('update_cause',kwargs={'cause_id':1}))
        self.assertRedirects(response, '/accounts/login/?next=/microDonation/cause/1/update/')
        
class DeleteCauseTestCase(TestCase):
    def test_deleteCauseHTML(self):
        response=self.client.get(reverse('delete_cause',kwargs={'cause_id': 1}))
        url=reverse('delete_cause',kwargs={'cause_id': 1})
        self.assertTrue(response.status_code,200)
    def test_authorizedDeleteCause(self):
        response=self.client.get(reverse('delete_cause',kwargs={'cause_id':1}))
        self.assertRedirects(response, '/accounts/login/?next=/microDonation/cause/1/delete/')
#Search Charity Testing
class SearchCharityTestCase(TestCase):
    def test_searchCharityHTML(self):
        response=self.client.get(reverse('search_charity'))
        self.assertTrue(response.status_code,200)
        self.assertTemplateUsed(response,'microDonation/charity_search.html')        
        
#Forms Unit Testing

class CartFormValidityTestCase(TestCase):
    def test_validCartForm(self):
        requesto=HttpRequest
        form=CartForm(data={'value':1.00,'cause_id':1},request=requesto)
        self.assertTrue(form.is_valid())
    def test_invalidCartForm(self):
        requesto=HttpRequest
        form=CartForm(data={},request=requesto)
        # void data for CartForm!
        self.assertFalse(form.is_valid())        
        
class CheckoutFormValidityTestCase(TestCase):
    def setUp(self):
        form=CheckoutForm(data={'contact_email':"ex@example.com",'paypal_email':"ex@example.com"})
    def test_InvalidCheckoutForm(self):
        form=CheckoutForm(data={'contact_email':"ex@example.com",'paypal_email':"ex@example.com"})
        self.assertFalse(form.is_valid())
    def test_invalidCheckoutFormTwo(self):
        form=CheckoutForm(data={})
        self.assertFalse(form.is_valid())

class CharityFormValidityTestCase(TestCase):
    def setUp(self):
        form=CharityForm(data={'name':"G226",'description':"Group 2-26 example test",'contact_email':"ex@example.com",'paypal_email':"ex@example.com",'tags':"CS3240"})
    def test_validCharityForm(self):
        you=TaggableManager()
        me=User.objects.create(email="jk4as@virginia.edu",first_name="Jaeun",last_name="Kim",is_staff=True,is_superuser=True,is_active=True)
        form=CharityForm(data={'name':"G226",'description':"Group 2-26 example test",'tags':"no",'contact_email':"ex@example.com",'paypal_email':"ex@example.com",'authenticated_users':{me}})
        self.assertTrue(form.is_valid())
    def test_invalidCharityForm(self):
        form=CharityForm(data={})
        self.assertFalse(form.is_valid())

class CauseFormValidityTestCase(TestCase):
    def setUp(self):
        form=CauseForm(data={'name':"G226",'description':"none",'tags':"one"})
    def test_validCauseForm(self):
        form=CauseForm(data={'name':"G226",'description':"none",'tags':"one"})
        self.assertTrue(form.is_valid())
    def test_invalidCauseForm(self):
        form=CauseForm(data={})
        self.assertFalse(form.is_valid())

class DeleteFormValidityTestCase(TestCase):
    def setUp(self):
        form=DeleteForm(data={})
    def test_validDeleteForm(self):
        form=DeleteForm(data={})
        self.assertTrue(form.is_valid())

class CharitySearchFormVaildityTestCase(TestCase):
    def setUp(self):
        form=CharitySearchForm(data={'name':"Bap", 'charity name':"Sampayan",'min_causes':0, 'at least _ causes':0,'tags':"Sloth", 'containing one or more tags':True})
    def test_invalidCharitySearchForm(self):
        formInv=CharitySearchForm(data={})
        self.assertFalse(formInv.is_valid())
