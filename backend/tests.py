import os
from pathlib import Path
TEST_DB = Path(__file__).with_name("test_route53.db")
if TEST_DB.exists(): TEST_DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def login():
    response = client.post("/api/auth/login", json={"email": "demo@route53.local", "password": "Route53Demo123"})
    assert response.status_code == 200
    return response.json()["token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_protected_routes_require_auth():
    response = client.get("/api/hosted-zones")
    assert response.status_code == 401


def test_login_session_and_logout():
    token = login()
    assert client.get("/api/auth/session", headers=auth(token)).status_code == 200
    assert client.post("/api/auth/logout", headers=auth(token)).status_code == 200
    assert client.get("/api/auth/session", headers=auth(token)).status_code == 401


def test_hosted_zone_crud_and_persistence():
    token = login()
    headers = auth(token)
    response = client.post("/api/hosted-zones", headers=headers, json={"name": "crud-test.example", "description": "test", "zone_type": "Public"})
    assert response.status_code == 201
    zone = response.json()
    zone_id = zone["id"]
    assert client.get(f"/api/hosted-zones/{zone_id}", headers=headers).status_code == 200
    assert client.put(f"/api/hosted-zones/{zone_id}", headers=headers, json={"name": "updated.example", "description": "updated", "zone_type": "Private"}).status_code == 200
    assert client.delete(f"/api/hosted-zones/{zone_id}", headers=headers).status_code == 200
    assert client.get(f"/api/hosted-zones/{zone_id}", headers=headers).status_code == 404


def test_dns_record_types_and_validation():
    token = login()
    headers = auth(token)
    zone = client.post("/api/hosted-zones", headers=headers, json={"name": "records-test.example", "zone_type": "Public"}).json()
    zone_id = zone["id"]
    valid = {
        "A": "192.0.2.10", "AAAA": "2001:db8::10", "CNAME": "target.example.com",
        "TXT": '"hello"', "MX": "10 mail.example.com", "NS": "ns1.example.com",
        "PTR": "ptr.example.com", "SRV": "10 5 443 service.example.com", "CAA": "0 issue \"letsencrypt.org\"",
    }
    for record_type, value in valid.items():
        response = client.post(f"/api/hosted-zones/{zone_id}/records", headers=headers, json={"name": f"{record_type.lower()}.example.com", "type": record_type, "ttl": 300, "value": value})
        assert response.status_code == 201, response.text
    assert client.post(f"/api/hosted-zones/{zone_id}/records", headers=headers, json={"name": "bad.example.com", "type": "A", "ttl": 300, "value": "not-an-ip"}).status_code == 422
    assert client.post(f"/api/hosted-zones/{zone_id}/records", headers=headers, json={"name": "bad.example.com", "type": "MX", "ttl": 300, "value": "mail.example.com"}).status_code == 422


def test_record_crud_search_and_cascade_delete():
    token = login()
    headers = auth(token)
    zone = client.post("/api/hosted-zones", headers=headers, json={"name": "cascade-test.example", "zone_type": "Public"}).json()
    zone_id = zone["id"]
    record = client.post(f"/api/hosted-zones/{zone_id}/records", headers=headers, json={"name": "www.cascade-test.example", "type": "A", "ttl": 300, "value": "192.0.2.30"}).json()
    record_id = record["id"]
    assert client.get(f"/api/hosted-zones/{zone_id}/records?search=www", headers=headers).json()["total"] == 1
    assert client.put(f"/api/records/{record_id}", headers=headers, json={"name": "api.cascade-test.example", "type": "A", "ttl": 60, "value": "192.0.2.31"}).status_code == 200
    assert client.delete(f"/api/hosted-zones/{zone_id}", headers=headers).status_code == 200
    assert client.get(f"/api/records/{record_id}", headers=headers).status_code == 404
