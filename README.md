# Remarket - Campus Second-hand Trading Platform

A campus second-hand goods trading platform.

## Features (MoSCoW)

### Must
- M1: User registration
- M2: Login/Logout
- M3: Post items (title, description, price, location)
- M4: View orders (purchased/sold)
- M5: Search and filter (keywords, category, price, pagination)
- M6: Place order
- M7: Admin manages users
- M8: Admin manages items

### Should
- S1: Edit/delete own items

### Could
- C1: Item image upload

## Backend Modules

- **Auth**: Registration, login, session, role permissions
- **Item**: Create, update, list, delete items
- **Search**: Keyword and attribute filtering, pagination
- **Order**: Order creation and status updates
- **Admin**: User, item, order management

## Installation & Run

1. Install dependencies: `pip install -r requirements.txt`
2. **If upgrading from old project**: Stop the server, delete `db.sqlite3`, then run migrations
3. Migrate: `python manage.py migrate`
4. Create admin: `python manage.py createsuperuser`
5. Start: `python manage.py runserver`
6. Visit: http://127.0.0.1:8000

## Running Tests

```bash
python manage.py test core
```

Tests cover:
- **Models**: Category, Item, Order, Conversation, EmailVerification
- **Views**: buy_now (purchase flow, item deactivation), update_order_status (seller control, AJAX)
- **API**: chat_api_messages (message list)

## Tech Stack

- Django 5.0
- SQLite
- Bootstrap 5
