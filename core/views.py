from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from .models import Item, OrderItem, Order, BillingAddress, Payments, Refunds
from .forms import CheckoutForm, RequestRefundForm
from .utils import create_ref_code

import stripe

# Create your views here.

stripe.api_key = settings.STRIPE_SECRET_KEY


class ProductsView(ListView):
    model = Item
    context_object_name = 'items'
    template_name = 'products.html'
    paginate_by = 5


class HomeView(ListView):
    model = Item
    context_object_name = 'items'
    template_name = 'home.html'
    queryset = Item.objects.order_by('-date_added')[:8]


class ProductDetailView(DetailView):
    model = Item
    template_name = "product_detail.html"


class ProfileOrderView(ListView):
    model = Order
    context_object_name = 'orders'
    template_name = 'profile/my_orders.html'

    def get_queryset(self):
        queryset = super(ProfileOrderView, self).get_queryset()
        queryset = queryset.filter(user=self.request.user, ordered=True)
        return queryset


class CartView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
            }
            return render(self.request, "cart.html", context)
        except ObjectDoesNotExist:
            messages.warning(
                self.request, "You do not have an active order !!")
            return redirect('/')


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order,
            }
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.warning(
                self.request, "You do not have an active order !!")
            return redirect('/')

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST)
        try:
            if form.is_valid():
                order = Order.objects.get(
                    user=self.request.user, ordered=False)

                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                street_address = form.cleaned_data['street_address']
                apartment_address = form.cleaned_data['apartment_address']
                country = form.cleaned_data['country']
                state = form.cleaned_data['state']
                pincode = form.cleaned_data['pincode']
                phone = form.cleaned_data['phone']
                payment_options = form.cleaned_data['payment_options']

                billing_address = BillingAddress(
                    user=self.request.user,
                    name=f"{first_name} {last_name}",
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    state=state,
                    pincode=pincode,
                    phone=phone
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                if payment_options == 'S':
                    return redirect('core:payment', payment_method='stripe')
                elif payment_options == 'P':
                    return redirect('core:payment', payment_method='paypal')
                else:
                    return redirect('/')

            messages.error(
                self.request, "Data entered is not valid !! Please try again.")
            return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(
                self.request, "You do not have an active order !!")
            return redirect('core:cart')


class PaymentView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if order.billing_address:
                context = {
                    'order': order,
                }
                return render(self.request, "payment.html", context)
            else:
                messages.error(
                    self.request, "You hadn't added a billing address. Please add one.")
                return redirect('core:checkout')

        except ObjectDoesNotExist:
            messages.warning(
                self.request, "You do not have an active order !!")
            return redirect('/')

    def post(self, *args, **kwargs):
        token = self.request.POST.get('stripeToken')
        order = Order.objects.get(user=self.request.user, ordered=False)

        try:
            charge = stripe.Charge.create(
                amount=int(order.get_cart_price() * 100),
                currency="inr",
                source=token,
            )
            payment = Payments()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_cart_price()
            payment.save()

            # assign the payment to the order

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.status = 'PRO'
            order.save()

            messages.success(
                self.request, "Order placed succesfully. Please check your mail for order details")
            # TODO: Email Invoicing to user
            return redirect('/')

        except stripe.error.CardError as e:
            messages.error(self.request, f"{e.error.message}")
            return redirect('/')

        except stripe.error.RateLimitError as e:
            messages.error(self.request, "Error!! Ratelimit error")
            return redirect('/')

        except stripe.error.InvalidRequestError as e:
            messages.error(self.request, "Error!! Invalid parameters error")
            return redirect('/')

        except stripe.error.AuthenticationError as e:
            messages.error(self.request, "Error!! Not authenticated")
            return redirect('/')

        except stripe.error.APIConnectionError as e:
            messages.error(self.request, "Error!! Can't connect to network")
            return redirect('/')

        except stripe.error.StripeError as e:
            messages.error(
                self.request, "Payment failed. In case of any deduction, the amount will get back to you soon !!")
            return redirect('/')

        except Exception as e:
            # Developer side error needs attention.
            messages.error(
                self.request, "Unexpected problem. Problem will be solved ASAP")
            return redirect('/')


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            if not order_item.quantity >= 6:
                order_item.quantity += 1
                order_item.save()
                messages.info(request, "Item quantity updated.")
            else:
                messages.error(request, "You can't add more than 6 products")
                return redirect('core:cart')
        else:
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.success(request, "Item added to cart")
    return redirect('core:cart')


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:home")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
                order_item.delete()
            messages.info(request, "This item quantity was updated")
            return redirect("core:cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RequestRefundForm()
        context = {
            'form': form
        }
        return render(self.request, 'request_refund.html', context)

    def post(self, *args, **kwargs):
        form = RequestRefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data['ref_code']
            issue = form.cleaned_data['issue']
            issue = dict(form.fields['issue'].choices)[issue]
            issue_description = form.cleaned_data['issue_description']

            try:
                order = Order.objects.get(ref_code=ref_code)
                # checks if the order belongs to that user
                # TODO - Check condition for multiple times refund request for one order
                if order.user == self.request.user:
                    order.refund_requested = True
                    order.save()
                # add refund entry
                    refund = Refunds(
                        order=order,
                        issue=issue,
                        issue_description=issue_description
                    )
                    refund.save()
                    messages.success(self.request, "Your request for refund has been received. Thankyou")
                    return redirect('/')
                else:
                    messages.error(self.request, "You dont have such order. Please check reff code")
                    return redirect('core:request-refund')
            except ObjectDoesNotExist:
                messages.error(self.request, "This order does not exists")
                return redirect('core:request-refund')
        else:
            messages.error(self.request, "Error !! Please input valid details")
            return redirect('/')
