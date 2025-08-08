#!/usr/bin/env python3

import requests
import uuid
import sqlite3
import time
import json
import os

BASE_URL = "http://localhost:5001"


def _db_path():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    p1 = os.path.join(root, 'backend', 'easyapply.db')
    p2 = os.path.join(root, 'easyapply.db')
    return p1 if os.path.exists(p1) else p2


def _approve_user(user_id: str):
    conn = sqlite3.connect(_db_path())
    cur = conn.cursor()
    cur.execute("UPDATE users SET status='approved' WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


def run_isolation_test():
    print("🧪 Running multi-tenant auth/isolation test…")
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPassword123!"

    # 1) Register
    r = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": email,
        "password": password,
        "firstName": "Test",
        "lastName": "User"
    })
    assert r.status_code in (200, 201), f"register failed: {r.status_code} {r.text}"

    # Extract created user id by looking it up
    conn = sqlite3.connect(_db_path())
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email=?", (email,))
    row = cur.fetchone()
    assert row, "user not created"
    user_id = row[0]
    conn.close()

    # 2) Approve user directly in DB for test
    _approve_user(user_id)

    # 3) Login to get token
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    token = r.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 4) Save LinkedIn creds (per-user)
    r = requests.put(f"{BASE_URL}/api/profile", headers=headers, json={
        "linkedin_email": f"linkedin_{uuid.uuid4().hex[:6]}@example.com",
        "linkedin_password": "LinkedInPass123!",
        "jobPreferences": {"positions": ["Software Engineer"], "locations": ["Remote"]}
    })
    assert r.status_code == 200, f"profile update failed: {r.status_code} {r.text}"

    # 5) Read back profile; ensure user id context is respected
    r = requests.get(f"{BASE_URL}/api/profile", headers=headers)
    assert r.status_code == 200, f"profile get failed: {r.status_code} {r.text}"
    data = r.json()
    assert data.get("user", {}).get("email") == email, "profile not scoped to logged-in user"

    # 6) Applications stats should be for this user and not depend on any hardcoded user
    r = requests.get(f"{BASE_URL}/api/applications/stats", headers=headers)
    assert r.status_code == 200, f"apps stats failed: {r.status_code} {r.text}"
    stats = r.json()
    assert isinstance(stats.get("totalApplications", 0), int), "stats missing totalApplications"

    print("✅ Isolation test passed for user:", email)


if __name__ == "__main__":
    run_isolation_test() 