"""Find exact image duplicates and optional visual review candidates."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import uuid

EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff", ".webp"}


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def scan(folder, visual=False, threshold=5):
    root = Path(folder).resolve()
    if not root.is_dir():
        raise ValueError("Scan path must be a directory")
    if not 0 <= threshold <= 64:
        raise ValueError("Threshold must be between 0 and 64")
    if visual:
        from PIL import Image, ImageOps
        import imagehash
    files = []
    errors = []
    for directory, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d != ".imagefinder-quarantine"
                         and not (Path(directory) / d).is_symlink())
        for name in sorted(names):
            path = Path(directory) / name
            if path.suffix.lower() in EXTENSIONS and not path.is_symlink():
                files.append(path)
    groups = {}
    hashes = []
    candidates = []
    for path in sorted(files):
        try:
            fingerprint = digest(path)
        except OSError as error:
            errors.append({"path": str(path), "error": str(error)})
            continue
        if fingerprint in groups:
            groups[fingerprint]["duplicates"].append(str(path))
            continue
        groups[fingerprint] = {"keeper": str(path), "sha256": fingerprint,
                               "duplicates": []}
        if visual:
            try:
                with Image.open(path) as image:
                    # Comparing only one frame could hide different animations/pages.
                    if getattr(image, "n_frames", 1) > 1:
                        continue
                    value = imagehash.phash(ImageOps.exif_transpose(image).convert("RGB"))
                for other, other_hash in hashes:
                    distance = value - other_hash
                    if distance <= threshold:
                        candidates.append({"first": str(other), "second": str(path),
                                           "distance": distance})
                hashes.append((path, value))
            except Exception as error:
                errors.append({"path": str(path), "error": str(error)})
    return {"root": str(root),
            "exact_groups": [group for group in groups.values() if group["duplicates"]],
            "visual_candidates": candidates, "errors": errors}


def quarantine(report):
    """Move verified exact copies into a unique run folder with a recovery manifest."""
    root = Path(report["root"]).resolve()
    base = root / ".imagefinder-quarantine"
    if base.is_symlink():
        raise ValueError("Quarantine directory must not be a symlink")
    base.mkdir(exist_ok=True)
    run = base / uuid.uuid4().hex
    run.mkdir()
    manifest = run / "manifest.json"
    moves = []
    for group in report["exact_groups"]:
        keeper = Path(group["keeper"])
        for filename in group["duplicates"]:
            source = Path(filename)
            for path in (keeper, source):
                if path.is_symlink() or not path.resolve().is_relative_to(root):
                    raise ValueError("File is a symlink or outside the scan folder")
            if source.resolve() == keeper.resolve():
                raise ValueError("Cannot quarantine the keeper")
            if digest(keeper) != group["sha256"] or digest(source) != group["sha256"]:
                raise ValueError("File changed since scanning; scan again")
            destination = run / str(len(moves))
            entry = {"original": str(source), "quarantined": str(destination),
                     "sha256": group["sha256"]}
            # Record the intended move first, so interrupted runs remain recoverable.
            moves.append(entry)
            temporary = run / "manifest.tmp"
            temporary.write_text(json.dumps(moves, indent=2), encoding="utf-8")
            temporary.replace(manifest)
            source.rename(destination)
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--visual", action="store_true",
                        help="Also report perceptually similar images (never moved)")
    parser.add_argument("--threshold", type=int, default=5)
    parser.add_argument("--report", type=Path, help="Write a JSON report to a new file")
    parser.add_argument("--quarantine", action="store_true",
                        help="Move exact copies to .imagefinder-quarantine")
    args = parser.parse_args(argv)
    if not args.folder.is_dir():
        parser.error("folder must be an existing directory")
    if not 0 <= args.threshold <= 64:
        parser.error("--threshold must be between 0 and 64")
    try:
        report = scan(args.folder, args.visual, args.threshold)
        if args.report:
            with args.report.open("x", encoding="utf-8") as stream:
                json.dump(report, stream, indent=2)
        print(json.dumps(report, indent=2))
        if args.quarantine and report["exact_groups"]:
            print(f"Recovery manifest: {quarantine(report)}")
    except (OSError, ValueError, ImportError) as error:
        parser.exit(1, f"Error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
