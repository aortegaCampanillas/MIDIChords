from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_JS = (PROJECT_ROOT / "apps" / "web" / "static" / "app.js").read_text(
    encoding="utf-8"
)


def test_chord_generation_modes_reset_the_guitar_variant_for_a_new_chord() -> None:
    reset = (
        "const chordChanged = guitarVariationChordKey(state.generatedChord) "
        "!== guitarVariationChordKey(out);"
    )
    assignment = "if (chordChanged) state.guitarSelectedVariationIdx = 0;"

    assert APP_JS.count(reset) == 2
    assert APP_JS.count(assignment) == 2


def test_guitar_variant_identity_includes_root_suffix_and_inversion() -> None:
    function_start = APP_JS.index("function guitarVariationChordKey(chord)")
    function_end = APP_JS.index("\n}\n", function_start)
    function_source = APP_JS[function_start:function_end]

    assert "chord.root_pc" in function_source
    assert "chord.suffix" in function_source
    assert "chord.inversion" in function_source
