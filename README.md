# Multi-Tenant Accounting Web Application

A comprehensive accounting system built with Django REST Framework backend and Vue.js frontend, designed for small associations with multi-tenant support.

## Features

- **Multi-tenant Architecture**: Each association has isolated data
- **Chart of Accounts**: Hierarchical account structure with support for sub-accounts
- **Journal Entries**: Double-entry bookkeeping with voucher system
- **Financial Reports**: Trial balance, income statement, and balance sheet generation
- **User Management**: JWT-based authentication with role-based access
- **API-First Design**: RESTful API with comprehensive endpoints

## Technology Stack

### Backend
- **Django 5.2.6**: Web framework
- **Django REST Framework**: API development
- **PostgreSQL**: Database
- **JWT Authentication**: Secure token-based auth
- **Python 3.12+**: Programming language

### Frontend (Coming Soon)
- **Vue.js 3**: Frontend framework
- **Vue Router**: Client-side routing
- **Axios**: HTTP client
- **Vuetify**: Material Design components

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 12+
- Node.js 16+ (for frontend)

### Backend Setup

1. **Clone and setup virtual environment**:
   ```bash
   cd /Users/alijay/Documents/Account
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Database Setup**:
   ```bash
   # Create PostgreSQL database
   createdb accounting_db
   
   # Run migrations
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create sample data**:
   ```bash
   python manage.py setup_sample_data
   ```

4. **Start development server**:
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/`

### API Endpoints

#### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `GET /api/auth/profile/` - Get user profile
- `POST /api/token/` - Get JWT token
- `POST /api/token/refresh/` - Refresh JWT token

#### Core Resources
- `GET /api/associations/` - List associations
- `GET /api/accounts/` - List chart of accounts
- `GET /api/vouchers/` - List journal vouchers
- `GET /api/voucher-details/` - List voucher details

#### Special Endpoints
- `GET /api/accounts/by_type/?type=Asset` - Filter accounts by type
- `GET /api/accounts/hierarchy/` - Get hierarchical account structure
- `GET /api/vouchers/by_date_range/?start_date=2024-01-01&end_date=2024-12-31` - Filter vouchers by date range
- `GET /api/vouchers/{id}/trial_balance/` - Get trial balance for voucher

### Sample Data

The setup command creates:
- **Sample Association**: "Sample Association"
- **Admin User**: username: `admin`, password: `admin123`
- **Chart of Accounts**: Complete set of standard accounts (Assets, Liabilities, Equity, Revenue, Expenses)

### Database Models

#### Association
- Represents each tenant organization
- Fields: name, created_at, updated_at

#### UserProfile
- Links users to associations for multi-tenancy
- Fields: user, association, created_at

#### Account
- Chart of accounts with hierarchical structure
- Fields: association, name, account_type, parent, code, is_active

#### Voucher
- Journal entry header
- Fields: association, date, description, voucher_type, voucher_number, created_by

#### VoucherDetail
- Individual debit/credit lines
- Fields: voucher, account, debit, credit, description

### Multi-Tenancy

The application implements multi-tenancy through:
- **Data Isolation**: All queries are filtered by user's association
- **User Profiles**: Each user is linked to exactly one association
- **API Security**: All endpoints enforce association-based access control

### Development

#### Running Tests
```bash
python manage.py test
```

#### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Django Admin
Access the admin interface at `http://localhost:8000/admin/` with the admin user credentials.

## Next Steps

1. **Frontend Development**: Vue.js SPA with modern UI
2. **Financial Reports**: Income statement and balance sheet generation
3. **Advanced Features**: Budgeting, reporting, and analytics
4. **Deployment**: Docker containerization and cloud deployment

## API Documentation

The API follows RESTful conventions and includes:
- Comprehensive serializers with nested relationships
- Pagination for large datasets
- Filtering and search capabilities
- Detailed error handling and validation
- JWT-based authentication

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

