import os

from datetime import date, datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

import plata
from plata.contact.models import Contact
from plata.product.models import TaxClass, Product, ProductVariation, Discount,\
    ProductPrice, OptionGroup, Option
from plata.product.stock.models import Period, StockTransaction
from plata.shop.models import Order, OrderStatus, OrderPayment

from plata.tests.base import PlataTest, get_request


class AdminTest(PlataTest):
    def setUp(self):
        u = User.objects.create_user('admin', 'admin@example.com', 'password')
        u.is_staff = True
        u.is_superuser = True
        u.save()

    def login(self):
        self.client.login(username='admin', password='password')

    def test_01_products(self):
        self.login()

        tax_class = TaxClass.objects.create(
            name='Standard Swiss Tax Rate',
            rate=Decimal('7.60'),
            )

        self.client.post('/admin/product/optiongroup/add/', {
            'name': 'size',

            'options-INITIAL_FORMS': 0,
            'options-MAX_NUM_FORMS': '',
            'options-TOTAL_FORMS': 2,

            'options-0-name': 'S',
            'options-0-value': 's',
            'options-0-ordering': 10,

            'options-1-name': 'M',
            'options-1-value': 'm',
            'options-1-ordering': 20,
            })

        self.client.post('/admin/product/optiongroup/add/', {
            'name': 'color',

            'options-INITIAL_FORMS': 0,
            'options-MAX_NUM_FORMS': '',
            'options-TOTAL_FORMS': 2,

            'options-0-name': 'red',
            'options-0-value': 'red',
            'options-0-ordering': 10,

            'options-1-name': 'blue',
            'options-1-value': 'blue',
            'options-1-ordering': 20,
            })

        product_data = {
            'description': '',
            'images-INITIAL_FORMS': '0',
            'images-MAX_NUM_FORMS': '',
            'images-TOTAL_FORMS': '0',
            'is_active': 'on',
            'name': 'Product 3',
            'slug': '324wregft5re',
            'ordering': '100',
            'sku': '324wregft5re',
            'option_groups': [1,2],

            'prices-0-id': '',
            'prices-0-product': '',

            'prices-0-_unit_price': '79.90',
            'prices-0-currency': 'CHF',
            'prices-0-is_active': 'on',
            'prices-0-tax_class': '1',
            'prices-0-tax_included': 'on',
            'prices-0-valid_from': '2010-05-19',
            'prices-0-valid_until': '',

            'prices-INITIAL_FORMS': '0',
            'prices-MAX_NUM_FORMS': '',
            'prices-TOTAL_FORMS': '1',

            'rawcontent-INITIAL_FORMS': '0',
            'rawcontent-MAX_NUM_FORMS': '',
            'rawcontent-TOTAL_FORMS': '0',

            'variations-INITIAL_FORMS': '0',
            'variations-MAX_NUM_FORMS': '',
            'variations-TOTAL_FORMS': '0',
            }

        self.client.post('/admin/product/product/add/', product_data)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(ProductVariation.objects.count(), 4)
        self.assertEqual(ProductPrice.objects.count(), 1)
        self.assertEqual(OptionGroup.objects.count(), 2)
        self.assertEqual(Option.objects.count(), 4)

        product_data['slug'] += '-'
        product_data['sku'] += '-'
        self.client.post('/admin/product/product/add/', product_data)
        self.client.post('/admin/product/product/add/', product_data)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(ProductVariation.objects.count(), 8)
        self.assertEqual(ProductPrice.objects.count(), 2)
        self.assertEqual(OptionGroup.objects.count(), 2)
        self.assertEqual(Option.objects.count(), 4)

        product_data.update({
            'variations-0-id': '5',
            'variations-0-product': '2',

            'variations-0-is_active': 'on',
            'variations-0-items_in_stock': '0',
            'variations-0-ordering': '0',
            'variations-0-options': [1, 3],

            'variations-1-id': '6',
            'variations-1-product': '2',

            'variations-1-is_active': 'on',
            'variations-1-items_in_stock': '0',
            'variations-1-ordering': '0',
            'variations-1-options': [1, 4],

            'variations-2-id': '7',
            'variations-2-product': '2',

            'variations-2-is_active': 'on',
            'variations-2-items_in_stock': '0',
            'variations-2-ordering': '0',
            'variations-2-options': [2, 3],

            'variations-3-id': '8',
            'variations-3-product': '2',

            'variations-3-is_active': 'on',
            'variations-3-items_in_stock': '0',
            'variations-3-ordering': '0',
            'variations-3-options': [2, 4],

            'variations-INITIAL_FORMS': '4',
            'variations-MAX_NUM_FORMS': '',
            'variations-TOTAL_FORMS': '4',
            })

        self.assertRedirects(self.client.post('/admin/product/product/2/', product_data),
            '/admin/product/product/')

        product_data.update({
            'variations-0-sku': '324wregft5re-0',
            'variations-1-sku': '324wregft5re-1',
            'variations-2-sku': '324wregft5re-2',
            'variations-3-sku': '324wregft5re-3',
            })

        self.assertRedirects(self.client.post('/admin/product/product/2/', product_data),
            '/admin/product/product/')

        product_data['variations-0-options'] = [1, 4]
        self.assertContains(self.client.post('/admin/product/product/2/', product_data),
            'Combination of options already encountered')
        product_data['variations-0-options'] = [1, 3]

        p = Product.objects.get(pk=2)
        options = list(OptionGroup.objects.all())
        p.option_groups.remove(options[1])

        self.assertEqual(p.option_groups.count(), 1)

        self.assertContains(self.client.post('/admin/product/product/2/', product_data),
            'Please select options from the following groups')

        product_data['variations-0-options'] = [1, 2]
        self.assertContains(self.client.post('/admin/product/product/2/', product_data),
            'Please select options from the following groups')
        self.assertContains(self.client.post('/admin/product/product/2/', product_data),
            'Only one option per group allowed')
