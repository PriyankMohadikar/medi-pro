"""Quick test: List + Create custom packages via the API (no external deps)."""
import urllib.request
import json

BASE = "http://localhost:8000/api/custom-packages"

def api_get(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, json.loads(resp.read().decode())

def api_post(url, data):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

def api_delete(url):
    req = urllib.request.Request(url, method="DELETE")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

# 1. List packages
print("=== GET /api/custom-packages ===")
status, data = api_get(BASE)
print(f"Status: {status}")
print(f"Packages count: {len(data)}")
print()

# 2. Create a test package
print("=== POST /api/custom-packages ===")
payload = {
    "package_name": "Test Wellness Package",
    "total_tests": 2,
    "individual_total_price": 500,
    "discount_percentage": 10,
    "suggested_package_price": 450,
    "market_average_price": 480,
    "expected_customer_savings": 50,
    "tests": [
        {"test_name": "CBC", "individual_price": 200, "display_order": 0},
        {"test_name": "Lipid Profile", "individual_price": 300, "display_order": 1},
    ],
}
status2, data2 = api_post(BASE, payload)
print(f"Status: {status2}")
print(f"Response: {json.dumps(data2, indent=2)}")
print()

# 3. List again to verify
print("=== GET /api/custom-packages (after create) ===")
status3, data3 = api_get(BASE)
print(f"Status: {status3}")
print(f"Total packages: {len(data3)}")
if data3:
    print(f"First package: {data3[0]['package_name']}")
print()

# 4. Cleanup - delete the test package
if status2 == 201:
    pkg_id = data2["package_id"]
    print(f"=== DELETE /api/custom-packages/{pkg_id} ===")
    status4, data4 = api_delete(f"{BASE}/{pkg_id}")
    print(f"Status: {status4}")
    print(f"Response: {data4}")

print("\n=== ALL TESTS PASSED ===" if status2 == 201 else "\n=== TESTS FAILED ===")
