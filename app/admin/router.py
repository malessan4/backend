from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.security import get_current_admin, verify_same_origin
from app.db import api_key_repository as repo
from app.services import key_rotation_service

router = APIRouter(include_in_schema=False)

_templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(_templates_dir))


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, admin: str = Depends(get_current_admin)):
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "keys": key_rotation_service.list_status_for_dashboard(),
            "max_keys_reached": repo.count_keys() >= repo.MAX_KEYS,
        },
    )


@router.post("/keys")
def create_key(
    label: str = Form(...),
    key_value: str = Form(...),
    rpm_threshold: int | None = Form(None),
    tpm_threshold: int | None = Form(None),
    rpd_threshold: int | None = Form(None),
    tpd_threshold: int | None = Form(None),
    admin: str = Depends(get_current_admin),
    _origin_ok: None = Depends(verify_same_origin),
):
    repo.create(
        label=label,
        raw_key=key_value,
        rpm_threshold=rpm_threshold,
        tpm_threshold=tpm_threshold,
        rpd_threshold=rpd_threshold,
        tpd_threshold=tpd_threshold,
    )
    return RedirectResponse("/admin", status_code=303)


@router.post("/keys/{key_id}/update")
def update_key(
    key_id: int,
    label: str = Form(...),
    key_value: str = Form(""),
    rpm_threshold: int | None = Form(None),
    tpm_threshold: int | None = Form(None),
    rpd_threshold: int | None = Form(None),
    tpd_threshold: int | None = Form(None),
    enabled: bool = Form(False),
    make_current: bool = Form(False),
    admin: str = Depends(get_current_admin),
    _origin_ok: None = Depends(verify_same_origin),
):
    repo.update(
        key_id,
        label=label,
        rpm_threshold=rpm_threshold,
        tpm_threshold=tpm_threshold,
        rpd_threshold=rpd_threshold,
        tpd_threshold=tpd_threshold,
        enabled=enabled,
        raw_key=key_value or None,
    )
    if make_current and enabled:
        repo.set_current(key_id)
    return RedirectResponse("/admin", status_code=303)


@router.post("/keys/{key_id}/delete")
def delete_key(
    key_id: int,
    admin: str = Depends(get_current_admin),
    _origin_ok: None = Depends(verify_same_origin),
):
    repo.delete(key_id)
    return RedirectResponse("/admin", status_code=303)
