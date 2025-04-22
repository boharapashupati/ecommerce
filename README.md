# E-Commerce Backend API

A robust e-commerce backend API built with Django and Django REST Framework, featuring user authentication, product management, shopping cart, and order processing.

## Features

- User Authentication & Role-Based Access (Admin, Seller, Buyer)
- Product Management with Categories and Filters
- Shopping Cart & Checkout System
- Order Processing & Tracking
- Payment Integration (Stripe)
- Admin Panel for Product & Order Management
- Redis Caching
- Celery Task Management

## Tech Stack

- Backend: Django 5.0.2, Django REST Framework 3.14.0
- Database: PostgreSQL
- Caching: Redis
- Task Queue: Celery
- Payment Processing: Stripe API
- Authentication: Django REST Knox

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a .env file in the root directory with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:password@localhost:5432/ecommerce
REDIS_URL=redis://localhost:6379/0
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Start Celery worker:
```bash
celery -A ecommerce worker -l info
```

## API Documentation

Once the server is running, visit:
- API Documentation: http://localhost:8000/api/docs/
- Admin Panel: http://localhost:8000/admin/

## Project Structure

```
ecommerce/
├── apps/
│   ├── users/          # User management
│   ├── products/       # Product management
│   ├── orders/         # Order processing
│   └── payments/       # Payment integration
├── config/             # Project settings
├── utils/              # Utility functions
└── tasks/              # Celery tasks
``` 