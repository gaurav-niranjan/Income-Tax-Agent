"""Eval run storage: run ids, folders and the comparison table (no models needed)."""

from datetime import datetime

from runs import config_diff, config_hash, load_runs, save_run, stamp

MANIFEST = {"name": "idx", "created": "2026-10-18T09:00:00", "chunker": {"size": 1000},
            "stats": {"embed_seconds": 185.5}}
CONFIG = {"index": "idx", "mode": "dense", "neighbours": True, "git_commit": "abc1234",
          "index_manifest": MANIFEST}
RANKS = {"n": 1, "hits@1": 1, "hit@1": 1.0, "hits@3": 1, "hit@3": 1.0, "hits@5": 1, "hit@5": 1.0, "mrr": 1.0}
SUMMARY = {"all": {"n": 1, "section": RANKS, "strict": RANKS, "phrase": RANKS}}


def test_hash_ignores_bookkeeping_but_not_settings():
    h = config_hash(CONFIG)
    rebuilt = MANIFEST | {"created": "2026-10-19T10:00:00", "stats": {"embed_seconds": 200.0}}
    assert config_hash(CONFIG | {"git_commit": "def5678", "note": "x", "index_manifest": rebuilt}) == h
    assert config_hash(CONFIG | {"mode": "bm25"}) != h
    assert config_hash(CONFIG | {"index_manifest": MANIFEST | {"chunker": {"size": 500}}}) != h


def test_stamp_puts_run_metadata_first():
    config = stamp("retrieval", CONFIG, note="baseline", created=datetime(2026, 10, 18, 16, 40))
    assert config["run_id"] == f"2026-10-18_{config_hash(CONFIG)}"
    assert list(config)[:5] == ["run_id", "kind", "created", "config_hash", "note"]
    assert config_hash(config) == config_hash(CONFIG)  # stamping does not change the hash


def test_same_config_same_day_replaces_the_run(tmp_path):
    first = stamp("retrieval", CONFIG, created=datetime(2026, 10, 18, 10, 0))
    again = stamp("retrieval", CONFIG | {"git_commit": "def5678"}, created=datetime(2026, 10, 18, 11, 0))
    other = stamp("retrieval", CONFIG | {"mode": "bm25"}, created=datetime(2026, 10, 18, 12, 0))
    for config in (first, again, other):
        save_run(config, SUMMARY, [], "# report\n", results_dir=tmp_path)

    runs = load_runs("retrieval", tmp_path)
    assert [r["config"]["mode"] for r in runs] == ["bm25", "dense"]  # newest first
    assert runs[1]["config"]["git_commit"] == "def5678"
    index = (tmp_path / "README.md").read_text()
    assert f"retrieval/{other['run_id']}/report.md" in index and "1.00 (1/1)" in index


def test_config_diff_compares_nested_keys():
    b = CONFIG | {"index_manifest": MANIFEST | {"chunker": {"size": 500}}}
    assert config_diff(CONFIG, b) == [("index_manifest.chunker.size", 1000, 500)]
