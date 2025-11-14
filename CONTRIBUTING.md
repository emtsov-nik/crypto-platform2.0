# Contributing to Crypto Trading Platform

Thank you for your interest in contributing to the Crypto Trading Platform! This document provides guidelines and instructions for contributing.

## =Ë Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Project Structure](#project-structure)
- [Resources](#resources)

## =Ü Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## =€ Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git
- Basic understanding of trading concepts
- Familiarity with FastAPI and React

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
```bash
git clone https://github.com/YOUR_USERNAME/crypto-trading-platform.git
cd crypto-trading-platform
```

3. Add upstream remote:
```bash
git remote add upstream https://github.com/emtsov-nik/crypto-trading-platform.git
```

## =» Development Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install pytest pytest-cov black flake8 isort mypy

# Set up pre-commit hooks
pip install pre-commit
pre-commit install
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Install dev dependencies
npm install --save-dev @types/node @types/react
```

### Database Setup

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Run migrations (if applicable)
cd backend
alembic upgrade head
```

### Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your test credentials
# Use Binance Testnet for development!
```

## > How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/emtsov-nik/crypto-trading-platform/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Detailed description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots (if applicable)
   - Environment details (OS, Python version, etc.)

### Suggesting Features

1. Check [Discussions](https://github.com/emtsov-nik/crypto-trading-platform/discussions) for similar suggestions
2. Create a new discussion with:
   - Clear feature description
   - Use case and motivation
   - Possible implementation approach
   - Examples (if applicable)

### Contributing Code

1. **Find an issue** to work on or create one
2. **Comment** on the issue to let others know you're working on it
3. **Create a branch** for your work:
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

4. **Make your changes** following our coding standards
5. **Write tests** for your changes
6. **Run tests** to ensure everything works
7. **Commit your changes** with clear commit messages
8. **Push** to your fork
9. **Create a Pull Request**

## =Ý Coding Standards

### Python (Backend)

#### Code Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use [Black](https://github.com/psf/black) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Use [flake8](https://flake8.pycqa.org/) for linting

```bash
# Format code
black app/

# Sort imports
isort app/

# Check linting
flake8 app/
```

#### Type Hints

- Use type hints for all function signatures
- Use `Optional[]` for nullable types
- Use `Union[]` for multiple types

```python
def calculate_position_size(
    capital: float,
    price: float,
    risk_percent: float = 1.0
) -> float:
    """Calculate position size based on capital and risk."""
    return (capital * risk_percent / 100) / price
```

#### Documentation

- Write docstrings for all public functions/classes
- Use Google-style docstrings

```python
def generate_signal(df: pd.DataFrame, index: int) -> str:
    """Generate trading signal based on indicators.

    Args:
        df: DataFrame with OHLCV data and indicators
        index: Current candle index

    Returns:
        Signal: 'long', 'short', 'close', or None

    Raises:
        ValueError: If dataframe is invalid
    """
    pass
```

### TypeScript/React (Frontend)

#### Code Style

- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use functional components with hooks
- Use TypeScript for type safety

```typescript
interface Strategy {
  id: number
  name: string
  params: Record<string, any>
}

const StrategyList: React.FC = () => {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  // ...
}
```

#### Component Structure

```tsx
// Imports
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'

// Types/Interfaces
interface Props {
  strategyId: number
}

// Component
export default function StrategyDetails({ strategyId }: Props) {
  // State
  const [selected, setSelected] = useState(false)

  // Queries/Mutations
  const { data, isLoading } = useQuery(...)

  // Effects
  useEffect(() => {...}, [])

  // Handlers
  const handleClick = () => {...}

  // Render
  return <div>...</div>
}
```

## >ê Testing Guidelines

### Writing Tests

#### Backend Tests

```python
import pytest

@pytest.mark.unit
@pytest.mark.strategy
class TestMyStrategy:
    def test_signal_generation(self, sample_strategy):
        """Test that strategy generates correct signals."""
        signal = sample_strategy.generate_signal(df, index)
        assert signal in ['long', 'short', 'close', None]

    def test_position_sizing(self, sample_strategy):
        """Test position size calculation."""
        size = sample_strategy.calculate_position_size(10000, 40000)
        assert size > 0
        assert size < 1
```

#### Frontend Tests

```typescript
import { render, screen } from '@testing-library/react'
import { StrategyList } from './StrategyList'

describe('StrategyList', () => {
  it('renders strategy list', () => {
    render(<StrategyList />)
    expect(screen.getByText('Strategies')).toBeInTheDocument()
  })

  it('loads strategies on mount', async () => {
    render(<StrategyList />)
    await waitFor(() => {
      expect(screen.getByText('RSI Strategy')).toBeInTheDocument()
    })
  })
})
```

### Running Tests

```bash
# Backend tests
cd backend
pytest                          # All tests
pytest tests/unit              # Unit tests only
pytest -m strategy             # Strategy tests only
pytest --cov=app              # With coverage

# Frontend tests
cd frontend
npm test                       # All tests
npm test -- --coverage        # With coverage
```

### Test Coverage

- Aim for > 80% overall coverage
- Critical modules (strategies, backtest, safety) should have > 90%
- All new features must include tests
- All bug fixes must include regression tests

## = Pull Request Process

### Before Submitting

1. **Update your branch** with latest upstream:
```bash
git fetch upstream
git rebase upstream/main
```

2. **Run all tests** and ensure they pass:
```bash
cd backend && pytest
cd frontend && npm test
```

3. **Run linters** and fix any issues:
```bash
cd backend
black app/
isort app/
flake8 app/

cd frontend
npm run lint
```

4. **Update documentation** if needed

5. **Add tests** for new features

### Submitting PR

1. **Push to your fork**:
```bash
git push origin feature/your-feature-name
```

2. **Create Pull Request** on GitHub with:
   - Clear, descriptive title
   - Detailed description of changes
   - Link to related issue(s)
   - Screenshots (if UI changes)
   - Checklist of completed items

3. **PR Template**:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Changes Made
- Change 1
- Change 2

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots here]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests pass locally
- [ ] No new warnings generated
```

### Review Process

1. **Automated checks** will run (tests, linting, etc.)
2. **Code review** by maintainers
3. **Address feedback** and push updates
4. **Approval** and merge by maintainers

## =Ý Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding/updating tests
- **chore**: Maintenance tasks

### Examples

```bash
feat(strategies): add MACD strategy

Implement MACD crossover strategy with configurable parameters.
Includes signal generation and position sizing logic.

Closes #42
```

```bash
fix(backtest): correct PnL calculation for short positions

Fix PnL calculation that was showing incorrect values
for short positions. Added regression tests.

Fixes #58
```

```bash
docs(readme): update installation instructions

Add detailed steps for Windows users and troubleshooting section.
```

## =Á Project Structure

```
crypto-trading-platform/
   backend/
      app/
         api/              # API endpoints (add new endpoints here)
         models/           # Database models
         schemas/          # Pydantic schemas
         services/         # Business logic
         strategies/       # Trading strategies (add new strategies here)
         backtesting/      # Backtest engine
         trading/          # Live trading
      telegram_bot/         # Telegram bot
      tests/                # Tests (add tests for new features)
   frontend/
      src/
         components/       # React components
         pages/            # Pages (add new pages here)
         services/         # API client
         types/            # TypeScript types
   docs/                     # Documentation
   .github/workflows/        # CI/CD
```

## <“ Resources

### Documentation

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Pandas Docs](https://pandas.pydata.org/docs/)
- [ccxt Docs](https://docs.ccxt.com/)

### Trading Concepts

- [Technical Analysis Basics](https://www.investopedia.com/terms/t/technicalanalysis.asp)
- [Risk Management](https://www.investopedia.com/terms/r/riskmanagement.asp)
- [Backtesting](https://www.investopedia.com/terms/b/backtesting.asp)

### Project Resources

- [GitHub Issues](https://github.com/emtsov-nik/crypto-trading-platform/issues)
- [GitHub Discussions](https://github.com/emtsov-nik/crypto-trading-platform/discussions)
- [Project Wiki](https://github.com/emtsov-nik/crypto-trading-platform/wiki)

## =O Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes
- Project documentation

Thank you for contributing to the Crypto Trading Platform! =€

## =Þ Questions?

- Create a [Discussion](https://github.com/emtsov-nik/crypto-trading-platform/discussions)
- Join our [Telegram Community](https://t.me/your_community)
- Email: support@example.com

---

**Happy Contributing! <‰**
