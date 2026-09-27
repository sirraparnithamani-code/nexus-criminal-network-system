import os
import json
import urllib.request
import urllib.parse

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("=" * 60)
    print("NEXUS INVESTIGATION INTELLIGENCE SYSTEM - INTEGRATION TESTS")
    print("=" * 60)

    # 1. Health check
    req = urllib.request.Request(f"{BASE_URL}/api/health")
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        data = json.loads(response.read().decode())
        print(f"[TEST 1] System Health: OK (Document Processor: {data['services']['document_processor']})")

    # 2. Login
    login_data = json.dumps({"username": "investigator", "password": "password123"}).encode()
    req = urllib.request.Request(f"{BASE_URL}/api/auth/login", data=login_data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        data = json.loads(response.read().decode())
        print(f"[TEST 2] Authentication: OK (User: {data['user']['name']}, Role: {data['user']['role']})")

    # 3. Dashboard Stats
    req = urllib.request.Request(f"{BASE_URL}/api/dashboard/stats")
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        data = json.loads(response.read().decode())
        print(f"[TEST 3] Dashboard Stats: OK (Active Cases: {data['activeCases']}, Entities: {data['keyEntities']}, Alerts: {data['alerts']})")

    # 4. Cases API
    req = urllib.request.Request(f"{BASE_URL}/api/cases")
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        data = json.loads(response.read().decode())
        assert len(data['cases']) >= 4
        print(f"[TEST 4] Cases Listing: OK ({len(data['cases'])} cases retrieved)")

    # 5. Create Case
    new_case_data = json.dumps({
        "title": "Automated Test Dossier",
        "description": "Integration test case for verification",
        "priority": "HIGH"
    }).encode()
    req = urllib.request.Request(f"{BASE_URL}/api/cases", data=new_case_data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        data = json.loads(response.read().decode())
        print(f"[TEST 5] Create Case: OK (Created ID: {data['case']['id']})")

    # 6. Graph API
    req = urllib.request.Request(f"{BASE_URL}/api/graph")
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        data = json.loads(response.read().decode())
        assert len(data['nodes']) > 0
        assert len(data['links']) > 0
        print(f"[TEST 6] Investigation Graph: OK ({len(data['nodes'])} nodes, {len(data['links'])} relationships)")

    # 7. Timeline API
    req = urllib.request.Request(f"{BASE_URL}/api/timeline")
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        data = json.loads(response.read().decode())
        assert len(data['timeline']) > 0
        print(f"[TEST 7] Case Timeline: OK ({len(data['timeline'])} chronological events mapped)")

    # 8. Search API
    q = urllib.parse.quote("Rahul")
    req = urllib.request.Request(f"{BASE_URL}/api/search?q={q}&category=All")
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        data = json.loads(response.read().decode())
        assert len(data['results']) > 0
        print(f"[TEST 8] Intelligence Search: OK ({len(data['results'])} matches for 'Rahul')")

    # 9. Investigation Summary
    req = urllib.request.Request(f"{BASE_URL}/api/investigation/summary")
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        data = json.loads(response.read().decode())
        print(f"[TEST 9] Investigation Summary & AI Report: OK ({data['keyEntitiesCount']} entities, {data['clustersCount']} clusters)")

    print("=" * 60)
    print("ALL 9 CORE NEXUS SYSTEM TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
