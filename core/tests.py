"""
Unit tests for ReMarket - ITECH implementation requirement.
Covers: models (core business logic), views, API endpoints.
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Category, Item, Order, Conversation, Message, EmailVerification


# ============ Model Tests ============

class CategoryModelTest(TestCase):
    """Test Category model."""

    def test_slug_auto_generated(self):
        cat = Category.objects.create(name='Test Slug Cat')
        self.assertEqual(cat.slug, 'test-slug-cat')

    def test_str_returns_name(self):
        cat = Category.objects.create(name='Test Str Cat')
        self.assertEqual(str(cat), 'Test Str Cat')


class ItemModelTest(TestCase):
    """Test Item model."""

    def setUp(self):
        self.user = User.objects.create_user('seller1', 's@test.com', 'pass123')
        self.category = Category.objects.create(name='Electronics Items')

    def test_item_creation(self):
        item = Item.objects.create(
            title='Test Phone',
            description='A phone',
            price=Decimal('99.99'),
            condition='Good',
            location='Campus',
            category=self.category,
            seller=self.user
        )
        self.assertTrue(item.is_active)
        self.assertEqual(item.title, 'Test Phone')

    def test_item_str(self):
        item = Item.objects.create(
            title='Laptop',
            description='Used laptop',
            price=Decimal('200'),
            condition='Very Good',
            location='Library',
            category=self.category,
            seller=self.user
        )
        self.assertIn('Laptop', str(item))


class OrderModelTest(TestCase):
    """Test Order model and buy/sold logic."""

    def setUp(self):
        self.seller = User.objects.create_user('seller', 's@test.com', 'pass123')
        self.buyer = User.objects.create_user('buyer', 'b@test.com', 'pass123')
        self.category = Category.objects.create(name='Books Order')
        self.item = Item.objects.create(
            title='Textbook',
            description='Math book',
            price=Decimal('20'),
            condition='Good',
            location='Campus',
            category=self.category,
            seller=self.seller
        )

    def test_order_creation(self):
        order = Order.objects.create(buyer=self.buyer, item=self.item, quantity=1)
        self.assertEqual(order.status, 'Pending')
        self.assertEqual(order.quantity, 1)

    def test_order_str(self):
        order = Order.objects.create(buyer=self.buyer, item=self.item)
        self.assertIn('Textbook', str(order))
        self.assertIn('Pending', str(order))


class ConversationModelTest(TestCase):
    """Test Conversation model."""

    def setUp(self):
        self.u1 = User.objects.create_user('user1', 'u1@test.com', 'pass123')
        self.u2 = User.objects.create_user('user2', 'u2@test.com', 'pass123')

    def test_get_other_participant(self):
        conv = Conversation.objects.create(
            participant1=self.u1,
            participant2=self.u2,
            item=None
        )
        self.assertEqual(conv.get_other_participant(self.u1), self.u2)
        self.assertEqual(conv.get_other_participant(self.u2), self.u1)


class EmailVerificationModelTest(TestCase):
    """Test EmailVerification model."""

    def test_generate_token(self):
        token = EmailVerification.generate_token()
        self.assertEqual(len(token), 32)
        self.assertTrue(token.isalnum())


# ============ View Tests ============

class BuyNowViewTest(TestCase):
    """Test buy_now view - core purchase flow."""

    def setUp(self):
        self.client = Client()
        self.seller = User.objects.create_user('seller', 's@test.com', 'pass123')
        self.buyer = User.objects.create_user('buyer', 'b@test.com', 'pass123')
        self.category = Category.objects.create(name='Electronics Buy')
        self.item = Item.objects.create(
            title='Phone',
            description='Used phone',
            price=Decimal('50'),
            condition='Good',
            location='Campus',
            category=self.category,
            seller=self.seller,
            is_active=True
        )

    def test_buy_now_requires_login(self):
        response = self.client.post(reverse('buy_now'), {'product_id': self.item.id})
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_buy_now_deactivates_item(self):
        self.client.force_login(self.buyer)
        response = self.client.post(reverse('buy_now'), {'product_id': self.item.id})
        self.assertEqual(response.status_code, 302)
        self.item.refresh_from_db()
        self.assertFalse(self.item.is_active)

    def test_buy_now_creates_order(self):
        self.client.force_login(self.buyer)
        self.client.post(reverse('buy_now'), {'product_id': self.item.id})
        self.assertEqual(Order.objects.filter(buyer=self.buyer, item=self.item).count(), 1)

    def test_cannot_buy_own_item(self):
        self.client.force_login(self.seller)
        response = self.client.post(reverse('buy_now'), {'product_id': self.item.id})
        self.assertEqual(response.status_code, 302)
        self.item.refresh_from_db()
        self.assertTrue(self.item.is_active)

    def test_cannot_buy_sold_item(self):
        self.item.is_active = False
        self.item.save()
        self.client.force_login(self.buyer)
        response = self.client.post(reverse('buy_now'), {'product_id': self.item.id})
        self.assertRedirects(response, reverse('home'))


class UpdateOrderStatusViewTest(TestCase):
    """Test update_order_status view."""

    def setUp(self):
        self.client = Client()
        self.seller = User.objects.create_user('seller', 's@test.com', 'pass123')
        self.buyer = User.objects.create_user('buyer', 'b@test.com', 'pass123')
        self.category = Category.objects.create(name='Books Status')
        self.item = Item.objects.create(
            title='Book',
            description='A book',
            price=Decimal('10'),
            condition='Good',
            location='Campus',
            category=self.category,
            seller=self.seller,
            is_active=False
        )
        self.order = Order.objects.create(
            buyer=self.buyer,
            item=self.item,
            quantity=1,
            status='Pending'
        )

    def test_seller_can_update_status(self):
        self.client.force_login(self.seller)
        url = reverse('update_order_status', args=[self.order.id])
        response = self.client.post(url, {'status': 'Confirmed'})
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'Confirmed')

    def test_cancelled_restores_item(self):
        self.client.force_login(self.seller)
        url = reverse('update_order_status', args=[self.order.id])
        self.client.post(url, {'status': 'Cancelled'})
        self.item.refresh_from_db()
        self.assertTrue(self.item.is_active)

    def test_ajax_returns_json(self):
        self.client.force_login(self.seller)
        url = reverse('update_order_status', args=[self.order.id])
        response = self.client.post(
            url,
            {'status': 'Completed'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'Completed')


class ChatApiMessagesViewTest(TestCase):
    """Test chat_api_messages API endpoint."""

    def setUp(self):
        self.client = Client()
        self.u1 = User.objects.create_user('user1', 'u1@test.com', 'pass123')
        self.u2 = User.objects.create_user('user2', 'u2@test.com', 'pass123')
        self.category = Category.objects.create(name='Books Chat')
        self.item = Item.objects.create(
            title='Item',
            description='Desc',
            price=Decimal('5'),
            condition='Good',
            location='Campus',
            category=self.category,
            seller=self.u1
        )
        self.conv = Conversation.objects.create(
            participant1=self.u1,
            participant2=self.u2,
            item=self.item
        )
        Message.objects.create(conversation=self.conv, sender=self.u1, content='Hello')

    def test_api_returns_messages(self):
        self.client.force_login(self.u1)
        url = reverse('chat_api_messages', args=[self.conv.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('messages', data)
        self.assertEqual(len(data['messages']), 1)
        self.assertEqual(data['messages'][0]['content'], 'Hello')
