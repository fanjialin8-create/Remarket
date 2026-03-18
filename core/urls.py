from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Auth
    path('login/', views.user_login, name='login'),
    path('registration/', views.register, name='customerregistration'),
    path('registration/success/', views.registration_success, name='registration_success'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('logout/', views.user_logout, name='logout'),

    # Profile / Account
    path('profile/', views.profile, name='profile'),
    path('changepassword/', views.change_password, name='changepassword'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Search / Orders
    path('search/', views.search, name='search'),
    path('orders/', views.orders, name='orders'),
    path('orders/api/statuses/', views.orders_api_statuses, name='orders_api_statuses'),
    path('sold-orders/', views.sold_orders, name='sold_orders'),
    path('sold-orders/api/statuses/', views.sold_orders_api_statuses, name='sold_orders_api_statuses'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('orders/<int:order_id>/buyer-action/', views.buyer_order_action, name='buyer_order_action'),

    # Item / Listing
    path('post-item/', views.post_item, name='post_item'),
    path('edit-item/<int:pk>/', views.edit_item, name='edit_item'),
    path('remove-item/<int:pk>/', views.remove_item, name='remove_item'),
    path('product-detail/<int:pk>/', views.item_detail, name='product-detail'),
    path('buy-now/', views.buy_now, name='buy_now'),
    path('category/<slug:slug>/', views.category_items, name='category_items'),

    # Chat
    path('chat/', views.chat_list, name='chat_list'),
    path('chat/start/<int:item_id>/', views.chat_start, name='chat_start'),
    path('chat/<int:conversation_id>/api/messages/', views.chat_api_messages, name='chat_api_messages'),
    path('chat/<int:conversation_id>/', views.chat_detail, name='chat_detail'),

    # Password Reset
    path(
        'password-reset/',
        views.CustomPasswordResetView.as_view(),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='app/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='app/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='app/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]