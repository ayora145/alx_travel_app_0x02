# ALX Travel App 0x02 - Chapa Payment Integration

This project integrates the Chapa Payment Gateway into a Django travel booking system.

## Features
- Secure payment initiation using Chapa API
- Verification of payment status
- Payment tracking model
- Asynchronous email confirmation via Celery
- Sandbox testing environment

## Setup
1. Create a `.env` file with:
```
CHAPA_SECRET_KEY=your_key_here
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Start Celery:
```bash
celery -A alx_travel_app worker --loglevel=info
```

5. Start Django server and test:
```bash
python manage.py runserver
```

## API Endpoints
- `GET /api/listings/` - List all listings
- `POST /api/listings/` - Create new listing
- `GET /api/bookings/` - List all bookings
- `POST /api/bookings/` - Create new booking
- `POST /api/initiate-payment/` - Initiate payment
- `GET /api/verify-payment/` - Verify payment

## Testing
Use Postman to test endpoints at `http://127.0.0.1:8000/api/`