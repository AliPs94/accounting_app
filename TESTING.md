# Testing Guide for Accounting Application

This document provides comprehensive information about testing the accounting application, including both backend (Django) and frontend (Vue.js) components.

## Overview

The application includes a comprehensive test suite covering:
- **Backend**: Django models, serializers, views, and API endpoints
- **Frontend**: Vue components, services, stores, and user interactions
- **Integration**: End-to-end testing scenarios

## Test Structure

```
├── accounting/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py          # Model tests
│   │   ├── test_serializers.py     # Serializer tests
│   │   └── test_views.py           # View/API tests
│   └── tests.py                    # Basic tests
├── frontend/
│   └── src/
│       └── test/
│           ├── setup.ts            # Test setup
│           ├── mocks/              # Mock data
│           ├── utils/              # Test utilities
│           ├── services/           # Service tests
│           ├── views/              # View tests
│           └── components/         # Component tests
├── run_tests.py                    # Test runner script
└── pytest.ini                     # Pytest configuration
```

## Prerequisites

### Backend Dependencies
```bash
pip install -r requirements.txt
```

### Frontend Dependencies
```bash
cd frontend
npm install
```

## Running Tests

### Quick Start
```bash
# Run all tests with coverage
python run_tests.py

# Install dependencies and run tests
python run_tests.py --install-deps

# Run only backend tests
python run_tests.py --backend-only

# Run only frontend tests
python run_tests.py --frontend-only

# Run without coverage
python run_tests.py --no-coverage
```

### Backend Tests

#### Using pytest (Recommended)
```bash
# Run all backend tests
python -m pytest accounting/tests/ accounting/tests.py

# Run with coverage
python -m pytest --cov=accounting --cov-report=html accounting/tests/

# Run specific test file
python -m pytest accounting/tests/test_models.py

# Run specific test
python -m pytest accounting/tests/test_models.py::TestAssociation::test_create_association

# Run with verbose output
python -m pytest -v accounting/tests/
```

#### Using Django's test runner
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounting

# Run specific test
python manage.py test accounting.tests.ModelTestCase
```

### Frontend Tests

#### Using npm scripts
```bash
cd frontend

# Run all tests
npm run test

# Run with coverage
npm run test:coverage

# Run with UI
npm run test:ui

# Run specific test file
npm run test src/test/services/apiService.test.ts

# Run in watch mode
npm run test -- --watch
```

#### Using vitest directly
```bash
cd frontend

# Run all tests
npx vitest

# Run with coverage
npx vitest --coverage

# Run specific test
npx vitest src/test/services/apiService.test.ts
```

## Test Categories

### Backend Tests

#### Model Tests (`test_models.py`)
- **Association**: Creation, validation, ordering
- **UserProfile**: User-association relationships, constraints
- **Account**: Account creation, parent-child relationships, validation
- **Voucher**: Voucher creation, balance validation, calculations
- **VoucherDetail**: Detail creation, validation rules
- **DefaultAccountTemplate**: Template creation, hierarchy

#### Serializer Tests (`test_serializers.py`)
- **AssociationSerializer**: Serialization/deserialization
- **UserProfileSerializer**: Profile data handling
- **AccountSerializer**: Account data, validation, relationships
- **VoucherSerializer**: Voucher creation, balance validation
- **VoucherDetailSerializer**: Detail validation, constraints
- **DefaultAccountTemplateSerializer**: Template handling

#### View Tests (`test_views.py`)
- **AssociationViewSet**: CRUD operations, permissions
- **AccountViewSet**: Account management, filtering, hierarchy
- **VoucherViewSet**: Voucher operations, date filtering, trial balance
- **VoucherDetailViewSet**: Detail management, validation
- **DefaultAccountTemplateViewSet**: Template application

### Frontend Tests

#### Service Tests (`apiService.test.ts`)
- **Authentication**: Login, token management, profile
- **Associations**: CRUD operations, selection
- **Accounts**: Account management, filtering, hierarchy
- **Vouchers**: Voucher operations, filtering, trial balance
- **Reports**: Report generation, data handling
- **Interceptors**: Token refresh, error handling

#### Component Tests
- **ReportsView**: Report generation, data display, user interactions
- **Navigation**: Navigation logic, authentication state
- **Forms**: Form validation, data handling

#### Store Tests (`counter.test.ts`)
- **State Management**: Store operations, state updates
- **Actions**: Action dispatching, side effects
- **Getters**: Computed values, derived state

## Test Data and Mocking

### Backend Mocking
- **Factory Boy**: Test data generation
- **Faker**: Realistic test data
- **Django Test Client**: API testing

### Frontend Mocking
- **MSW (Mock Service Worker)**: API mocking
- **Vue Test Utils**: Component testing
- **Vitest**: Test runner and mocking

## Coverage Reports

### Backend Coverage
- **HTML Report**: `htmlcov/index.html`
- **Terminal Report**: Shows missing lines
- **Coverage Threshold**: 80% minimum

### Frontend Coverage
- **HTML Report**: `frontend/coverage/index.html`
- **Terminal Report**: Shows missing lines
- **Coverage Threshold**: 80% minimum

## Best Practices

### Writing Tests
1. **Test Naming**: Use descriptive names that explain what is being tested
2. **Arrange-Act-Assert**: Structure tests clearly
3. **One Assertion**: One assertion per test when possible
4. **Independent Tests**: Tests should not depend on each other
5. **Clean Setup**: Use setUp/tearDown methods appropriately

### Test Data
1. **Realistic Data**: Use realistic test data
2. **Edge Cases**: Test boundary conditions
3. **Error Scenarios**: Test error handling
4. **Validation**: Test all validation rules

### Performance
1. **Fast Tests**: Keep tests fast and focused
2. **Database**: Use test database for backend tests
3. **Mocking**: Mock external dependencies
4. **Parallel**: Run tests in parallel when possible

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.12
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          cd frontend && npm install
      - name: Run tests
        run: python run_tests.py
```

## Troubleshooting

### Common Issues

#### Backend Tests
1. **Database Issues**: Ensure test database is properly configured
2. **Migration Issues**: Run migrations before tests
3. **Import Errors**: Check Python path and imports
4. **Authentication**: Ensure JWT tokens are properly configured

#### Frontend Tests
1. **Node Modules**: Ensure all dependencies are installed
2. **TypeScript**: Check TypeScript configuration
3. **Vue Router**: Mock router properly in tests
4. **API Mocking**: Ensure MSW handlers are properly configured

### Debugging Tests
```bash
# Backend debugging
python -m pytest -v -s accounting/tests/test_models.py::TestAssociation::test_create_association

# Frontend debugging
cd frontend
npm run test -- --reporter=verbose src/test/services/apiService.test.ts
```

## Test Maintenance

### Regular Tasks
1. **Update Dependencies**: Keep test dependencies up to date
2. **Review Coverage**: Ensure coverage remains high
3. **Refactor Tests**: Keep tests maintainable
4. **Add New Tests**: Add tests for new features

### Monitoring
1. **Coverage Reports**: Monitor coverage trends
2. **Test Performance**: Monitor test execution time
3. **Flaky Tests**: Identify and fix flaky tests
4. **Test Quality**: Review test quality regularly

## Resources

- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Vue Testing](https://vuejs.org/guide/scaling-up/testing.html)
- [Vitest Documentation](https://vitest.dev/)
- [Pytest Documentation](https://docs.pytest.org/)
- [MSW Documentation](https://mswjs.io/)

## Contributing

When adding new features:
1. **Write Tests First**: Follow TDD principles
2. **Test Coverage**: Ensure adequate test coverage
3. **Documentation**: Update this guide if needed
4. **Review**: Have tests reviewed with code

## Support

For testing issues:
1. Check this guide first
2. Review test output and error messages
3. Check dependencies and configuration
4. Ask for help in the development team
