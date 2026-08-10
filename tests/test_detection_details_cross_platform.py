from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_web_detection_details_toggles_include_behavior_and_contextual_help() -> None:
    html = (PROJECT_ROOT / "apps/web/app.html").read_text(encoding="utf-8")
    app = (PROJECT_ROOT / "apps/web/static/app.js").read_text(encoding="utf-8")
    help_callouts = (
        PROJECT_ROOT / "apps/web/static/help_callouts.js"
    ).read_text(encoding="utf-8")
    texts = (PROJECT_ROOT / "apps/web/static/ui_texts.js").read_text(
        encoding="utf-8"
    )

    for mode in ("detect", "interval"):
        assert f'id="{mode}DetailsToggle"' in html
        assert f'id="{mode}ResultBlock"' in html
        assert f'el("{mode}DetailsToggle")' in app
        assert f'#{mode}DetailsToggle' in help_callouts
    assert "For learning purposes" in texts
    assert "Con fines didácticos" in texts


def test_mobile_detection_details_toggles_include_behavior_and_contextual_help() -> None:
    main = (PROJECT_ROOT / "apps/mobile_flutter/lib/main.dart").read_text(
        encoding="utf-8"
    )
    pages = (
        PROJECT_ROOT / "apps/mobile_flutter/lib/main_pages.dart"
    ).read_text(encoding="utf-8")
    help_catalog = (
        PROJECT_ROOT / "apps/mobile_flutter/lib/main_help.dart"
    ).read_text(encoding="utf-8")

    assert "bool _detectionDetailsVisible = true;" in main
    assert "bool _intervalDetailsVisible = true;" in main
    for help_id in ("detection_details_toggle", "interval_details_toggle"):
        assert f"'{help_id}'" in pages
        assert f"id: '{help_id}'" in help_catalog
    assert "For learning purposes" in help_catalog
    assert "Con fines didácticos" in help_catalog
