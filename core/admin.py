"""
Remarket Admin - Manage users and items
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Category, Item, Order, Conversation, Message, EmailVerification


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'category', 'price', 'condition', 'location', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('is_active',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'item', 'quantity', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    list_editable = ('status',)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'participant1', 'participant2', 'item', 'created_at')
    list_filter = ('created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'content', 'created_at')
    list_filter = ('created_at',)


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')
    list_filter = ('created_at',)
