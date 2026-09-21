from pathlib import Path

from scripts.patch_native_geofencing import (
    EXTENSION_LINE,
    IMPORT_LINE,
    PACKAGE_NAME,
    patch_main,
    patch_pubspec,
)


def test_patch_pubspec_adiciona_dependencia_local_uma_vez(tmp_path):
    pubspec = tmp_path / "pubspec.yaml"
    pubspec.write_text(
        "name: app\ndependencies:\n  flutter:\n    sdk: flutter\n",
        encoding="utf-8",
    )

    patch_pubspec(pubspec)
    patch_pubspec(pubspec)

    texto = pubspec.read_text(encoding="utf-8")
    assert texto.count(f"{PACKAGE_NAME}:") == 1
    assert f"path: ../../native/{PACKAGE_NAME}" in texto


def test_patch_main_registra_extensao_uma_vez(tmp_path):
    main = tmp_path / "main.dart"
    main.write_text(
        "import 'package:flet/flet.dart';\n\n"
        "const bool isProduction = false;\n"
        "void main() {\n"
        "  List<FletExtension> extensions = [\n"
        "    FletCoreExtension(),\n"
        "  ];\n"
        "}\n",
        encoding="utf-8",
    )

    patch_main(main)
    patch_main(main)

    texto = main.read_text(encoding="utf-8")
    assert texto.count(IMPORT_LINE) == 1
    assert texto.count(EXTENSION_LINE.strip()) == 1
