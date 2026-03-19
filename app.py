import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
DIST_ASSETS_DIR = DIST_DIR / "assets"
PUBLIC_DIR = BASE_DIR / "public"
DATA_DIR = BASE_DIR / "data"
PUBLIC_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
SUBSCRIBERS_LOG = DATA_DIR / "subscribers.jsonl"
GUIDE_PUBLIC_PATH = "/static/lead-magnet-atelier-operators.pdf"
SAMPLE_ISSUE_PUBLIC_PATH = "/static/newsletter/issue-001.md"

BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
BREVO_LIST_ID = int(os.getenv("BREVO_LIST_ID", "17"))
BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL", "adrienlaine91@gmail.com")
BREVO_SENDER_NAME = os.getenv("BREVO_SENDER_NAME", "Atelier Operators")
RESEND_FROM = os.getenv("RESEND_FROM", "onboarding@resend.dev")
ADMIN_NOTIFICATION_EMAIL = os.getenv("ADMIN_NOTIFICATION_EMAIL", "adrienlaine91@gmail.com")
ENABLE_ADMIN_NOTIFICATIONS = os.getenv("ENABLE_ADMIN_NOTIFICATIONS", "false").lower() == "true"
WELCOME_REPLY_TO = os.getenv("WELCOME_REPLY_TO", "atelieroperators@agentmail.to")
SITE_URL = os.getenv("SITE_URL", "http://localhost:8030").rstrip("/")

app = FastAPI(title="Atelier Operators", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=str(PUBLIC_DIR)), name="static")
if DIST_ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(DIST_ASSETS_DIR)), name="assets")


class SubscribeRequest(BaseModel):
    email: str
    first_name: str | None = Field(default=None, max_length=120)
    role: str | None = Field(default=None, max_length=160)
    bottleneck: str | None = Field(default=None, max_length=500)
    source: str | None = Field(default="site")
    tracking: dict[str, str] | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Email invalide")
        return value


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def public_url(path: str, site_url: str | None = None) -> str:
    base_url = (site_url or SITE_URL).rstrip("/")
    return f"{base_url}{path}"


async def brevo_request(method: str, path: str, payload: dict[str, Any] | None = None) -> httpx.Response:
    if not BREVO_API_KEY:
        raise RuntimeError("BREVO_API_KEY manquant")
    headers = {
        "api-key": BREVO_API_KEY,
        "accept": "application/json",
        "content-type": "application/json",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        return await client.request(method, f"https://api.brevo.com/v3{path}", headers=headers, json=payload)


async def resend_request(payload: dict[str, Any]) -> httpx.Response:
    if not RESEND_API_KEY:
        raise RuntimeError("RESEND_API_KEY manquant")
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        return await client.post("https://api.resend.com/emails", headers=headers, json=payload)


async def ensure_brevo_setup() -> None:
    if not BREVO_API_KEY:
        return
    for attr in ("ROLE", "BOTTLENECK", "SOURCE"):
        resp = await brevo_request("POST", f"/contacts/attributes/normal/{attr}", {"type": "text"})
        if resp.status_code not in (201, 204, 400):
            raise RuntimeError(f"Erreur Brevo attribut {attr}: {resp.status_code} {resp.text}")


async def upsert_brevo_contact(payload: SubscribeRequest) -> None:
    contact_payload = {
        "email": payload.email,
        "listIds": [BREVO_LIST_ID],
        "updateEnabled": True,
        "attributes": {
            "PRENOM": payload.first_name or "",
            "ROLE": payload.role or "",
            "BOTTLENECK": payload.bottleneck or "",
            "SOURCE": payload.source or "site",
        },
    }
    resp = await brevo_request("POST", "/contacts", contact_payload)
    if resp.status_code not in (201, 204):
        raise RuntimeError(f"Erreur Brevo contact: {resp.status_code} {resp.text}")


async def send_welcome_email(payload: SubscribeRequest, site_url: str | None = None) -> dict[str, Any]:
    subject = "Ton guide Atelier Operators — lien direct + workflow #1"
    guide_url = public_url(GUIDE_PUBLIC_PATH, site_url=site_url)
    sample_issue_url = public_url(SAMPLE_ISSUE_PUBLIC_PATH, site_url=site_url)
    greeting_name = payload.first_name or ""
    text = (
        f"Salut {greeting_name},\n\n"
        "Ton guide est prêt. Ouvre-le ici :\n"
        f"{guide_url}\n\n"
        "Tu peux aussi lire un exemple réel ici :\n"
        f"{sample_issue_url}\n\n"
        "TL;DR :\n"
        "- 7 workflows IA structurés\n"
        "- des prompts + checklists directement réutilisables\n"
        "- 1 prochain test à lancer aujourd’hui\n\n"
        "Le bon usage du guide n’est pas de tout lire. Choisis 1 workflow et teste-le aujourd’hui.\n\n"
        "Réponds à ce mail avec ton rôle + ton principal blocage, et je t’enverrai le workflow le plus utile pour toi.\n\n"
        "À très vite,\nAtelier Operators"
    )
    html = f"""
    <div style=\"font-family:Inter,Arial,sans-serif;max-width:640px;margin:0 auto;color:#111827;line-height:1.6\">
      <p>Salut {greeting_name},</p>
      <p><strong>Ton guide est prêt.</strong> Ouvre-le ici :</p>
      <p>
        <a href=\"{guide_url}\" style=\"display:inline-block;padding:12px 18px;border-radius:12px;background:#111827;color:#ffffff;text-decoration:none;font-weight:600\">Ouvrir le guide</a>
      </p>
      <p>Tu peux aussi lire un exemple réel ici : <a href=\"{sample_issue_url}\">voir une édition complète</a>.</p>
      <div style=\"margin:20px 0;padding:16px;border-radius:16px;background:#f3f4f6\">
        <div style=\"font-size:12px;letter-spacing:0.12em;text-transform:uppercase;color:#6b7280\">TL;DR</div>
        <ul style=\"margin:12px 0 0;padding-left:18px\">
          <li>7 workflows IA structurés</li>
          <li>des prompts + checklists directement réutilisables</li>
          <li>1 prochain test à lancer aujourd’hui</li>
        </ul>
      </div>
      <p>Le bon usage du guide n’est pas de tout lire. Choisis <strong>1 workflow</strong> et teste-le aujourd’hui.</p>
      <p><strong>Réponds à ce mail avec ton rôle + ton principal blocage</strong>, et je t’enverrai le workflow le plus utile pour toi.</p>
      <p>À très vite,<br><strong>Atelier Operators</strong></p>
    </div>
    """
    resend_payload = {
        "from": RESEND_FROM,
        "to": [payload.email],
        "reply_to": WELCOME_REPLY_TO,
        "subject": subject,
        "text": text,
        "html": html,
    }
    try:
        resp = await resend_request(resend_payload)
        if resp.status_code == 200:
            return {"provider": "resend", "status_code": resp.status_code, "body": resp.text}
        fallback = await brevo_request("POST", "/smtp/email", {
            "sender": {"name": BREVO_SENDER_NAME, "email": BREVO_SENDER_EMAIL},
            "to": [{"email": payload.email, "name": payload.first_name or payload.email}],
            "replyTo": {"email": WELCOME_REPLY_TO, "name": BREVO_SENDER_NAME},
            "subject": subject,
            "textContent": text,
            "htmlContent": html,
        })
        return {
            "provider": "brevo-fallback",
            "resend_status_code": resp.status_code,
            "resend_body": resp.text,
            "status_code": fallback.status_code,
            "body": fallback.text,
        }
    except Exception as exc:
        return {"provider": "resend", "error": str(exc)}


async def notify_admin(payload: SubscribeRequest) -> dict[str, Any]:
    if not ENABLE_ADMIN_NOTIFICATIONS:
        return {"provider": "disabled", "status": "skipped"}

    body = {
        "from": RESEND_FROM,
        "to": [ADMIN_NOTIFICATION_EMAIL],
        "reply_to": payload.email,
        "subject": f"Nouvelle inscription Atelier Operators — {payload.email}",
        "text": (
            f"Email: {payload.email}\n"
            f"Prénom: {payload.first_name or ''}\n"
            f"Rôle: {payload.role or ''}\n"
            f"Goulet d'étranglement: {payload.bottleneck or ''}\n"
            f"Source: {payload.source or 'site'}\n"
        ),
    }
    try:
        resp = await resend_request(body)
        return {"provider": "resend", "status_code": resp.status_code, "body": resp.text}
    except Exception as exc:
        return {"provider": "resend", "error": str(exc)}



def log_subscriber(
    payload: SubscribeRequest,
    brevo_status: dict[str, Any],
    welcome_status: dict[str, Any],
    admin_status: dict[str, Any],
) -> None:
    row = {
        "timestamp": now_iso(),
        "email": payload.email,
        "first_name": payload.first_name,
        "role": payload.role,
        "bottleneck": payload.bottleneck,
        "source": payload.source,
        "tracking": payload.tracking,
        "brevo": brevo_status,
        "welcome": welcome_status,
        "admin_notification": admin_status,
    }
    with SUBSCRIBERS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


@app.on_event("startup")
async def startup_event() -> None:
    await ensure_brevo_setup()


@app.get("/")
async def home() -> FileResponse:
    target = DIST_DIR / "index.html" if (DIST_DIR / "index.html").exists() else BASE_DIR / "index.html"
    return FileResponse(target)


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({
        "ok": True,
        "brevo_configured": bool(BREVO_API_KEY),
        "resend_configured": bool(RESEND_API_KEY),
        "brevo_list_id": BREVO_LIST_ID,
    })


@app.get("/api/proof")
async def proof() -> JSONResponse:
    subscriber_count = 0
    try:
        if BREVO_API_KEY:
            resp = await brevo_request("GET", f"/contacts/lists/{BREVO_LIST_ID}")
            if resp.status_code == 200:
                data = resp.json()
                subscriber_count = int(data.get("uniqueSubscribers") or data.get("totalSubscribers") or 0)
    except Exception:
        subscriber_count = 0

    return JSONResponse({
        "subscriber_count": subscriber_count,
        "label": (
            f"{subscriber_count}+ inscrits"
            if subscriber_count >= 25
            else "3 éditions déjà publiées"
        ),
    })


@app.post("/api/subscribe")
async def subscribe(payload: SubscribeRequest, request: Request) -> JSONResponse:
    tracking = dict(payload.tracking or {})
    if request.headers.get("referer"):
        tracking.setdefault("request_referer", request.headers["referer"][:500])
    if request.headers.get("user-agent"):
        tracking.setdefault("user_agent", request.headers["user-agent"][:300])
    payload = payload.model_copy(update={"tracking": tracking or None})
    request_site_url = str(request.base_url).rstrip("/")

    brevo_status: dict[str, Any]
    try:
        await upsert_brevo_contact(payload)
        brevo_status = {"status": "ok"}
    except Exception as exc:
        brevo_status = {"status": "error", "detail": str(exc)}

    welcome_status = await send_welcome_email(payload, site_url=request_site_url)
    admin_status = await notify_admin(payload)
    log_subscriber(payload, brevo_status, welcome_status, admin_status)

    response_payload = {
        "success": True,
        "message": "Inscription enregistrée.",
        "download_url": GUIDE_PUBLIC_PATH,
        "sample_issue_url": SAMPLE_ISSUE_PUBLIC_PATH,
        "brevo": brevo_status,
        "welcome": welcome_status,
        "admin_notification": admin_status,
    }
    if brevo_status.get("status") != "ok":
        response_payload["processing_warning"] = "Inscription capturée avec reprise en arrière-plan requise côté ESP."

    return JSONResponse(response_payload)
