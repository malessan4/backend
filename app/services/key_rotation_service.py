from app.core.config import settings
from app.db import api_key_repository as repo

NEAR_LIMIT_RATIO = 0.8

# Defaults de capa gratuita para Gemini 2.5 Flash (modelo default del proyecto),
# según AI Studio > Límites de frecuencia por modelo. Ajustables por key desde /admin.
DEFAULT_RPM_THRESHOLD = 5
DEFAULT_TPM_THRESHOLD = 250_000
DEFAULT_RPD_THRESHOLD = 20


class GeminiKeyError(Exception):
    pass


class NoApiKeyConfiguredError(GeminiKeyError, ValueError):
    """Sin ninguna key cargada. Subclase de ValueError para no romper
    el manejo de errores ya existente en los endpoints (400)."""


class AllKeysExhaustedError(GeminiKeyError):
    """Las 3 keys alcanzaron su umbral configurado (429)."""


def _threshold_pairs(row: dict) -> list[tuple[int | None, int]]:
    """(umbral, contador_actual) para cada una de las 4 dimensiones:
    RPM/TPM (ventana de minuto) y RPD/TPD (ventana diaria)."""
    return [
        (row["rpm_threshold"], row["minute_request_count"]),
        (row["tpm_threshold"], row["minute_token_count"]),
        (row["rpd_threshold"], row["request_count"]),
        (row["tpd_threshold"], row["total_token_count"]),
    ]


def _is_exhausted(row: dict) -> bool:
    return any(
        threshold is not None and count >= threshold
        for threshold, count in _threshold_pairs(row)
    )


def _usage_ratio(row: dict) -> float:
    ratios = [count / threshold for threshold, count in _threshold_pairs(row) if threshold]
    return max(ratios) if ratios else 0.0


def get_status_label(row: dict) -> str:
    if not row["enabled"]:
        return "disabled"
    if _is_exhausted(row):
        return "exhausted"
    near = _usage_ratio(row) >= NEAR_LIMIT_RATIO
    if row["is_current"]:
        return "near-limit" if near else "active"
    return "near-limit" if near else "standby"


def get_active_client_key() -> tuple[int, str]:
    """
    Devuelve (key_id, raw_key) de la key activa, rotando automáticamente
    a la siguiente disponible si la actual está agotada.
    """
    rows = [repo.apply_resets_if_needed(r) for r in repo.list_all_enabled_ordered_by_id()]
    if not rows:
        raise NoApiKeyConfiguredError(
            "No hay ninguna API key de Gemini configurada. Agregá una desde /admin."
        )

    current = next((r for r in rows if r["is_current"]), None)
    if current is None or _is_exhausted(current):
        start = rows.index(current) + 1 if current in rows else 0
        ordered = rows[start:] + rows[:start]
        nxt = next((r for r in ordered if not _is_exhausted(r)), None)
        if nxt is None:
            raise AllKeysExhaustedError(
                "Todas las API keys de Gemini alcanzaron su límite configurado. "
                "Los límites por minuto (RPM/TPM) se liberan en el próximo minuto; "
                "los diarios (RPD/TPD), a las 00:00 UTC. También podés agregar/ajustar "
                "una key desde /admin."
            )
        repo.set_current(nxt["id"])
        current = nxt

    return current["id"], repo.decrypt_raw_key(current)


def record_usage(key_id: int, usage_metadata) -> None:
    repo.record_usage(
        key_id,
        prompt_tokens=getattr(usage_metadata, "prompt_token_count", 0) or 0,
        candidates_tokens=getattr(usage_metadata, "candidates_token_count", 0) or 0,
        total_tokens=getattr(usage_metadata, "total_token_count", 0) or 0,
    )
    try:
        # Re-chequeo proactivo: si esta llamada agotó la key, el puntero
        # "activa" ya queda actualizado sin esperar la próxima request real.
        get_active_client_key()
    except (AllKeysExhaustedError, NoApiKeyConfiguredError):
        pass


def list_status_for_dashboard() -> list[dict]:
    rows = [repo.apply_resets_if_needed(r) for r in repo.list_all_ordered_by_id()]
    return [
        {
            "id": r["id"],
            "label": r["label"],
            "masked_key": repo.mask(r),
            "status": get_status_label(r),
            "enabled": bool(r["enabled"]),
            "minute_request_count": r["minute_request_count"],
            "rpm_threshold": r["rpm_threshold"],
            "minute_token_count": r["minute_token_count"],
            "tpm_threshold": r["tpm_threshold"],
            "request_count": r["request_count"],
            "rpd_threshold": r["rpd_threshold"],
            "total_token_count": r["total_token_count"],
            "tpd_threshold": r["tpd_threshold"],
            "usage_pct": round(_usage_ratio(r) * 100, 1),
        }
        for r in rows
    ]


def seed_from_env_if_empty() -> None:
    if repo.count_keys() > 0:
        return
    key = settings.GEMINI_API_KEY
    if key is None:
        return
    raw = key.get_secret_value()
    if not raw or raw == "tu_api_key_aqui":
        return
    new_id = repo.create(
        label="Key #1 (migrada desde .env)",
        raw_key=raw,
        rpm_threshold=DEFAULT_RPM_THRESHOLD,
        tpm_threshold=DEFAULT_TPM_THRESHOLD,
        rpd_threshold=DEFAULT_RPD_THRESHOLD,
        tpd_threshold=None,
    )
    repo.set_current(new_id)
