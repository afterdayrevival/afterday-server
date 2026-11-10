#!/usr/bin/env python3
"""Build updater-compatible AFTERDAY release assets."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = (
    "cliente/*.py", "cliente/*.js",
    "launcher/*.py", "launcher/*.bat",
    "host/servidor_host.py", "host/carregar_script_no_host.py",
    "host/scripts/*.js", "host/ferramentas/*.js",
    "host_otimizado/servidor_host.py", "host_otimizado/carregar_script_no_host.py",
    "host_otimizado/scripts/*.js", "host_otimizado/ferramentas/*.js",
)
PROTECTED = {
    "cliente/host.txt", "cliente/steamid.txt",
    "launcher/config.json", "launcher/versao.txt",
    "launcher/publicar_versao.py",
}
ALLOWED_PREFIXES = ("cliente/", "launcher/", "host/", "host_otimizado/")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_path(rel: str) -> bool:
    rel = rel.replace("\\", "/")
    if rel.startswith("/") or ":" in rel or ".." in rel.split("/"):
        return False
    return rel.startswith(ALLOWED_PREFIXES) and rel not in PROTECTED


def collect_files() -> list[Path]:
    files: set[Path] = set()
    for pattern in PATTERNS:
        files.update(p for p in ROOT.glob(pattern) if p.is_file() and not p.is_symlink())
    return sorted(files, key=lambda p: p.relative_to(ROOT).as_posix())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("version", help="Release version, e.g. 2026.11.10-1")
    parser.add_argument("--notes", default="", help="Release notes")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,80}", args.version):
        parser.error("version may contain only letters, numbers, dot, underscore and hyphen")

    files = collect_files()
    if not files:
        raise SystemExit("No distributable files found; add authorized client/launcher/server source first.")

    out_dir = ROOT / "dist" / args.version
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    hashes: dict[str, str] = {}
    zip_path = out_dir / "atualizacao.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            rel = path.relative_to(ROOT).as_posix()
            if not safe_path(rel):
                continue
            data = path.read_bytes()
            hashes[rel] = sha256(data)
            archive.writestr(rel, data)

    manifest = {
        "versao": args.version,
        "zip": "atualizacao.zip",
        "zip_sha256": sha256(zip_path.read_bytes()),
        "arquivos": hashes,
        "notas": args.notes,
        "gerado_em": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
    }
    (out_dir / "manifesto.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Built {len(hashes)} files for {args.version}: {out_dir}")
    print(f"ZIP SHA-256: {manifest['zip_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
