"""
Remarket - Campus Second-hand Trading Platform
ER Model: User, Item, Order, Category
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class EmailVerification(models.Model):
    """Email verification token for registration"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Verification for {self.user.email}"

    @staticmethod
    def generate_token():
        return uuid.uuid4().hex


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Item(models.Model):
    CONDITION_CHOICES = [
        ('Like New', 'Like New'),
        ('Very Good', 'Very Good'),
        ('Good', 'Good'),
        ('Fair', 'Fair'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES)
    location = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @property
    def primary_image(self):
        first = self.images.first()
        return first.image if first else None

    @property
    def image(self):
        """
        Compatibility for old templates that still use product.image.url
        """
        return self.primary_image


class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='items/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.item.title}"


class Order(models.Model):
    """Order: purchase transaction linking buyer to item"""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_bought')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.buyer.username} - {self.item.title} ({self.status})"


class Conversation(models.Model):
    """Chat conversation between buyer and seller about an item"""
    participant1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_p1')
    participant2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_p2')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.participant1.username} & {self.participant2.username} - {self.item.title if self.item else 'Direct'}"

    def get_other_participant(self, user):
        return self.participant2 if user == self.participant1 else self.participant1


class Message(models.Model):
    """Chat message"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}..."