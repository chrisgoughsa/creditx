# CreditX

A credit risk assessment and pricing system built with Python 3.13, FastAPI, Polars, and Pydantic.

## Features

- FastAPI web framework for building APIs
- Polars for high-performance data processing
- Pydantic for data validation and serialization
- Comprehensive type checking with mypy
- Code formatting and linting with ruff

## Project Structure

```
creditx/
├── app/                    # Main application code
│   ├── __init__.py
│   ├── main.py            # FastAPI application entry point
│   ├── models.py          # Pydantic models
│   ├── service.py         # Business logic services
│   ├── features.py        # Feature engineering
│   ├── pricing.py         # Pricing algorithms
│   └── data_cache.py      # Data caching utilities
├── tests/                  # Test suite
│   ├── test_pricing.py
│   └── test_triage.py
├── sample_data/           # Sample datasets
│   ├── submissions.csv
│   └── renewals.csv
├── pyproject.toml         # Project configuration
└── README.md
```

## Development

### Prerequisites

- Python 3.13+
- uv package manager

### Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate     # On Windows
   ```

### Available Scripts

- `uv run dev` - Start the development server with hot reload
- `uv run test` - Run the test suite
- `uv run lint` - Check code formatting and linting
- `uv run typecheck` - Run type checking with mypy

### Development Server

Start the FastAPI development server:

```bash
uv run dev
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## Code Quality

This project uses strict but practical code quality tools:

- **ruff**: Fast Python linter and formatter with comprehensive rule set
- **mypy**: Static type checker with strict settings
- **pytest**: Testing framework

All tools are configured in `pyproject.toml` with sensible defaults for a production-ready codebase.
