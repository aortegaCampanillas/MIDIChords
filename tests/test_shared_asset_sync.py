import json
from pathlib import Path

from scripts import sync_shared_assets


def test_changelog_sync_writes_all_generated_targets(tmp_path, monkeypatch):
    source = tmp_path / "assets" / "changelog.json"
    targets = (
        tmp_path / "web" / "changelog.json",
        tmp_path / "mobile" / "changelog.json",
    )
    source.parent.mkdir(parents=True)
    source.write_text(
        json.dumps([{"version": "test", "items": []}], ensure_ascii=False),
        encoding="utf-8",
    )
    monkeypatch.setattr(sync_shared_assets, "CHANGELOG_SOURCE", source)
    monkeypatch.setattr(sync_shared_assets, "CHANGELOG_TARGETS", targets)

    assert sync_shared_assets.sync_changelog(check=True) == targets
    assert sync_shared_assets.sync_changelog() == targets
    assert sync_shared_assets.sync_changelog(check=True) == ()
    assert all(target.read_bytes() == source.read_bytes() for target in targets)


def test_changelog_sync_rejects_a_non_list_document(tmp_path, monkeypatch):
    source = tmp_path / "changelog.json"
    source.write_text('{"version": "invalid"}', encoding="utf-8")
    monkeypatch.setattr(sync_shared_assets, "CHANGELOG_SOURCE", source)

    try:
        sync_shared_assets.sync_changelog()
    except SystemExit as exc:
        assert "debe contener una lista" in str(exc)
    else:
        raise AssertionError("An invalid canonical changelog must be rejected")
