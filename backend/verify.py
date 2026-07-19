"""OTP delivery via Plivo Verify — bypasses DLT with pre-approved templates."""
from __future__ import annotations
import logging
import os
import plivo

logger = logging.getLogger(__name__)


def _client():
    auth_id = os.environ.get("PLIVO_AUTH_ID", "")
    auth_token = os.environ.get("PLIVO_AUTH_TOKEN", "")
    if not (auth_id and auth_token):
        return None
    return plivo.RestClient(auth_id, auth_token)


def _normalize_indian(number: str) -> str:
    n = number.strip().replace(" ", "").replace("-", "")
    if n.startswith("+"):
        n = n[1:]
    if len(n) == 10 and n.isdigit():
        n = "91" + n
    return n


def send_otp_via_plivo(to: str, otp: str) -> dict:
    client = _client()
    app_uuid = os.environ.get("PLIVO_VERIFY_APP_UUID", "")
    if not (client and app_uuid):
        return {"sent": False, "error": "no_plivo_config"}
    try:
        resp = client.verify_session.create(
            recipient=_normalize_indian(to),
            app_uuid=app_uuid,
            channel="sms",
            otp=otp,
        )
        return {"sent": True, "session_uuid": getattr(resp, "session_uuid", None)}
    except Exception as e:
        logger.warning(f"Plivo Verify failure: {e}")
        return {"sent": False, "error": str(e)}
