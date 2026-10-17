# Image Duplicate Finder v2

Find byte-identical image files and optionally report visually similar images.
Requires Python 3.10 or newer.

## Usage

Default scans only report results and never change image files:

```sh
python imagefinder.py "C:\Photos"
python imagefinder.py "C:\Photos" --report results.json
```

Exact duplicate detection uses streaming SHA-256 and does not require extra packages.
It examines supported image extensions; it does not validate image decoding in exact mode.
The lexicographically first path is kept, making selection repeatable.

To review visual similarity, install the optional dependencies:

```sh
python -m pip install -r requirements.txt
python imagefinder.py "C:\Photos" --visual --threshold 5
```

Visual candidates use a 64-bit perceptual hash with EXIF orientation normalization.
Distances range from 0 to 64; lower is stricter. Even distance zero does not prove
identical content. Different byte content is always treated as review-only.
Animated and multipage images are excluded from visual matching, but still checked
for exact duplication. Visual matching currently compares all unique image pairs
and can be slow on large collections.

## Recoverable cleanup

```sh
python imagefinder.py "C:\Photos" --quarantine
```

Only exact copies are moved. Visual candidates are never moved.
Each run creates a unique folder inside `.imagefinder-quarantine`, excluded from
future scans. Files and their keepers are hashed again before each move to catch
changes since the scan. Avoid modifying the collection while cleanup runs.

The run's `manifest.json` records original paths, quarantine paths and SHA-256.
To restore a file, move its recorded quarantine path back to its original path,
after checking that the original path is unoccupied. An interrupted move may leave
a manifest entry whose original file still exists; check both paths before restoring.
Quarantine preserves the files and does not free disk space.

## Compatibility

v2 replaces the positional threshold with `--threshold`.
The old `--auto` permanent deletion option is removed.
JSON reports are created exclusively, so an existing report is never overwritten.
Unreadable files are listed in the report's `errors` array.

## Tests

```sh
python -m unittest discover -s tests -v
```
