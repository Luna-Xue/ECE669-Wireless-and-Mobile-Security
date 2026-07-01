"""Local web backend for the ranscope UI — your trained model, live.

Loads `base (Qwen2.5-1.5B) + your LoRA adapter` once via explainer.local, then
serves the UI and three endpoints so the page can drive it:

    GET  /                 -> ui/index.html
    GET  /api/scenarios    -> {"scenarios": [...]}
    POST /api/generate     {scenario, seed, noise, inject} -> {logs, ground_truth}
    POST /api/diagnose     {logs:[{id,ts,component,severity,message}, ...]}
                           -> DiagnosisResult JSON (your model's analysis)

Stdlib only (http.server) — no FastAPI/uvicorn. Single trained model instance,
served thread-safely. Run from anywhere:

    pip install -r requirements-local.txt        # one-time (torch/transformers/peft)
    python ui/server.py                          # then open http://localhost:8000
    ORAN_LOCAL_ADAPTER=./explainer-lora python ui/server.py   # explicit adapter

The base model downloads from HuggingFace on first run (~3GB); the adapter is
read from ORAN_LOCAL_ADAPTER (default ./explainer-lora).
"""
from __future__ import annotations

import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Make the project importable no matter where the server is launched from.
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
# Default the adapter to the repo-root explainer-lora/ unless the user set one.
os.environ.setdefault("ORAN_LOCAL_ADAPTER", os.path.join(_REPO, "explainer-lora"))

from core.log_event import LogEvent          # noqa: E402
from generator import SCENARIOS, generate    # noqa: E402

_UI_HTML = os.path.join(_REPO, "ui", "index.html")
HOST = os.environ.get("ORAN_UI_HOST", "127.0.0.1")
PORT = int(os.environ.get("ORAN_UI_PORT", "8000"))

# The model is heavy to load; build it lazily on the first /diagnose and guard
# concurrent generation (one model, not thread-safe for parallel .generate()).
_explainer = None
_explainer_err = None
_lock = threading.Lock()


def _get_explainer():
    global _explainer, _explainer_err
    if _explainer is not None or _explainer_err is not None:
        return _explainer
    with _lock:
        if _explainer is None and _explainer_err is None:
            try:
                from explainer.local import LocalExplainer
                adapter = os.environ["ORAN_LOCAL_ADAPTER"]
                print(f"[server] loading base + adapter ({adapter}) — first run downloads the base model…",
                      flush=True)
                _explainer = LocalExplainer(adapter_path=adapter, max_new_tokens=1024)
                print(f"[server] model ready on device={_explainer.device}", flush=True)
            except Exception as exc:  # surfaced to the UI as a clear error
                _explainer_err = str(exc)
                print(f"[server] model load FAILED: {exc}", flush=True)
    return _explainer


def _ground_truth_dict(gt) -> dict:
    return {
        "root_cause_component": gt.root_cause_component,
        "root_cause_summary": gt.root_cause_summary,
        "chain": [{"component": s.component, "event": s.event, "log_ids": s.log_ids} for s in gt.chain],
        "recommended_actions": gt.recommended_actions,
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self) -> dict:
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n) or b"{}")

    def log_message(self, fmt, *args):  # quieter console
        return

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            try:
                with open(_UI_HTML, "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            except FileNotFoundError:
                self._send(404, {"error": f"ui not found at {_UI_HTML}"})
        elif self.path == "/api/scenarios":
            self._send(200, {"scenarios": list(SCENARIOS)})
        elif self.path == "/api/health":
            self._send(200, {"loaded": _explainer is not None, "error": _explainer_err})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        try:
            payload = self._read_json()
        except Exception as exc:
            return self._send(400, {"error": f"bad JSON: {exc}"})

        if self.path == "/api/generate":
            name = payload.get("scenario")
            if name not in SCENARIOS:
                return self._send(400, {"error": f"unknown scenario {name!r}"})
            try:
                gen = generate(
                    name,
                    seed=int(payload.get("seed", 0)),
                    noise_level=int(payload.get("noise", 6)),
                    inject=bool(payload.get("inject", False)),
                )
            except Exception as exc:
                return self._send(500, {"error": f"generate failed: {exc}"})
            return self._send(200, {
                "scenario": gen.name,
                "note": gen.note,
                "logs": [l.model_dump() for l in gen.logs],
                "ground_truth": _ground_truth_dict(gen.ground_truth),
            })

        if self.path == "/api/diagnose":
            raw = payload.get("logs") or []
            try:
                logs = [LogEvent(**l) for l in raw]
            except Exception as exc:
                return self._send(400, {"error": f"bad logs: {exc}"})
            if not logs:
                return self._send(400, {"error": "no logs provided"})
            ex = _get_explainer()
            if ex is None:
                return self._send(503, {"error": f"model unavailable: {_explainer_err}"})
            with _lock:  # one generation at a time on a single model
                try:
                    result = ex.diagnose(logs)
                except Exception as exc:
                    return self._send(500, {"error": f"diagnose failed: {exc}"})
            return self._send(200, json.loads(result.model_dump_json()))

        self._send(404, {"error": "not found"})


def main():
    eager = "--load" in sys.argv
    print(f"[server] ranscope on http://{HOST}:{PORT}  (adapter={os.environ['ORAN_LOCAL_ADAPTER']})", flush=True)
    print("[server] open the URL in a browser; the model loads on the first Diagnose.", flush=True)
    if eager:
        _get_explainer()
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
