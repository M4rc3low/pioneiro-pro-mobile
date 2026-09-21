from __future__ import annotations

import argparse
from pathlib import Path


PACKAGE_NAME = "pioneiro_pro_geofencing"
IMPORT_LINE = (
    "import 'package:pioneiro_pro_geofencing/pioneiro_pro_geofencing.dart' "
    "as pioneiro_pro_geofencing;"
)
EXTENSION_LINE = "    pioneiro_pro_geofencing.Extension(),"


def patch_pubspec(pubspec: Path) -> None:
    text = pubspec.read_text(encoding="utf-8")
    if f"{PACKAGE_NAME}:" in text:
        return

    marker = "dependencies:\n"
    if marker not in text:
        raise RuntimeError("Bloco dependencies não encontrado no pubspec gerado.")

    addition = (
        f"{marker}"
        f"  {PACKAGE_NAME}:\n"
        f"    path: ../../native/{PACKAGE_NAME}\n"
    )
    pubspec.write_text(text.replace(marker, addition, 1), encoding="utf-8")


def patch_main(main_dart: Path) -> None:
    text = main_dart.read_text(encoding="utf-8")

    if IMPORT_LINE not in text:
        marker = "const bool isProduction"
        if marker not in text:
            raise RuntimeError("Ponto de importação do main.dart não encontrado.")
        text = text.replace(marker, f"{IMPORT_LINE}\n\n{marker}", 1)

    if EXTENSION_LINE.strip() not in text:
        marker = "List<FletExtension> extensions = [\n"
        if marker not in text:
            raise RuntimeError("Lista de extensões Flet não encontrada no main.dart.")
        text = text.replace(marker, marker + EXTENSION_LINE + "\n", 1)

    main_dart.write_text(text, encoding="utf-8")


def patch_project(project_root: Path) -> None:
    pubspec = project_root / "pubspec.yaml"
    main_dart = project_root / "lib" / "main.dart"

    if not pubspec.exists():
        raise FileNotFoundError(f"pubspec.yaml não encontrado em {project_root}")
    if not main_dart.exists():
        raise FileNotFoundError(f"main.dart não encontrado em {project_root}")

    patch_pubspec(pubspec)
    patch_main(main_dart)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "project_root",
        nargs="?",
        default="build/flutter",
        help="Diretório do projeto Flutter gerado pelo Flet.",
    )
    args = parser.parse_args()
    patch_project(Path(args.project_root))


if __name__ == "__main__":
    main()
