#!/usr/bin/env python3
"""Сборка пакета обновления AFTERDAY для игрового лаунчера."""
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

# В архив попадают только файлы, необходимые игроку для работы клиента и сервера.
ШАБЛОНЫ_ФАЙЛОВ = (
    "cliente/*.py", "cliente/*.js",
    "launcher/*.py", "launcher/*.bat",
    "host/servidor_host.py", "host/carregar_script_no_host.py",
    "host/scripts/*.js", "host/ferramentas/*.js",
    "host_otimizado/servidor_host.py", "host_otimizado/carregar_script_no_host.py",
    "host_otimizado/scripts/*.js", "host_otimizado/ferramentas/*.js",
)

# Эти файлы содержат настройки конкретного пользователя или владельца сервера.
ЗАЩИЩЁННЫЕ_ФАЙЛЫ = {
    "cliente/host.txt", "cliente/steamid.txt",
    "launcher/config.json", "launcher/versao.txt",
    "launcher/publicar_versao.py",
}
РАЗРЕШЁННЫЕ_ПАПКИ = ("cliente/", "launcher/", "host/", "host_otimizado/")


def sha256(данные: bytes) -> str:
    """Возвращает SHA-256 для переданных данных."""
    return hashlib.sha256(данные).hexdigest()


def безопасный_путь(путь: str) -> bool:
    путь = путь.replace("\\", "/")
    if путь.startswith("/") or ":" in путь or ".." in путь.split("/"):
        return False
    return путь.startswith(РАЗРЕШЁННЫЕ_ПАПКИ) and путь not in ЗАЩИЩЁННЫЕ_ФАЙЛЫ


def собрать_список_файлов() -> list[Path]:
    файлы: set[Path] = set()
    for шаблон in ШАБЛОНЫ_ФАЙЛОВ:
        файлы.update(
            файл for файл in ROOT.glob(шаблон)
            if файл.is_file() and not файл.is_symlink()
        )
    return sorted(файлы, key=lambda файл: файл.relative_to(ROOT).as_posix())


def main() -> int:
    parser = argparse.ArgumentParser(description="Сборка архива обновления AFTERDAY.")
    parser.add_argument("версия", help="Номер версии, например 2026.11.10-1")
    parser.add_argument("--notes", default="", help="Описание изменений для релиза")
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9._-]{1,80}", args.версия):
        parser.error("В номере версии допустимы только латинские буквы, цифры, точка, дефис и подчёркивание.")

    файлы = собрать_список_файлов()
    if not файлы:
        raise SystemExit("Не найдено файлов для обновления. Сначала добавьте разрешённые исходники проекта.")

    папка_релиза = ROOT / "dist" / args.версия
    if папка_релиза.exists():
        shutil.rmtree(папка_релиза)
    папка_релиза.mkdir(parents=True)

    контрольные_суммы: dict[str, str] = {}
    путь_архива = папка_релиза / "atualizacao.zip"

    with zipfile.ZipFile(путь_архива, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as архив:
        for файл in файлы:
            относительный_путь = файл.relative_to(ROOT).as_posix()
            if not безопасный_путь(относительный_путь):
                continue
            данные = файл.read_bytes()
            контрольные_суммы[относительный_путь] = sha256(данные)
            архив.writestr(относительный_путь, данные)

    манифест = {
        "versao": args.версия,
        "zip": "atualizacao.zip",
        "zip_sha256": sha256(путь_архива.read_bytes()),
        "arquivos": контрольные_суммы,
        "notas": args.notes,
        "gerado_em": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
    }

    (папка_релиза / "manifesto.json").write_text(
        json.dumps(манифест, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Готово! В версию {args.версия} добавлено файлов: {len(контрольные_суммы)}")
    print(f"Папка релиза: {папка_релиза}")
    print(f"SHA-256 архива: {манифест['zip_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
