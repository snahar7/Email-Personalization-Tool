"""One-command demo: load sample_prospects.csv and draft a personalized email per prospect.

    python scripts/demo.py          # uses OPENAI_API_KEY from env/.env
    python scripts/demo.py --mock   # no key needed; fakes the OpenAI response

Uses a throwaway SQLite DB (demo.db) so it never touches your real data.
"""
import argparse
import os
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class _MockCompletions:
    def create(self, model, messages, **_):
        prompt = messages[-1]["content"]
        name = next((l.split(": ", 1)[1] for l in prompt.splitlines() if l.startswith("- Name: ")), "there")
        text = (
            f"SUBJECT: Quick idea for you, {name.split()[0]}\n"
            f"BODY:\nHi {name.split()[0]},\n\n(mock) This is where the AI-personalized email goes.\n\nBest,\nYou"
        )
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text))])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mock", action="store_true", help="fake OpenAI; no API key needed")
    parser.add_argument("--csv", default=str(ROOT / "sample_prospects.csv"))
    args = parser.parse_args()

    db_path = ROOT / "demo.db"
    db_path.unlink(missing_ok=True)
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    from fastapi.testclient import TestClient

    from app.main import app
    from app.services import email_service

    if args.mock:
        email_service.get_openai_client = lambda: SimpleNamespace(chat=SimpleNamespace(completions=_MockCompletions()))
    elif not os.getenv("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set. Add it to .env, or run with --mock.")

    client = TestClient(app)
    with open(args.csv, "rb") as f:
        r = client.post("/api/companies/upload-csv", files={"file": ("prospects.csv", f, "text/csv")})
    r.raise_for_status()
    print(f"Imported: {r.json()}\n")

    for p in client.get("/api/prospects/").json():
        r = client.post(f"/api/prospects/{p['id']}/generate-email", json={})
        if r.status_code != 200:
            print(f"[{p['name']}] failed: {r.status_code} {r.json().get('detail')}")
            continue
        email = r.json()
        print("=" * 70)
        print(f"To: {p['name']} <{p['email']}>  ({p.get('position') or ''})  model={email['model']}")
        print(f"Subject: {email['subject']}\n\n{email['body']}\n")


if __name__ == "__main__":
    main()
