from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django_countries.fields import CountryField

CATEGORY_CHOICES = (
    ('S', 'Shirt'),
    ('TS', 'T Shirts'),
    ('J', 'Jeans'),
    ('T', 'Trousers')
)

LABEL_CHOICES = (
    ('T', 'Trending'),
    ('HD', 'Hot Deal'),
    ('N', 'New')
)

ORDER_STATUS_CHOICES = (
    ('PRO', 'Processing'),
    ('PKD', 'Packed'),
    ('SHP', 'Shipped'),
    ('DLV', 'Delivered')
)


class Item(models.Model):
    title = models.CharField(max_length=130)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES,
                             max_length=2, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:product', kwargs={
            'slug': self.slug,
        })

    def get_add_to_cart_url(self):
        return reverse('core:add-to-cart', kwargs={
            'slug': self.slug,
        })

    def get_remove_from__cart_url(self):
        return reverse('core:remove-from-cart', kwargs={
            'slug': self.slug,
        })


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE
                             )
    ordered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.slug}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_price(self):
        return self.quantity * self.item.discount_price

    def get_total_saved(self):
        return self.get_total_item_price - self.get_total_discount_price

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    ordered = models.BooleanField(default=False)
    items = models.ManyToManyField(OrderItem)
    order_started = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    billing_address = models.ForeignKey(
        "BillingAddress", on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        "Payments", on_delete=models.SET_NULL, blank=True, null=True)
    status = models.CharField(
        choices=ORDER_STATUS_CHOICES, max_length=3, blank=True, null=True)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_cart_price(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    street_address = models.CharField(max_length=300)
    apartment_address = models.CharField(max_length=300)
    country = CountryField(multiple=False)
    state = models.CharField(max_length=150)
    pincode = models.CharField(max_length=15)
    phone = models.CharField(max_length=30)

    def __str__(self):
        return self.user.username


class Payments(models.Model):
    stripe_charge_id = models.CharField(max_length=60)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Refunds(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    issue = models.CharField(max_length=100)
    issue_description = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.pk}"
