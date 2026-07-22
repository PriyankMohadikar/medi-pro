# 🚀 Supabase PostgreSQL Setup & Data Seeding Guide

This guide details how to host your MediPrice Pro PostgreSQL database on **Supabase** and migrate all tables and dataset records.

---

## Step 1: Create a Supabase Project

1. Log in or sign up at [Supabase.com](https://supabase.com/).
2. Click **New Project** and select your organization.
3. Enter your project details:
   - **Name**: `mediprice-pro` (or your preferred name)
   - **Database Password**: Set a strong password (save this securely!).
   - **Region**: Choose the region closest to your server/users.
4. Wait for your Supabase project to finish provisioning (~1–2 minutes).

---

## Step 2: Retrieve your Supabase Connection String

1. In your Supabase Dashboard, go to **Project Settings** (gear icon) → **Database**.
2. Scroll down to **Connection String**.
3. Select **URI** (or **Transaction Pooler** / **Session Pooler**).
4. Copy your connection URL. It will look like one of the following:

   **Direct Connection (Port 5432):**
   ```text
   postgresql://postgres.[project-ref]:[YOUR-PASSWORD]@db.[project-ref].supabase.co:5432/postgres
   ```

   **Pooler Connection (Port 6543 / Recommended for Serverless/Cloud):**
   ```text
   postgresql://postgres.[project-ref]:[YOUR-PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres?sslmode=require
   ```

---

## Step 3: Configure `backend/.env`

Open your `backend/.env` file and set the `DATABASE_URL` variable:

```env
# Supabase PostgreSQL Connection
DATABASE_URL=postgresql://postgres.[project-ref]:[YOUR-PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres?sslmode=require

# AI Provider Configuration
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

> [!TIP]
> `backend/config.py` automatically detects `DATABASE_URL` and uses it for SQLAlchemy database operations.

---

## Step 4: Create Tables and Seed Data to Supabase

Run the main ETL script to automatically create all tables (`providers`, `test_pricing`, `package_pricing`, `package_tests`, `custom_packages`, `custom_package_tests`) and seed all data into your Supabase database:

```bash
cd backend
python main.py
```

### What happens when you run `python main.py`:
1. Connects securely to your Supabase PostgreSQL instance.
2. Creates all ORM schema tables using `CREATE TABLE IF NOT EXISTS`.
3. Reads `dataset_web.xlsx`.
4. Normalizes providers, test pricing, and package pricing records.
5. Populates Supabase PostgreSQL with all records in a single transaction.

---

## Step 5: Verify Database on Supabase Dashboard

1. Open your Supabase Dashboard → **Table Editor**.
2. You will see all tables populated:
   - `providers`
   - `test_pricing`
   - `package_pricing`
   - `package_tests`
   - `custom_packages`
   - `custom_package_tests`

---

## Step 6: Start MediPrice Pro API Server

```bash
python start.py
```

Your FastAPI backend will now connect to Supabase PostgreSQL for all pricing calculations, search, package intelligence, and AI queries!
