# CreditX Frontend

A modern Next.js 14 dashboard for interacting with the CreditX underwriting, renewal, and pricing APIs.

## Getting started

1. Install dependencies (Node.js 20+ recommended):
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server (ensure the FastAPI backend is running on `http://localhost:8000`):
   ```bash
   npm run dev
   ```

3. Configure the API base URL if needed via `.env.local`:
   ```bash
   NEXT_PUBLIC_CREDITX_API=http://localhost:8000
   ```

## Features

- Underwriting triage workspace with manual entry and CSV uploads
- Renewal priority scoring with policy builder and CSV ingestion
- Pricing studio for indicative rate suggestions and adjustment breakdowns
- Responsive design with Tailwind CSS, React Query, and Zod validation

## Scripts

- `npm run dev` – start Next.js in development mode
- `npm run build` – production build
- `npm run start` – run the production build locally
- `npm run lint` – lint with Next.js ESLint configuration
