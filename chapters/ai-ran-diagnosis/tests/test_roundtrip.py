"""Log files must round-trip: render_logs (Python / gen_logs) -> parse_logs
(analyze_logs / same format the UI saves) -> identical logs."""
import json

from core.log_event import render_logs
from generator import generate
from tools.analyze_logs import parse_logs


def test_text_roundtrip():
    g = generate("prb_exhaustion", seed=7, noise_level=10)
    parsed = parse_logs(render_logs(g.logs))
    assert len(parsed) == len(g.logs)
    for a, b in zip(parsed, g.logs):
        assert (a.id, a.ts, a.severity, a.component, a.message) == \
               (b.id, b.ts, b.severity, b.component, b.message)


def test_json_list_roundtrip():
    g = generate("auth_failure", seed=0)
    parsed = parse_logs(json.dumps([l.model_dump() for l in g.logs]))
    assert [l.id for l in parsed] == [l.id for l in g.logs]


def test_parse_ignores_blank_and_garbage_lines():
    text = "\n[L001] 10:42:00.058 ERROR O-DU something happened\n\nnot a log line\n"
    parsed = parse_logs(text)
    assert len(parsed) == 1 and parsed[0].component == "O-DU"
