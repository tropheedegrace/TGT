"""Create and rotate consistent SQLite backups for UzaApp."""

from __future__ import annotations

import argparse
from contextlib import closing
import sqlite3
import os
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = Path(os.environ.get("UZAA_DATABASE_PATH", BASE_DIR / "data" / "uzaapp.sqlite3"))
BACKUP_DIR = Path(os.environ.get("UZAA_BACKUP_DIR", BASE_DIR / "backups"))


def create_backup(output_dir: Path, keep: int) -> Path:
    if keep < 1:
        raise ValueError("La rétention doit conserver au moins une sauvegarde.")
    if not DATABASE_PATH.is_file():
        raise FileNotFoundError(f"Base introuvable : {DATABASE_PATH}")

    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    destination = output_dir / f"uzaapp-{timestamp}.sqlite3"
    source_uri = f"{DATABASE_PATH.resolve().as_uri()}?mode=ro"

    with closing(sqlite3.connect(source_uri, uri=True)) as source:
        with closing(sqlite3.connect(destination)) as backup:
            source.backup(backup)
            result = backup.execute("PRAGMA quick_check").fetchone()[0]
            if result != "ok":
                raise sqlite3.DatabaseError(f"Vérification de sauvegarde échouée : {result}")

    try:
        destination.chmod(0o600)
    except OSError:
        pass

    backups = sorted(output_dir.glob("uzaapp-*.sqlite3"), key=lambda item: item.name, reverse=True)
    for old_backup in backups[keep:]:
        old_backup.unlink()
    return destination


def restore_backup(source_path: Path, output_dir: Path, keep: int) -> Path:
    source_path = source_path.resolve()
    if not source_path.is_file():
        raise FileNotFoundError(f"Sauvegarde introuvable : {source_path}")
    if source_path == DATABASE_PATH.resolve():
        raise ValueError("La sauvegarde ne peut pas être la base active.")

    source_uri = f"{source_path.as_uri()}?mode=ro"
    with closing(sqlite3.connect(source_uri, uri=True)) as source:
        result = source.execute("PRAGMA quick_check").fetchone()[0]
        if result != "ok":
            raise sqlite3.DatabaseError(f"Sauvegarde invalide : {result}")

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    before_restore = None
    if DATABASE_PATH.is_file():
        before_restore = create_backup(output_dir, keep)

    temporary_path = DATABASE_PATH.with_name(f"{DATABASE_PATH.name}.restore.tmp")
    temporary_path.unlink(missing_ok=True)
    try:
        with closing(sqlite3.connect(source_uri, uri=True)) as source:
            with closing(sqlite3.connect(temporary_path)) as restored:
                source.backup(restored)
                result = restored.execute("PRAGMA quick_check").fetchone()[0]
                if result != "ok":
                    raise sqlite3.DatabaseError(f"Vérification de restauration échouée : {result}")
        os.replace(temporary_path, DATABASE_PATH)
    finally:
        temporary_path.unlink(missing_ok=True)
    return before_restore or DATABASE_PATH


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=BACKUP_DIR)
    parser.add_argument("--keep", type=int, default=30)
    parser.add_argument("--restore", type=Path, help="restaurer cette sauvegarde (arrêter le serveur avant)")
    args = parser.parse_args()
    if args.restore:
        print(f"Base restaurée. Copie préalable : {restore_backup(args.restore, args.output_dir, args.keep)}")
    else:
        print(create_backup(args.output_dir, args.keep))


if __name__ == "__main__":
    main()