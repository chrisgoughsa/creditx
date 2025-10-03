# CreditX

A credit risk assessment and pricing system built with Python 3.13, FastAPI, Polars, and Pydantic.

## Features

- FastAPI web framework for building APIs
- Polars for high-performance data processing
- Pydantic for data validation and serialization
- Comprehensive type checking with mypy
- Code formatting and linting with ruff

## Quickstart

### Prerequisites

- Python 3.13+
- uv package manager

### Installation & Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Start the development server:**
   ```bash
   uv run dev
   ```

3. **Access the API:**
   - API: `http://localhost:8000`
   - Interactive docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/`

### Available Commands

```bash
# Development
uv run dev              # Start development server with hot reload
uv run test             # Run test suite
uv run lint             # Check code formatting and linting
uv run typecheck        # Run type checking with mypy

# Production
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Frontend linting and tests:

```bash
cd frontend
npm run lint
npm run test
```

## Frontend Workspace

The `frontend/` directory ships with a Next.js 14 dashboard for running triage, renewal, and pricing workflows.

```bash
cd frontend
npm install
npm run dev
```

By default the UI targets `http://localhost:8000`. Override via `frontend/.env.local`:

```
NEXT_PUBLIC_CREDITX_API=http://your-api-host
```

## Development Workflow

When contributing changes, create a feature branch from `work` to keep commits scoped and reviewable:

```bash
git checkout work
git pull
git checkout -b feature/my-change
```

After switching to the new branch, stage and commit files with clear, descriptive messages:

```bash
git status
git add README.md
git commit -m "Update development workflow guidance"
```

Once your commits are ready, publish the branch and open a pull request:

```bash
git push -u origin feature/my-change
```

Opening pull requests from topic branches helps maintain a clean history while enabling collaborative reviews.

## API Endpoints

### Health Check
- **GET** `/` - Simple health check endpoint

### Underwriting Triage
- **POST** `/triage/underwriting` - Calculate triage scores for submissions (JSON)
- **POST** `/triage/underwriting/csv` - Upload CSV file for triage scoring

### Renewal Priority
- **POST** `/renewals/priority` - Calculate priority scores for renewals (JSON)
- **POST** `/renewals/priority/csv` - Upload CSV file for renewal priority

### Pricing Suggestions
- **POST** `/pricing/suggest` - Generate pricing suggestions for submissions (JSON)

## API Documentation

### Underwriting Triage

Calculate triage scores (0-1, higher is better) for credit insurance submissions to prioritize underwriting review.

**Endpoint:** `POST /triage/underwriting`

**Request Body:**
```json
{
  "submissions": [
    {
      "submission_id": "SUB-001",
      "broker": "ABC Insurance",
      "sector": "Manufacturing",
      "exposure_limit": 1000000.0,
      "debtor_days": 45.0,
      "financials_attached": true,
      "years_trading": 5.0,
      "broker_hit_rate": 0.85,
      "requested_cov_pct": 0.8,
      "has_judgements": false
    }
  ]
}
```

**Response:**
```json
[
  {
    "id": "SUB-001",
    "score": 0.75,
    "reasons": [
      "Good broker hit rate (0.85)",
      "Financials attached",
      "Reasonable debtor days (45)",
      "No outstanding judgements"
    ]
  }
]
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/triage/underwriting" \
  -H "Content-Type: application/json" \
  -d '{
    "submissions": [
      {
        "submission_id": "SUB-001",
        "broker": "ABC Insurance",
        "sector": "Manufacturing",
        "exposure_limit": 1000000.0,
        "debtor_days": 45.0,
        "financials_attached": true,
        "years_trading": 5.0,
        "broker_hit_rate": 0.85,
        "requested_cov_pct": 0.8,
        "has_judgements": false
      }
    ]
  }'
```

### Renewal Priority

Calculate priority scores (0-1, higher is more urgent) for policy renewals based on expiry dates, utilization rates, and claims history.

**Endpoint:** `POST /renewals/priority`

**Request Body:**
```json
{
  "policies": [
    {
      "policy_id": "POL-001",
      "sector": "Retail",
      "current_premium": 50000.0,
      "limit": 2000000.0,
      "utilization_pct": 0.65,
      "claims_last_24m_cnt": 2,
      "claims_ratio_24m": 0.15,
      "days_to_expiry": 30.0,
      "requested_change_pct": -0.1,
      "broker": "XYZ Brokers"
    }
  ]
}
```

**Response:**
```json
[
  {
    "id": "POL-001",
    "score": 0.9,
    "reasons": [
      "Expires in 30 days (urgent)",
      "High utilization (65%)",
      "Recent claims activity",
      "Requested premium reduction"
    ]
  }
]
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/renewals/priority" \
  -H "Content-Type: application/json" \
  -d '{
    "policies": [
      {
        "policy_id": "POL-001",
        "sector": "Retail",
        "current_premium": 50000.0,
        "limit": 2000000.0,
        "utilization_pct": 0.65,
        "claims_last_24m_cnt": 2,
        "claims_ratio_24m": 0.15,
        "days_to_expiry": 30.0,
        "requested_change_pct": -0.1,
        "broker": "XYZ Brokers"
      }
    ]
  }'
```

### Pricing Suggestions

Generate pricing suggestions with risk bands (A-E) and suggested rates in basis points.

**Endpoint:** `POST /pricing/suggest`

**Request Body:**
```json
{
  "submissions": [
    {
      "submission_id": "SUB-002",
      "broker": "DEF Brokers",
      "sector": "Logistics",
      "exposure_limit": 500000.0,
      "debtor_days": 60.0,
      "financials_attached": true,
      "years_trading": 8.0,
      "broker_hit_rate": 0.92,
      "requested_cov_pct": 0.9,
      "has_judgements": false
    }
  ]
}
```

**Response:**
```json
[
  {
    "id": "SUB-002",
    "band_code": "B",
    "band_label": "201-250 bps",
    "band_description": "Low risk submissions",
    "suggested_rate_bps": 125,
    "base_rate_bps": 100,
    "adjustments": [
      "Sector rate: 100 bps",
      "Broker quality bonus: +15 bps",
      "Financials attached: +10 bps"
    ]
  }
]
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/pricing/suggest" \
  -H "Content-Type: application/json" \
  -d '{
    "submissions": [
      {
        "submission_id": "SUB-002",
        "broker": "DEF Brokers",
        "sector": "Logistics",
        "exposure_limit": 500000.0,
        "debtor_days": 60.0,
        "financials_attached": true,
        "years_trading": 8.0,
        "broker_hit_rate": 0.92,
        "requested_cov_pct": 0.9,
        "has_judgements": false
      }
    ]
  }'
```

### CSV Upload Endpoints

Both triage and renewal endpoints support CSV file uploads for batch processing:

**Triage CSV Upload:**
```bash
curl -X POST "http://localhost:8000/triage/underwriting/csv" \
  -F "file=@sample_data/submissions.csv"
```

**Renewal Priority CSV Upload:**
```bash
curl -X POST "http://localhost:8000/renewals/priority/csv" \
  -F "file=@sample_data/renewals.csv"
```

### Administration
- **POST** `/admin/reload-weights` - Reload weights configuration from `weights.yaml`
- **GET** `/config/current` - Inspect active weights, thresholds, and broker score curves
- **POST** `/policy/check` - Validate sector coverage requests against configured limits

### Feature Importance

Batch responses for triage, renewals, and pricing now include `feature_importance` maps that count how often
each heuristic or adjustment fired. These aggregates help prioritise which drivers influenced the batch results.

## Data Models

### Submission Fields
- `submission_id` (str): Unique submission identifier
- `broker` (str): Broker name
- `sector` (str): Industry sector (Retail, Manufacturing, Logistics, Agri, Services, Other)
- `exposure_limit` (float): Exposure limit in currency units
- `debtor_days` (float): Debtor days (0-180)
- `financials_attached` (bool): Whether financial statements are attached
- `years_trading` (float): Years of trading experience (0-30)
- `broker_hit_rate` (float): Broker success rate (0-1)
- `requested_cov_pct` (float): Requested coverage percentage (0-1)
- `has_judgements` (bool): Whether debtor has outstanding judgements

### Policy Fields
- `policy_id` (str): Unique policy identifier
- `sector` (str): Industry sector
- `current_premium` (float): Current premium in currency units
- `limit` (float): Policy limit in currency units
- `utilization_pct` (float): Utilization percentage (0-1)
- `claims_last_24m_cnt` (int): Claims count in last 24 months
- `claims_ratio_24m` (float): Claims ratio in last 24 months
- `days_to_expiry` (float): Days until policy expiry (0-365)
- `requested_change_pct` (float): Requested premium change percentage
- `broker` (str): Broker name

## Sample Data

The `sample_data/` directory contains example CSV files:
- `submissions.csv` - Sample credit insurance submissions
- `renewals.csv` - Sample policy renewal data

## Important Notice

⚠️ **Policy Governance Disclaimer**

All pricing suggestions and triage scores generated by this system are **indicative only**. Underwriter override always takes precedence and should be used for final decision-making. This system is designed to assist underwriters with data-driven insights but should not replace professional judgment and risk assessment expertise.

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

## Code Quality

This project uses strict but practical code quality tools:

- **ruff**: Fast Python linter and formatter with comprehensive rule set
- **mypy**: Static type checker with strict settings
- **pytest**: Testing framework

All tools are configured in `pyproject.toml` with sensible defaults for a production-ready codebase.
