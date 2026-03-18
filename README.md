# ReMarket - Campus Second-hand Trading Platform

A campus second-hand goods trading platform where users can buy, sell, and chat directly.

## Features (MoSCoW)

### Must
- M1: User registration with email verification
- M2: Login/Logout
- M3: Post items (title, description, price, location, condition, images)
- M4: View orders (bought / sold) with status sync
- M5: Search and filter (keywords, category)
- M6: Place order
- M7: Admin manages users
- M8: Admin manages items

### Should
- S1: Edit/delete own items
- S2: Chat between buyer and seller
- S3: Order status flow: Pending → Delivered → Completed (buyer confirms)

### Could
- C1: Multiple images per item
- C2: Item condition (Like New, Very Good, Good, Fair)

## Order Flow

- **Seller**: Pending → Delivered (marks shipped) → Completed (when buyer confirms)
- **Buyer**: When status is Delivered, can choose:
  - **Confirm received** → Order becomes Completed (both sides sync)
  - **Not received** → Order becomes Cancelled, item relisted
- Status updates sync in real-time via polling (both buyer and seller pages)

## Backend Modules

- **Auth**: Registration with email verification, login, session, role permissions
- **Item**: Create, update, list, delete items; multi-image upload; condition
- **Search**: Keyword and category filtering
- **Order**: Order creation, seller status (Delivered), buyer actions (confirm/report)
- **Chat**: Direct messaging between buyer and seller per item
- **Admin**: User, item, order management

## Installation & Run

1. Install dependencies: `pip install -r requirements.txt`
2. **If upgrading**: Stop the server, delete `db.sqlite3`, then run migrations
3. Migrate: `python manage.py migrate`
4. Create admin: `python manage.py createsuperuser`
5. Start: `python manage.py runserver`
6. Visit: http://127.0.0.1:8000

## Deploy on PythonAnywhere

1. Clone the repo and set up a virtualenv
2. Add your domain to `ALLOWED_HOSTS` in `Commerce/settings.py`
3. Set `STATIC_ROOT` and run `python manage.py collectstatic`
4. Configure WSGI to point to your project
5. Reload the web app

## Running Tests

```bash
python manage.py test core
```

Tests cover:
- **Models**: Category, Item, Order, Conversation, EmailVerification
- **Views**: buy_now, update_order_status, buyer_order_action
- **API**: chat_api_messages, orders_api_statuses

## Tech Stack

- Django 5.0
- SQLite
- Bootstrap 5
- Pillow (image upload)
