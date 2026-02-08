# SmartQuote - B2B Online Quotation & Ordering System

A comprehensive B2B quotation and ordering system with role-based access control, sophisticated pricing engine, and ERP integration.

## Features

- **Role-Based Access Control**: Super Admin, Admin, Sales, Client roles
- **3-Tier Pricing System**: Base prices (X, S, A) with client-specific overrides
- **Low-Price Protection**: Intelligent batch price updates that protect negotiated rates
- **Inventory Sync**: Integration with Lingxing ERP (mock API)
- **Complete Workflow**: PI generation → Payment confirmation → Stock locking
- **Audit Trail**: Complete price change history

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 14+
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose)

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: Ant Design
- **State Management**: React Context + Hooks

## Project Structure

```
smartquote/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── api/            # API routes
│   │   ├── services/       # Business logic
│   │   ├── middleware/     # Auth & RBAC
│   │   └── main.py         # Application entry
│   ├── migrations/         # Alembic migrations
│   ├── tests/              # Backend tests
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   └── services/       # API services
│   └── package.json
└── docs/                   # Documentation
    ├── database_schema.md
    └── schema.sql
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup

1. **Create database**:
   ```bash
   createdb smartquote
   ```

2. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

5. **Start server**:
   ```bash
   uvicorn app.main:app --reload
   ```

   API will be available at: http://localhost:8000
   API docs: http://localhost:8000/docs

### Frontend Setup

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

   Frontend will be available at: http://localhost:5173

## Database Schema

The system uses 14 tables organized into functional areas:

- **Authentication**: `roles`, `users`
- **Clients**: `clients`
- **Products**: `products`
- **Pricing**: `base_prices`, `client_prices`, `price_history`
- **Inventory**: `inventory`
- **Quotations**: `quotations`, `quotation_items`
- **Orders**: `orders`, `order_items`, `payments`, `stock_locks`

See [docs/database_schema.md](docs/database_schema.md) for detailed schema documentation.

## Key Business Logic

### Pricing Engine

The system implements a sophisticated 3-tier pricing model:

1. **Base Prices**: Every product has prices for tiers X, S, and A
2. **Client Overrides**: Clients can have custom negotiated prices
3. **Low-Price Protection**: When base prices change, client prices are only updated if they are higher than the new base price

### Order Workflow

1. Sales creates quotation
2. System generates Proforma Invoice (PI)
3. Admin manually confirms payment
4. System locks stock in inventory
5. Order is processed and fulfilled

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

## Development

### Running Tests

```bash
cd backend
pytest
```

### Creating Migrations

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## License

Proprietary - All rights reserved

## Support

For questions or issues, contact the development team.
