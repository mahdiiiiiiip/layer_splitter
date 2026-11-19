"""
Layer Splitter
--------------
Extracts separate visible elements from transparent raster images and saves
each element as an individual PNG file.

Place source images in the INPUT folder and run this script.
"""

from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError
from scipy import ndimage


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "INPUT"
OUTPUT_DIR = BASE_DIR / "OUTPUT"

# Pixels with alpha values greater than this threshold are treated as visible.
# Valid range: 0-254.
ALPHA_THRESHOLD = 10

# Join nearby elements by expanding the visibility mask before detection.
# Set to 0 to keep separate elements apart. Larger values join elements that
# are closer together. The value is measured in pixels.
MERGE_DISTANCE = 0

# Ignore detected elements containing fewer visible pixels than this value.
MIN_AREA = 20

# Add transparent space around each exported element, measured in pixels.
PADDING = 0

SUPPORTED_EXTENSIONS = {".png", ".webp", ".tif", ".tiff"}


def validate_settings():
    """Check configuration values before processing images."""
    if not 0 <= ALPHA_THRESHOLD <= 254:
        raise ValueError("ALPHA_THRESHOLD must be between 0 and 254.")
    if MERGE_DISTANCE < 0:
        raise ValueError("MERGE_DISTANCE cannot be negative.")
    if MIN_AREA < 0:
        raise ValueError("MIN_AREA cannot be negative.")
    if PADDING < 0:
        raise ValueError("PADDING cannot be negative.")


def split_image(image_path: Path) -> int:
    """Extract visible connected components from one image.

    Returns the number of elements successfully saved.
    """
    with Image.open(image_path) as source:
        image = source.convert("RGBA")

    pixels = np.asarray(image)
    alpha = pixels[:, :, 3]
    visible_mask = alpha > ALPHA_THRESHOLD

    if not np.any(visible_mask):
        return 0

    # Expand the mask when merging nearby elements is enabled.
    if MERGE_DISTANCE > 0:
        structure = np.ones((3, 3), dtype=bool)
        detection_mask = ndimage.binary_dilation(
            visible_mask,
            structure=structure,
            iterations=MERGE_DISTANCE,
        )
    else:
        detection_mask = visible_mask

    # 8-connectivity: pixels touching horizontally, vertically, or diagonally
    # are considered part of the same element.
    labels, _ = ndimage.label(
        detection_mask,
        structure=np.ones((3, 3), dtype=bool),
    )
    object_slices = ndimage.find_objects(labels)

    saved_count = 0
    file_stem = image_path.stem

    for component_id, component_slice in enumerate(object_slices, start=1):
        if component_slice is None:
            continue

        component_labels = labels[component_slice]
        original_visible_pixels = visible_mask[component_slice]
        element_mask = (component_labels == component_id) & original_visible_pixels

        if int(np.count_nonzero(element_mask)) < MIN_AREA:
            continue

        y_slice, x_slice = component_slice
        crop = pixels[y_slice, x_slice].copy()

        # Keep only pixels belonging to this detected component. When merging
        # is enabled, the component may contain multiple nearby source shapes.
        if MERGE_DISTANCE > 0:
            keep_mask = component_labels == component_id
        else:
            keep_mask = element_mask

        crop[~keep_mask, 3] = 0
        output_image = Image.fromarray(crop, mode="RGBA")

        if PADDING > 0:
            padded_image = Image.new(
                "RGBA",
                (
                    output_image.width + 2 * PADDING,
                    output_image.height + 2 * PADDING,
                ),
                (0, 0, 0, 0),
            )
            padded_image.paste(output_image, (PADDING, PADDING))
            output_image = padded_image

        saved_count += 1
        output_path = OUTPUT_DIR / f"{file_stem}_{saved_count:03d}.png"
        output_image.save(output_path, format="PNG")

    return saved_count


def main():
    """Process all supported images in the INPUT folder."""
    validate_settings()
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    image_paths = sorted(
        path for path in INPUT_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not image_paths:
        print(f"No supported images found in: {INPUT_DIR}")
        print("Add PNG, WEBP, TIF, or TIFF files to the INPUT folder.")
        return

    total_saved = 0

    for image_path in image_paths:
        try:
            saved_count = split_image(image_path)
            total_saved += saved_count
            print(f"{image_path.name}: {saved_count} element(s) exported")
        except (OSError, UnidentifiedImageError, ValueError) as error:
            print(f"Skipped {image_path.name}: {error}")

    print(f"Finished. Exported {total_saved} element(s) to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
