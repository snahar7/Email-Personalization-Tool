from app.services import email_service


def test_health(client):
    assert client.get("/health").json() == {"status": "healthy"}


def test_create_and_list_company(client):
    r = client.post("/api/companies/", json={"name": "Acme", "industry": "SaaS"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["id"] and body["name"] == "Acme" and body["created_at"]
    assert [c["name"] for c in client.get("/api/companies/").json()] == ["Acme"]


def test_csv_import_and_prospect_list(client, imported):
    assert len(imported) >= 2
    assert {"name", "email", "company_id", "created_at"} <= set(imported[0])
    # re-import skips duplicates
    with open("sample_prospects.csv", "rb") as f:
        r = client.post("/api/companies/upload-csv", files={"file": ("p.csv", f, "text/csv")})
    assert r.json()["prospects_created"] == 0
    assert r.json()["prospects_skipped"] == len(imported)


def test_csv_missing_columns(client):
    r = client.post("/api/companies/upload-csv", files={"file": ("p.csv", b"name,email\na,b@c.com\n", "text/csv")})
    assert r.status_code == 400
    assert "missing columns" in r.json()["detail"]


def test_generate_email_uses_openai(client, imported, fake_openai, monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-test")
    pid = imported[0]["id"]
    r = client.post(f"/api/prospects/{pid}/generate-email", json={"additional_context": {"seats": 40}})
    assert r.status_code == 200, r.text
    email = r.json()
    assert email["subject"] == "Hello John"
    assert email["body"].startswith("Hi John")
    assert email["model"] == "gpt-test"
    call = fake_openai.calls[0]
    assert call["model"] == "gpt-test"
    prompt = call["messages"][-1]["content"]
    assert imported[0]["name"] in prompt and "seats: 40" in prompt


def test_generate_email_with_template(client, imported, fake_openai):
    company_id = imported[0]["company_id"]
    t = client.post("/api/templates/", json={"name": "intro", "subject": "Hi", "body": "Base body", "company_id": company_id})
    assert t.status_code == 200, t.text
    r = client.post(f"/api/prospects/{imported[0]['id']}/generate-email", json={"template_id": t.json()["id"]})
    assert r.status_code == 200
    assert "Base body" in fake_openai.calls[0]["messages"][-1]["content"]


def test_generate_email_without_key_returns_503(client, imported):
    r = client.post(f"/api/prospects/{imported[0]['id']}/generate-email", json={})
    assert r.status_code == 503
    assert "OPENAI_API_KEY" in r.json()["detail"]


def test_generate_email_unknown_prospect(client, fake_openai):
    assert client.post("/api/prospects/999/generate-email", json={}).status_code == 404


def test_default_model(monkeypatch):
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    assert email_service.get_model() == "gpt-4o-mini"


def test_parse_email_fallback():
    assert email_service.parse_email("just a body") == ("", "just a body")


def test_send_email_requires_smtp(client, imported, monkeypatch):
    for k in ("SMTP_SERVER", "SMTP_USERNAME", "SMTP_PASSWORD"):
        monkeypatch.delenv(k, raising=False)
    r = client.post(f"/api/prospects/{imported[0]['id']}/send-email", json={"subject": "s", "body": "b"})
    assert r.status_code == 503


def test_send_email_marks_contacted(client, imported, monkeypatch):
    sent = []
    monkeypatch.setattr(email_service, "send_email", lambda to, s, b: sent.append((to, s, b)))
    p = imported[0]
    r = client.post(f"/api/prospects/{p['id']}/send-email", json={"subject": "s", "body": "b"})
    assert r.status_code == 200, r.text
    assert sent == [(p["email"], "s", "b")]
    updated = client.get(f"/api/prospects/{p['id']}").json()
    assert updated["status"] == "contacted" and updated["last_contacted"]


def test_metrics_and_engagement(client, imported):
    assert client.get("/api/engagements/metrics/").json()["total_sent"] == 0
    assert client.get(f"/api/prospects/{imported[0]['id']}/engagement/").status_code == 200
