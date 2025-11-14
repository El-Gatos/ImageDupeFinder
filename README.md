# Image Duplicate Finder & Remover

A Python tool that finds and deletes duplicate images based on **visual similarity** rather than just file names or exact byte matching. Uses perceptual hashing to detect images that look nearly identical, even if they've been slightly modified, resized, or saved in different formats.

## Features

- 🔍 **Perceptual Hashing**: Detects visually similar images, not just identical files
- 🎯 **Adjustable Sensitivity**: Configure how strict the similarity matching should be
- 📁 **Recursive Search**: Scans folder and all subfolders automatically
- 🖼️ **Multiple Formats**: Supports JPG, JPEG, PNG, BMP, GIF, TIFF, and WebP
- 🛡️ **Safe Deletion**: Shows preview and asks for confirmation before deleting
- 📊 **Detailed Reports**: Displays file sizes, similarity scores, and space freed
- ⚡ **Batch Processing**: Efficiently processes hundreds or thousands of images

## Installation

1. Make sure Python 3.7+ is installed on your system

2. Install required dependencies:
```bash
pip install Pillow imagehash
```

## Usage

### Basic Usage (Interactive Mode)
```bash
python imagefinder.py "C:\path\to\folder"
```
This will scan the folder, show you all duplicates found, and ask for confirmation before deleting.

### Custom Similarity Threshold
```bash
python imagefinder.py "C:\path\to\folder" 3
```
The threshold value (0-10) controls how strict the matching is:
- **0-2**: Only nearly identical images (very strict)
- **3-5**: Very similar images (recommended, default is 5)
- **6-10**: Similar images with more variation allowed (more lenient)

### Automatic Mode (No Confirmation)
```bash
python imagefinder.py "C:\path\to\folder" 5 --auto
```
Use the `--auto` flag to skip the confirmation prompt and delete automatically.

## How It Works

1. **Scanning**: The program recursively scans the specified folder for all image files
2. **Hashing**: Each image is converted to a perceptual hash (a fingerprint of its visual content)
3. **Comparison**: Images are compared using Hamming distance between their hashes
4. **Grouping**: Similar images (within the threshold) are grouped together
5. **Selection**: The first image in each group is kept as the "original"
6. **Deletion**: All other images in the group are marked as duplicates and deleted

## Example Output

```
Scanning folder: C:\Photos
Similarity threshold: 5
Mode: Interactive
================================================================================
Found 150 image files to process...
Processing 10/150...
Processing 20/150...
...
Successfully processed 150 images.

Found 23 duplicate images across 8 groups.

Duplicate groups:
--------------------------------------------------------------------------------

Original: C:\Photos\vacation\beach1.jpg
  Size: 2456789 bytes
  Duplicates (3):
    - C:\Photos\vacation\beach1_copy.jpg
      Size: 2456789 bytes
      Similarity distance: 0
    - C:\Photos\backup\beach1_edited.jpg
      Size: 2398456 bytes
      Similarity distance: 3
    - C:\Photos\beach1_resized.png
      Size: 1234567 bytes
      Similarity distance: 4

...

================================================================================
Delete 23 duplicate files? (yes/no): yes

Deleted: C:\Photos\vacation\beach1_copy.jpg
Deleted: C:\Photos\backup\beach1_edited.jpg
...

================================================================================
Successfully deleted 23 duplicate files.
Total space freed: 45.67 MB
```

## Command Reference

```bash
python imagefinder.py <folder_path> [similarity_threshold] [--auto]
```

**Arguments:**
- `folder_path` (required): Path to the folder containing images
- `similarity_threshold` (optional): Maximum distance for duplicates (0-10, default=5)
- `--auto` (optional): Skip confirmation prompt and delete automatically

## Important Notes

⚠️ **Warning**: Deleted files are permanently removed and cannot be recovered from this tool. Always backup important files before running in automatic mode.

💡 **Tip**: Start with a low threshold (3-4) on a test folder to see how the program works before processing important photo collections.

🎯 **Best Practice**: The default threshold of 5 works well for most use cases - it catches duplicates while avoiding false positives.

## Use Cases

- Remove duplicate photos from camera uploads
- Clean up backup folders with mixed original and edited versions
- Deduplicate image collections after merging multiple sources
- Organize photo libraries by removing redundant copies

## Technical Details

- Uses **Average Hash (aHash)** algorithm for perceptual hashing
- Hamming distance measures similarity between hashes
- Images are converted to RGB before hashing for consistency
- Progress updates shown every 10 images during processing

## Troubleshooting

**"Error processing [file]"**: Some image files may be corrupted or in an unsupported format. The program will skip these and continue.

**Too many/few duplicates found**: Adjust the similarity threshold. Lower values are more strict, higher values are more lenient.

**Program runs slowly**: This is normal for large image collections. Processing time depends on the number and size of images.

## License

Free to use and modify for personal or commercial projects.
