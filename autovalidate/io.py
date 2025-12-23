import shutil
from pathlib import Path
from typing import Iterable, List, Tuple


def move_files_by_keyword(
    source_folder: str | Path,
    destination_folder: str | Path,
    keywords: Iterable[str],
    *,
    confirm: bool = True,
) -> List[Path]:
    """
    Copy files whose name contains any keyword from source_folder to
    destination_folder. If confirm is True, ask once before copying.
    Returns the list of copied paths.
    """
    source = Path(source_folder)
    dest = Path(destination_folder)
    dest.mkdir(parents=True, exist_ok=True)

    planned: List[Tuple[Path, Path]] = []
    for p in source.rglob("*"):
        if p.is_file() and any(k in p.name for k in keywords):
            target = dest / p.name
            planned.append((p, target))

    if not planned:
        print("No files matched the given keywords.")
        return []

    for src, dst in planned:
        print(f"Would copy: {src} -> {dst}")

    if confirm:
        user_input = input("Do you want to COPY all these files? [y/N]: ").strip().lower()
        if user_input not in ("y", "yes"):
            print("Aborting, no files copied.")
            return []

    copied: List[Path] = []
    for src, dst in planned:
        shutil.copy2(src, dst)
        copied.append(dst)

    print(f"Copied {len(copied)} files.")
    return copied
