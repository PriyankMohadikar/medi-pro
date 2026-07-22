"""Validate the new API responses after catalog expansion."""
import urllib.request
import json

BASE = "http://localhost:8000/api"

print("=== Validation: GET /api/stats ===")
req = urllib.request.Request(f"{BASE}/stats")
with urllib.request.urlopen(req, timeout=10) as resp:
    stats = json.loads(resp.read().decode())
    print(f"Total Tests: {stats['total_tests']}")
    print("Categories:")
    for c in stats['categories']:
        if c in ['Hormones', 'Nutrition', 'Cardiology', 'Consultation', 'Additional Services']:
            print(f"  - [NEW] {c}")
        else:
            print(f"  - {c}")

print("\n=== Validation: GET /api/tests ===")
req2 = urllib.request.Request(f"{BASE}/tests")
with urllib.request.urlopen(req2, timeout=10) as resp:
    data = json.loads(resp.read().decode())
    tests = data # It's a list directly
    print(f"Fetched {len(tests)} tests total.")
    
    # Check for the new tests
    new_names = ['Testosterone', 'Prolactin', 'LH (Luteinizing Hormone)', 'Iron Profile', 'ECG', 'Doctor Consultation', 'Breakfast']
    found = {n: False for n in new_names}
    for t in tests:
        if t['test_name'] in found:
            found[t['test_name']] = True
            
    print("\nNew items presence:")
    for n, is_found in found.items():
        print(f"  {n}: {'[OK]' if is_found else '[MISSING]'}")

