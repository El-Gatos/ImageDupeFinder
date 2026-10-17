# 🔎 Image Duplicate Finder

**Find duplicate photos. Review similar images. Keep cleanup recoverable.**

A small Python command-line tool for sorting out image collections.
Scan a folder and its subfolders, review the results, then optionally move exact
copies into quarantine.

**Python 3.10+** · **Report-only by default** · **Optional visual matching**

[Quick start](#quick-start) · [Visual matching](#visual-matching) · [Cleanup & recovery](#cleanup--recovery) · [Command reference](#command-reference)

---

## At a glance

| Feature | What it does |
| :--- | :--- |
| 🔍 Exact duplicates | Finds files with identical SHA-256 fingerprints |
| 🖼️ Visual review | Flags images that look similar, including resized or re-encoded copies |
| 📁 Recursive scanning | Searches the selected folder and its subfolders |
| 📄 JSON reports | Saves results for later review |
| 📦 Recoverable cleanup | Moves exact copies into quarantine with a recovery manifest |

> [!TIP]
> Start with a plain scan. It reports results without moving or deleting your images.

## Quick start

### 1. Get the project

Install [Python 3.10 or newer](https://www.python.org/downloads/), then download
this repository using **Code → Download ZIP** and extract it, or clone it:

```sh
git clone https://github.com/El-Gatos/ImageDupeFinder.git
cd ImageDupeFinder
```

Open a terminal in the project folder. Exact duplicate scanning needs **no extra packages**.

### 2. Scan your photos

Replace the example path with your own folder:

```sh
python imagefinder.py "C:\Photos"
```

Results appear in the terminal as JSON. Your images stay where they are.

### 3. Save a report

```sh
python imagefinder.py "C:\Photos" --report results.json
```

Use a new filename each time—existing reports are never overwritten.

## Visual matching

Want to find photos that look alike but have different file contents?
Install the optional dependencies:

```sh
python -m pip install -r requirements.txt
```

Then run:

```sh
python imagefinder.py "C:\Photos" --visual --threshold 5
```

| Match type | Meaning | Eligible for quarantine? |
| :--- | :--- | :---: |
| **Exact duplicate** | Same SHA-256 file fingerprint | Yes |
| **Visual candidate** | Similar perceptual image hash | No |

The visual threshold accepts **0–64**, with **5** as the default.
Lower values are stricter; higher values return more candidates.
Even a visual distance of **0** does not prove that two files are identical.

> [!NOTE]
> Visual results are review suggestions. They are never moved by cleanup.

## Cleanup & recovery

### Move exact copies into quarantine

After reviewing a scan, run:

```sh
python imagefinder.py "C:\Photos" --quarantine
```

For each exact duplicate group, the tool keeps the first path in sorted order
and moves the other copies into a unique run folder under
`.imagefinder-quarantine`. It checks the keeper and each copy again before moving.

- **No permanent deletion:** quarantined files remain on disk.
- **Recovery record:** each run includes a `manifest.json` with original paths,
  quarantine paths, and SHA-256 fingerprints.
- **Clean rescans:** quarantine folders are excluded from future scans.

### Restore a quarantined file

1. Open the run's `manifest.json`.
2. Find the file's `original` and `quarantined` paths.
3. Check that the original path is unoccupied.
4. Move the quarantined file back to its original path.

Restoration is currently manual.

> [!IMPORTANT]
> Avoid changing the collection while quarantine runs. File checks and moves are
> not atomic. If a run is interrupted, check both recorded paths before restoring:
> a manifest entry may exist even if its move did not complete.
>
> Quarantine does **not** free disk space.

## Command reference

```sh
python imagefinder.py <folder> [--visual] [--threshold 5] [--report results.json] [--quarantine]
```

| Argument | Purpose | Default |
| :--- | :--- | :--- |
| `folder` | Folder to scan, including subfolders | Required |
| `--visual` | Also report visually similar images | Off |
| `--threshold` | Maximum visual hash distance, from 0 to 64 | `5` |
| `--report` | Write a JSON report to a new file | Terminal output only |
| `--quarantine` | Move exact duplicate copies into quarantine | Off |
| `-h`, `--help` | Show command help | — |

### Reading the report

| Field | Contents |
| :--- | :--- |
| `root` | Absolute path of the scanned folder |
| `exact_groups` | Keeper, SHA-256 fingerprint, and duplicate paths for each group |
| `visual_candidates` | Image pairs and their visual hash distances |
| `errors` | File read or image-processing errors encountered |

## Supported formats & current limits

**JPG · JPEG · PNG · BMP · GIF · TIF · TIFF · WebP**

- Exact scans use file contents and extensions; they do not check whether an image
  can be decoded.
- Visual scans normalize EXIF orientation and use a 64-bit perceptual hash.
- Animated and multipage images are checked for exact duplication, but skipped
  for visual matching.
- Visual matching compares every pair of unique images and may be slow on large
  collections. Hash caching and indexed matching are not implemented yet.
- Keeper selection uses sorted paths; it does not rank images by resolution or quality.
