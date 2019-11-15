from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import format_html

from .models import Item, Order, OrderItem, Payments, BillingAddress, Refunds
# Register your models here.


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granded'


def linkify(field_name):
    """
    Converts a foreign key value into clickable links.

    If field_name is 'parent', link text will be str(obj.parent)
    Link will be admin url for the admin url for obj.parent.id:change
    """

    def _linkify(obj):
        if obj.ordered and obj is not None:
            app_label = obj._meta.app_label
            linked_obj = getattr(obj, field_name)
            model_name = linked_obj._meta.model_name
            view_name = f"admin:{app_label}_{model_name}_change"
            link_url = reverse(view_name, args=[linked_obj.pk])
            return format_html('<a href="{}">{}</a>', link_url, linked_obj)
        else:
            return 'Nill'

    _linkify.short_description = field_name  # Sets column name
    return _linkify


class OrderAdmin(admin.ModelAdmin):

    list_display = ['user', 'ordered', 'status',
                    'refund_requested', 'refund_granted', linkify(field_name="billing_address"), linkify(field_name="payment"), ]

    # list_display_links = ['user', 'billing_address', 'payment']

    list_filter = ['ordered', 'status',
                   'refund_requested', 'refund_granted']

    search_fields = ['user__username', 'ref_code']

    actions = [make_refund_accepted]


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payments)
admin.site.register(Refunds)
admin.site.register(BillingAddress)
