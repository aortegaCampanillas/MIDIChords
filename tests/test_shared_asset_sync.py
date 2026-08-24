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


def _write_version_fixture(tmp_path, monkeypatch, *, version="1.2.3", pubspec_build=5):
    version_source = tmp_path / "VERSION"
    version_source.write_text(f"{version}\n", encoding="utf-8")

    app_constants = tmp_path / "app_constants.py"
    app_constants.write_text('APP_RELEASE_NAME = "0.0.0"\n', encoding="utf-8")

    worker = tmp_path / "_worker.js"
    worker.write_text('const APP_VERSION = "0.0.0";\n', encoding="utf-8")

    web_app_js = tmp_path / "app.js"
    web_app_js.write_text('const WEB_APP_VERSION_FALLBACK = "0.0.0";\n', encoding="utf-8")

    app_html = tmp_path / "app.html"
    app_html.write_text('"softwareVersion": "0.0.0",\n', encoding="utf-8")
    index_html = tmp_path / "index.html"
    index_html.write_text('"softwareVersion": "0.0.0",\n', encoding="utf-8")

    pubspec = tmp_path / "pubspec.yaml"
    pubspec.write_text(f"name: app\nversion: 0.0.0+{pubspec_build}\n", encoding="utf-8")

    monkeypatch.setattr(sync_shared_assets, "VERSION_SOURCE", version_source)
    monkeypatch.setattr(sync_shared_assets, "APP_CONSTANTS_PATH", app_constants)
    monkeypatch.setattr(sync_shared_assets, "WORKER_PATH", worker)
    monkeypatch.setattr(sync_shared_assets, "WEB_APP_JS_PATH", web_app_js)
    monkeypatch.setattr(sync_shared_assets, "WEB_HTML_PATHS", (app_html, index_html))
    monkeypatch.setattr(sync_shared_assets, "PUBSPEC_PATH", pubspec)
    return {
        "app_constants": app_constants,
        "worker": worker,
        "web_app_js": web_app_js,
        "app_html": app_html,
        "index_html": index_html,
        "pubspec": pubspec,
    }


def test_version_sync_propagates_to_every_platform(tmp_path, monkeypatch):
    paths = _write_version_fixture(tmp_path, monkeypatch, version="1.2.3", pubspec_build=5)

    assert sync_shared_assets.sync_version(check=True) != ()
    sync_shared_assets.sync_version()
    assert sync_shared_assets.sync_version(check=True) == ()

    assert 'APP_RELEASE_NAME = "1.2.3"' in paths["app_constants"].read_text(encoding="utf-8")
    assert 'const APP_VERSION = "1.2.3";' in paths["worker"].read_text(encoding="utf-8")
    assert (
        'const WEB_APP_VERSION_FALLBACK = "1.2.3";'
        in paths["web_app_js"].read_text(encoding="utf-8")
    )
    assert '"softwareVersion": "1.2.3"' in paths["app_html"].read_text(encoding="utf-8")
    assert '"softwareVersion": "1.2.3"' in paths["index_html"].read_text(encoding="utf-8")
    # The build number after the '+' must increment past whatever it was before.
    assert "version: 1.2.3+6" in paths["pubspec"].read_text(encoding="utf-8")


def test_version_sync_is_a_noop_when_already_current(tmp_path, monkeypatch):
    _write_version_fixture(tmp_path, monkeypatch, version="2.0.0", pubspec_build=1)
    sync_shared_assets.sync_version()
    paths_after_first_sync = {
        sync_shared_assets.APP_CONSTANTS_PATH.read_text(encoding="utf-8"),
        sync_shared_assets.PUBSPEC_PATH.read_text(encoding="utf-8"),
    }

    assert sync_shared_assets.sync_version() == ()
    assert {
        sync_shared_assets.APP_CONSTANTS_PATH.read_text(encoding="utf-8"),
        sync_shared_assets.PUBSPEC_PATH.read_text(encoding="utf-8"),
    } == paths_after_first_sync


def test_version_sync_rejects_a_malformed_version_file(tmp_path, monkeypatch):
    version_source = tmp_path / "VERSION"
    version_source.write_text("not-a-version\n", encoding="utf-8")
    monkeypatch.setattr(sync_shared_assets, "VERSION_SOURCE", version_source)

    try:
        sync_shared_assets.sync_version()
    except SystemExit as exc:
        assert "formato X.Y.Z" in str(exc)
    else:
        raise AssertionError("A malformed VERSION file must be rejected")
