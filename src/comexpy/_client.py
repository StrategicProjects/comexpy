"""HTTP layer for the ComexStat API.

Mirrors ``comex_get`` / ``comex_post`` from the R package's ``utils.R``:

* GET and POST helpers against :data:`BASE_URL`.
* User-configurable retry/timeout behaviour (the ComexStat API rate-limits
  aggressively with HTTP 429 and a 10-second recommended back-off).
* Automatic retry on SSL certificate-verification failures — the ComexStat
  servers use ICP-Brasil certificates that some systems do not trust.

On failure a :class:`ComexError` is raised with a friendly message.
"""
from __future__ import annotations

import time
from typing import Any, Mapping, Optional

import requests

from . import _msg

BASE_URL = "https://api-comexstat.mdic.gov.br"

_USER_AGENT = "comexpy (Python package)"

# Defaults mirror the R package options (comexr.*). The API recommends a
# 10-second wait after a 429, so retry_time defaults to 10.
_CONFIG = {
    "timeout_get": 60,
    "timeout_post": 120,
    "max_tries": 3,
    "retry_time": 10,
    "ssl_verify": True,
}


class ComexError(RuntimeError):
    """Raised when a ComexStat API request fails."""


def set_options(
    *,
    timeout_get: Optional[int] = None,
    timeout_post: Optional[int] = None,
    max_tries: Optional[int] = None,
    retry_time: Optional[int] = None,
    ssl_verify: Optional[bool] = None,
) -> None:
    """Configure HTTP retry/timeout behaviour (equivalent to the R options).

    The ComexStat API frequently returns rate-limit errors (HTTP 429,
    *"Você excedeu o limite de solicitações..."*) or times out. Adjust these
    settings to work around such errors without overloading the servers.

    Parameters
    ----------
    timeout_get : int, optional
        Seconds to wait for a response on GET requests (default 60).
    timeout_post : int, optional
        Seconds to wait for a response on POST requests (default 120).
    max_tries : int, optional
        Maximum number of attempts for a failing request (default 3).
        Adjusting ``retry_time`` is generally a better way to avoid errors.
    retry_time : int, optional
        Seconds to wait between retries after a transient failure
        (default 10, matching the API's recommended back-off).
    ssl_verify : bool, optional
        Whether to verify SSL certificates. Set to ``False`` to skip
        verification when the ICP-Brasil certificate chain is not trusted.
    """
    if timeout_get is not None:
        _CONFIG["timeout_get"] = int(timeout_get)
    if timeout_post is not None:
        _CONFIG["timeout_post"] = int(timeout_post)
    if max_tries is not None:
        _CONFIG["max_tries"] = int(max_tries)
    if retry_time is not None:
        _CONFIG["retry_time"] = int(retry_time)
    if ssl_verify is not None:
        _CONFIG["ssl_verify"] = bool(ssl_verify)


def get_options() -> dict:
    """Return a copy of the current HTTP configuration."""
    return dict(_CONFIG)


def _is_ssl_error(exc: Exception) -> bool:
    text = f"{exc} {getattr(exc, '__cause__', '')}".lower()
    return any(t in text for t in ("ssl", "certificate", "peer"))


def _perform(method: str, url: str, **kwargs: Any) -> requests.Response:
    """Perform a request with retries and SSL auto-fallback."""
    max_tries = max(1, int(_CONFIG["max_tries"]))
    retry_time = int(_CONFIG["retry_time"])
    verify = bool(_CONFIG["ssl_verify"])

    last_exc: Optional[Exception] = None
    for attempt in range(1, max_tries + 1):
        try:
            resp = requests.request(method, url, verify=verify, **kwargs)
        except requests.exceptions.SSLError as exc:
            # SSL verification failed: retry once without verification and
            # remember the choice for the rest of the session.
            if verify:
                _msg.warn(
                    "SSL certificate verification failed. Retrying without "
                    "SSL verification. To suppress this, call "
                    "comexpy.set_options(ssl_verify=False)."
                )
                _CONFIG["ssl_verify"] = False
                verify = False
                last_exc = exc
                continue
            last_exc = exc
        except requests.RequestException as exc:
            last_exc = exc
        else:
            # Retry on rate-limit / transient server errors.
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < max_tries:
                time.sleep(retry_time)
                continue
            return resp

        if attempt < max_tries:
            time.sleep(retry_time)

    raise ComexError(
        f"Failed to perform HTTP request to the ComexStat API.\n"
        f"  x {last_exc}\n  i URL: {url}"
    )


def _check(resp: requests.Response, endpoint: str) -> Any:
    if resp.status_code >= 400:
        try:
            body = resp.json()
            msg = body.get("message") or (
                body.get("error", {}).get("message")
                if isinstance(body.get("error"), dict)
                else None
            )
        except ValueError:
            msg = None
        msg = msg or f"HTTP {resp.status_code}"
        raise ComexError(
            f"API request failed (HTTP {resp.status_code})\n"
            f"  i Endpoint: {endpoint}\n  i Message: {msg}"
        )
    try:
        return resp.json()
    except ValueError as exc:  # pragma: no cover
        raise ComexError(
            f"Could not parse API response as JSON.\n  i Endpoint: {endpoint}"
        ) from exc


def comex_get(
    endpoint: str,
    query: Optional[Mapping[str, Any]] = None,
    verbose: bool = True,
) -> Any:
    """Perform a GET request to the ComexStat API and return parsed JSON."""
    url = BASE_URL + endpoint
    if verbose:
        _msg.step(f"GET {endpoint}")
    clean = {k: v for k, v in (query or {}).items() if v is not None}
    resp = _perform(
        "GET",
        url,
        params=clean or None,
        headers={"Accept": "application/json", "User-Agent": _USER_AGENT},
        timeout=_CONFIG["timeout_get"],
    )
    return _check(resp, endpoint)


def comex_post(
    endpoint: str,
    body: Any,
    query: Optional[Mapping[str, Any]] = None,
    verbose: bool = True,
) -> Any:
    """Perform a POST request to the ComexStat API and return parsed JSON."""
    url = BASE_URL + endpoint
    if verbose:
        _msg.step(f"POST {endpoint}")
    clean = {k: v for k, v in (query or {}).items() if v is not None}
    resp = _perform(
        "POST",
        url,
        params=clean or None,
        json=body,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": _USER_AGENT,
        },
        timeout=_CONFIG["timeout_post"],
    )
    return _check(resp, endpoint)
