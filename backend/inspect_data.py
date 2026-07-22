"""Inspect existing data to understand structure for new catalog items."""
import json
from sqlalchemy import func
from config import load_settings
from database import get_engine, get_session_factory
from models import Provider, TestPricing

settings = load_settings()
engine = get_engine(settings)
Session = get_session_factory(engine)
session = Session()

# 1. Show ES Healthcare providers
print("=== ES Healthcare Providers ===")
es_providers = session.query(Provider).filter(Provider.provider_name == "ES Healthcare").all()
for p in es_providers:
    print(f"  ID={p.provider_id}, Name={p.provider_name}, City={p.city}, Type={p.provider_type}")

# 2. Show all categories
print("\n=== All Categories ===")
cats = session.query(TestPricing.category).distinct().order_by(TestPricing.category).all()
for c in cats:
    print(f"  {c[0]}")

# 3. Show sample tests for ES Healthcare (first 10)
print("\n=== Sample ES Healthcare Tests (first 15) ===")
if es_providers:
    es_id = es_providers[0].provider_id
    tests = session.query(TestPricing).filter(TestPricing.provider_id == es_id).order_by(TestPricing.test_name).limit(15).all()
    for t in tests:
        print(f"  {t.test_name} | Category={t.category} | Price={t.price}")

# 4. Check if any of the new tests already exist
print("\n=== Check if new tests already exist ===")
new_tests = ["Testosterone", "Prolactin", "LH (Luteinizing Hormone)", "Iron Profile", "ECG", "Doctor Consultation", "Breakfast"]
for name in new_tests:
    exists = session.query(TestPricing).filter(TestPricing.test_name == name).first()
    print(f"  {name}: {'EXISTS' if exists else 'NOT FOUND'}")

# 5. Count total tests
total = session.query(func.count(TestPricing.pricing_id)).scalar()
print(f"\n=== Total Test Pricing Rows: {total} ===")

# 6. Show all cities
print("\n=== All Cities ===")
cities = session.query(Provider.city).distinct().order_by(Provider.city).all()
for c in cities:
    print(f"  {c[0]}")

session.close()
