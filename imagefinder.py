import os
import sys
from PIL import Image
import imagehash
from collections import defaultdict
from pathlib import Path


def get_image_hash(image_path, hash_size=8):
    """
    Calculate perceptual hash of an image.
    Uses average hash which is resistant to minor changes.
    """
    try:
        with Image.open(image_path) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")
            return imagehash.average_hash(img, hash_size=hash_size)
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None


def hamming_distance(hash1, hash2):
    """Calculate the Hamming distance between two hashes."""
    return hash1 - hash2


def find_duplicate_images(folder_path, similarity_threshold=5):
    """
    Find duplicate images in a folder based on perceptual hashing.

    Args:
        folder_path: Path to the folder to search
        similarity_threshold: Maximum Hamming distance for considering images as duplicates
                            (0 = identical, lower = more strict, higher = more lenient)
                            Recommended: 0-5 for very similar, 5-10 for similar

    Returns:
        Dictionary mapping original files to their duplicates
    """
    # Supported image extensions
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}

    image_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if Path(file).suffix.lower() in image_extensions:
                image_files.append(os.path.join(root, file))

    print(f"Found {len(image_files)} image files to process...")

    file_hashes = {}
    for i, image_path in enumerate(image_files, 1):
        if i % 10 == 0:
            print(f"Processing {i}/{len(image_files)}...")
        img_hash = get_image_hash(image_path)
        if img_hash is not None:
            file_hashes[image_path] = img_hash

    print(f"Successfully processed {len(file_hashes)} images.")

    duplicates = defaultdict(list)
    processed = set()

    file_list = list(file_hashes.items())

    for i, (file1, hash1) in enumerate(file_list):
        if file1 in processed:
            continue

        for file2, hash2 in file_list[i + 1 :]:
            if file2 in processed:
                continue

            distance = hamming_distance(hash1, hash2)

            if distance <= similarity_threshold:
                duplicates[file1].append((file2, distance))
                processed.add(file2)

    return duplicates


def get_file_size(file_path):
    """Get file size in bytes."""
    return os.path.getsize(file_path)


def delete_duplicates(duplicates, interactive=True):
    """
    Delete duplicate images, keeping the first/original one.

    Args:
        duplicates: Dictionary mapping original files to their duplicates
        interactive: If True, ask for confirmation before deleting
    """
    total_duplicates = sum(len(dupes) for dupes in duplicates.values())

    if total_duplicates == 0:
        print("\nNo duplicate images found!")
        return

    print(
        f"\nFound {total_duplicates} duplicate images across {len(duplicates)} groups."
    )
    print("\nDuplicate groups:")
    print("-" * 80)

    files_to_delete = []

    for original, dupes in duplicates.items():
        print(f"\nOriginal: {original}")
        print(f"  Size: {get_file_size(original)} bytes")
        print(f"  Duplicates ({len(dupes)}):")

        for dupe_path, distance in dupes:
            print(f"    - {dupe_path}")
            print(f"      Size: {get_file_size(dupe_path)} bytes")
            print(f"      Similarity distance: {distance}")
            files_to_delete.append(dupe_path)

    print("\n" + "=" * 80)

    if interactive:
        response = (
            input(f"\nDelete {len(files_to_delete)} duplicate files? (yes/no): ")
            .strip()
            .lower()
        )
        if response not in ["yes", "y"]:
            print("Deletion cancelled.")
            return

    deleted_count = 0
    total_size_freed = 0

    for file_path in files_to_delete:
        try:
            file_size = get_file_size(file_path)
            os.remove(file_path)
            deleted_count += 1
            total_size_freed += file_size
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

    print(f"\n" + "=" * 80)
    print(f"Successfully deleted {deleted_count} duplicate files.")
    print(f"Total space freed: {total_size_freed / (1024*1024):.2f} MB")


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python imagefinder.py <folder_path> [similarity_threshold] [--auto]"
        )
        print("\nArguments:")
        print("  folder_path: Path to the folder containing images")
        print(
            "  similarity_threshold: (Optional) Max distance for duplicates (0-10, default=5)"
        )
        print("                       Lower = stricter, Higher = more lenient")
        print("  --auto: Skip confirmation prompt and delete automatically")
        print("\nExamples:")
        print("  python imagefinder.py C:\\Photos")
        print("  python imagefinder.py C:\\Photos 3")
        print("  python imagefinder.py C:\\Photos 5 --auto")
        sys.exit(1)

    folder_path = sys.argv[1]

    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        sys.exit(1)

    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a directory.")
        sys.exit(1)

    # Parse optional arguments
    similarity_threshold = 5
    interactive = True

    for arg in sys.argv[2:]:
        if arg == "--auto":
            interactive = False
        else:
            try:
                similarity_threshold = int(arg)
            except ValueError:
                print(
                    f"Warning: Invalid similarity threshold '{arg}', using default (5)"
                )

    print(f"Scanning folder: {folder_path}")
    print(f"Similarity threshold: {similarity_threshold}")
    print(f"Mode: {'Automatic' if not interactive else 'Interactive'}")
    print("=" * 80)

    duplicates = find_duplicate_images(folder_path, similarity_threshold)

    delete_duplicates(duplicates, interactive)


if __name__ == "__main__":
    main()

