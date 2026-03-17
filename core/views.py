"""
Remarket Backend Views
Modules: Auth, Item, Search, Order, Admin
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.contrib.messages import get_messages
from django.core.mail import send_mail
from django.conf import settings

from .models import Category, Item, ItemImage, Order, Conversation, Message, EmailVerification
from .forms import RegistrationForm, LoginForm, ItemForm, CustomPasswordResetForm


# ============ Auth Module ============

def register(request):
    """User registration with email verification"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            token = EmailVerification.generate_token()
            EmailVerification.objects.create(user=user, token=token)

            verify_url = request.build_absolute_uri(
                reverse('verify_email', args=[token])
            )
            try:
                send_mail(
                    subject='Verify your ReMarket account',
                    message=(
                        f'Hello {user.username},\n\n'
                        f'Please click the link below to verify your email and activate your account:\n\n'
                        f'{verify_url}\n\n'
                        f'If you did not create this account, please ignore this email.\n\n'
                        f'ReMarket Team'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@remarket.local',
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                storage = get_messages(request)
                for _ in storage:
                    pass

                messages.success(
                    request,
                    'Registration successful. Please check your email to verify your account.',
                    extra_tags='register_msg'
                )
            except Exception:
                storage = get_messages(request)
                for _ in storage:
                    pass

                messages.warning(
                    request,
                    'Registration successful, but we could not send the verification email. '
                    'Please use "Resend verification email" on the next page to try again.',
                    extra_tags='register_msg'
                )

            return redirect('registration_success')
        else:
            messages.error(
                request,
                'Registration failed. Please check your input.',
                extra_tags='register_msg'
            )
    else:
        form = RegistrationForm()

    return render(request, 'app/customerregistration.html', {'form': form})

def registration_success(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'app/registration_success.html')


def resend_verification(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip()
        user = User.objects.filter(email__iexact=email, is_active=False).first()
        if not user:
            messages.info(request, 'No unverified account found for this email, or the account is already verified.')
            return redirect('login')

        verification = EmailVerification.objects.filter(user=user).first()
        if not verification:
            messages.error(request, 'Verification record not found. Please register again.')
            return redirect('customerregistration')

        verify_url = request.build_absolute_uri(reverse('verify_email', args=[verification.token]))
        try:
            send_mail(
                subject='Verify your ReMarket account',
                message=(
                    f'Hello {user.username},\n\n'
                    f'Please click the link below to verify your email:\n\n'
                    f'{verify_url}\n\n'
                    f'ReMarket Team'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@remarket.local',
                recipient_list=[user.email],
                fail_silently=False,
            )
            messages.success(request, 'Verification email sent. Please check your inbox.')
        except Exception:
            messages.error(request, 'Could not send email. Please check your email configuration.')

        return redirect('login')

    return render(request, 'app/resend_verification.html')


class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'app/password_reset.html'
    email_template_name = 'app/password_reset_email.html'
    subject_template_name = 'app/password_reset_subject.txt'
    form_class = CustomPasswordResetForm

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception:
            form.add_error(None, 'Could not send the reset email. Please try again later.')
            return self.form_invalid(form)


def verify_email(request, token):
    if request.user.is_authenticated:
        return redirect('home')

    verification = EmailVerification.objects.filter(token=token).select_related('user').first()
    if not verification:
        messages.error(request, 'Invalid or expired verification link.')
        return redirect('login')

    user = verification.user
    user.is_active = True
    user.save()
    verification.delete()

    messages.success(request, 'Email verified successfully! You can now log in.')
    return redirect('login')


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                try:
                    u = User.objects.get(username=username)
                    if not u.is_active:
                        messages.error(request, 'Please verify your email before logging in. Check your inbox for the verification link.')
                    else:
                        messages.error(request, 'Invalid username or password.')
                except User.DoesNotExist:
                    messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'app/login.html', {'form': form})


@login_required(login_url='/login/')
def user_logout(request):
    logout(request)
    return redirect('home')


# ============ Item Module ============

@login_required(login_url='/login/')
def post_item(request):
    """Post item with multiple images"""
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        images = request.FILES.getlist('images')

        if form.is_valid():
            if not images:
                messages.error(request, 'Please upload at least one product image.')
                return render(request, 'app/post_item.html', {'form': form})

            item = form.save(commit=False)
            item.seller = request.user
            item.save()

            for img in images:
                ItemImage.objects.create(item=item, image=img)

            messages.success(request, 'Item posted successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please check your input.')
    else:
        form = ItemForm()

    return render(request, 'app/post_item.html', {
        'form': form,
        'categories': Category.objects.all()
    })


@login_required(login_url='/login/')
def edit_item(request, pk):
    """Edit own item and optionally add more images"""
    item = get_object_or_404(Item, pk=pk)
    if item.seller != request.user:
        return HttpResponseForbidden('You do not have permission to edit this item')

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        form.fields['images'].required = False
        images = request.FILES.getlist('images')

        if form.is_valid():
            form.save()

            for img in images:
                ItemImage.objects.create(item=item, image=img)

            messages.success(request, 'Item updated successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please check your input.')
    else:
        form = ItemForm(instance=item)
        form.fields['images'].required = False

    return render(request, 'app/edit_item.html', {
        'form': form,
        'item': item
    })


@login_required(login_url='/login/')
def remove_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.seller != request.user:
        return HttpResponseForbidden('You do not have permission to delete this item')
    item.delete()
    messages.success(request, 'Item deleted successfully.')
    return redirect('dashboard')


def item_detail(request, pk):
    """Pass the actual item object to the template for multi-image display"""
    item = get_object_or_404(
        Item.objects.select_related('category', 'seller').prefetch_related('images'),
        pk=pk,
        is_active=True
    )
    return render(request, 'app/productdetail.html', {
        'product': item,
        'product_cart': False
    })


# ============ Search Module ============

def search(request):
    query = ''
    if request.method == 'POST':
        query = (request.POST.get('search') or '').strip()
    else:
        query = request.GET.get('q', '').strip()

    items = Item.objects.filter(is_active=True).select_related('category', 'seller').prefetch_related('images')
    if query:
        items = items.filter(Q(title__icontains=query) | Q(description__icontains=query))

    products = [_product_wrapper(i) for i in items]
    return render(request, 'app/search.html', {'products': products, 'query': query})


# ============ Order Module ============

@login_required(login_url='/login/')
def add_to_cart(request):
    product_id = request.GET.get('product_id')
    if product_id:
        return redirect('place_order', item_id=product_id)
    return redirect('home')


@login_required(login_url='/login/')
def buy_now(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        if not product_id:
            messages.error(request, 'No product selected.')
            return redirect('home')

        try:
            item = Item.objects.get(id=product_id, is_active=True)
        except Item.DoesNotExist:
            messages.error(request, 'Item not found.')
            return redirect('home')

        if item.seller == request.user:
            messages.error(request, 'Cannot buy your own item.')
            return redirect('product-detail', pk=product_id)

        Order.objects.create(
            buyer=request.user,
            item=item,
            quantity=1,
            status='Pending'
        )

        messages.success(request, 'Order placed successfully.')
        return redirect('orders')

    return redirect('home')


@login_required(login_url='/login/')
def view_cart(request):
    return redirect('orders')


@login_required(login_url='/login/')
def profile(request):
    context = {
        'user': request.user,
    }
    return render(request, 'app/profile.html', context)


@login_required(login_url='/login/')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.', extra_tags='password_msg')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.', extra_tags='password_msg')
        elif len(new_password) < 8:
            messages.error(request, 'New password must be at least 8 characters long.', extra_tags='password_msg')
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password updated successfully.', extra_tags='password_msg')
            return redirect('profile')

    return redirect('profile')


@login_required(login_url='/login/')
def place_order(request, item_id):
    item = get_object_or_404(Item, pk=item_id, is_active=True)
    if item.seller == request.user:
        messages.error(request, 'Cannot buy your own item.')
        return redirect('product-detail', pk=item_id)

    quantity = int(request.POST.get('quantity', 1) or request.GET.get('quantity', 1))
    if quantity < 1:
        quantity = 1

    Order.objects.create(buyer=request.user, item=item, quantity=quantity)
    messages.success(request, 'Order placed.')
    return redirect('orders')


@login_required(login_url='/login/')
def orders(request):
    bought = Order.objects.filter(buyer=request.user).select_related('item', 'item__seller').prefetch_related('item__images')
    orders_list = []
    for o in bought:
        orders_list.append(type('OrderRow', (), {
            'product': _product_wrapper(o.item),
            'quantity': o.quantity,
            'price': str(o.item.price * o.quantity),
            'ordered_date': o.created_at,
            'status': o.status
        })())
    return render(request, 'app/orders.html', {'orders': orders_list})


@login_required(login_url='/login/')
def update_order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if order.item.seller != request.user and not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission')
    new_status = request.POST.get('status')
    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()
        messages.success(request, 'Order status updated.')
    return redirect('orders')


# ============ User Dashboard ============

@login_required(login_url='/login/')
def dashboard(request):
    my_items = Item.objects.filter(seller=request.user, is_active=True).prefetch_related('images')
    orders_bought = Order.objects.filter(buyer=request.user).select_related('item')[:5]
    orders_sold = Order.objects.filter(item__seller=request.user).select_related('buyer', 'item')[:5]
    context = {
        'my_items': my_items,
        'orders_bought': orders_bought,
        'orders_sold': orders_sold,
    }
    return render(request, 'app/dashboard.html', context)


# ============ Home ============

def _product_wrapper(item):
    img = item.primary_image if item.primary_image else type('Img', (), {'url': '/static/app/img/placeholder.png'})()
    return type('Product', (), {
        'id': item.id,
        'title': item.title,
        'price': item.price,
        'image': img,
        'condition': item.condition,
        'location': item.location,
        'seller': item.seller,
        'created_at': item.created_at,
        'category': item.category,
    })()


def home(request):
    base = Item.objects.filter(is_active=True).select_related('category', 'seller').prefetch_related('images')

    mobile = list(base.filter(category__slug='electronics')[:8]) or list(base[:8])
    electronics = list(base.filter(category__slug='electronics')[:8]) or list(base[:8])
    books = list(base.filter(category__slug='books')[:8]) or list(base[:8])
    cloth = list(base.filter(category__slug='clothing')[:8]) or list(base[:8])
    accessorie = list(base.filter(category__slug='daily')[:8]) or list(base[:8])

    mobile = [_product_wrapper(i) for i in mobile]
    electronics = [_product_wrapper(i) for i in electronics]
    books = [_product_wrapper(i) for i in books]
    cloth = [_product_wrapper(i) for i in cloth]
    accessorie = [_product_wrapper(i) for i in accessorie]

    return render(request, 'app/home.html', {
        'mobile': mobile,
        'electronics': electronics,
        'books': books,
        'cloth': cloth,
        'accessorie': accessorie,
        'banners': []
    })


def category_items(request, slug):
    category = get_object_or_404(Category, slug=slug)
    items = Item.objects.filter(category=category, is_active=True).select_related('seller', 'category').prefetch_related('images').order_by('-created_at')

    return render(request, 'app/category_items.html', {
        'category': category,
        'items': items,
    })


# ============ Admin Module ============

@staff_member_required
def admin_dashboard(request):
    users_count = User.objects.count()
    items_count = Item.objects.filter(is_active=True).count()
    orders_count = Order.objects.count()
    context = {
        'users_count': users_count,
        'items_count': items_count,
        'orders_count': orders_count,
    }
    return render(request, 'app/admin_dashboard.html', context)


@staff_member_required
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'app/admin_users.html', {'users': users})


@staff_member_required
def admin_items(request):
    items = Item.objects.all().select_related('seller', 'category').prefetch_related('images').order_by('-created_at')
    return render(request, 'app/admin_items.html', {'items': items})


@staff_member_required
def admin_orders(request):
    orders = Order.objects.all().select_related('buyer', 'item', 'item__seller').order_by('-created_at')
    return render(request, 'app/admin_orders.html', {'orders': orders})


@staff_member_required
def admin_disable_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = False
    user.save()
    messages.success(request, f'User {user.username} has been disabled.')
    return redirect('admin_users')


@staff_member_required
def admin_remove_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    item.is_active = False
    item.save()
    messages.success(request, f'Item "{item.title}" has been deactivated.')
    return redirect('admin_items')


# ============ Chat Module ============

@login_required(login_url='/login/')
def chat_list(request):
    convs = Conversation.objects.filter(
        Q(participant1=request.user) | Q(participant2=request.user)
    ).select_related('participant1', 'participant2', 'item').prefetch_related('messages').order_by('-updated_at')

    conv_list = []
    for c in convs:
        last_msg = c.messages.last()
        other = c.get_other_participant(request.user)
        conv_list.append({'conversation': c, 'other': other, 'last_message': last_msg})
    return render(request, 'app/chat_list.html', {'conversations': conv_list})


@login_required(login_url='/login/')
def chat_start(request, item_id):
    item = get_object_or_404(Item, pk=item_id, is_active=True)
    seller = item.seller
    if request.user == seller:
        messages.error(request, 'Cannot chat with yourself.')
        return redirect('product-detail', pk=item_id)

    conv = Conversation.objects.filter(
        Q(participant1=request.user, participant2=seller, item=item) |
        Q(participant1=seller, participant2=request.user, item=item)
    ).first()

    if not conv:
        conv = Conversation.objects.create(participant1=request.user, participant2=seller, item=item)

    return redirect('chat_detail', conversation_id=conv.id)


@login_required(login_url='/login/')
def chat_detail(request, conversation_id):
    conv = get_object_or_404(Conversation, pk=conversation_id)
    if request.user not in (conv.participant1, conv.participant2):
        return HttpResponseForbidden('You do not have permission to view this conversation')

    msg_list = conv.messages.select_related('sender').all()

    if request.method == 'POST':
        content = (request.POST.get('content') or '').strip()
        if content:
            Message.objects.create(conversation=conv, sender=request.user, content=content)
            conv.save()
            return redirect('chat_detail', conversation_id=conv.id)

    other = conv.get_other_participant(request.user)
    return render(request, 'app/chat_detail.html', {
        'conversation': conv,
        'messages': msg_list,
        'other': other,
    })


@login_required(login_url='/login/')
def chat_api_messages(request, conversation_id):
    from django.http import JsonResponse

    conv = get_object_or_404(Conversation, pk=conversation_id)
    if request.user not in (conv.participant1, conv.participant2):
        return JsonResponse({'error': 'Forbidden'}, status=403)

    msg_list = conv.messages.select_related('sender').order_by('created_at')
    data = [{
        'id': m.id,
        'sender': m.sender.username,
        'content': m.content,
        'created_at': m.created_at.isoformat(),
    } for m in msg_list]

    return JsonResponse({'messages': data})