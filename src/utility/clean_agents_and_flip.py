from pathlib import Path

import cv2
from cv2.typing import MatLike


def process_agent_icons() -> bool:
    """Process transparent agent icons: grayscale, resize, and mirror."""
    PROJECT_ROOT = Path(__file__).parent.parent
    RAW_DIR = PROJECT_ROOT / "assets" / "agent_icons_raw"
    CLEAN_DIR = PROJECT_ROOT / "assets" / "agent_icons_clean"

    # Ensure output directory and its __init__.py exist
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / "__init__.py").touch(exist_ok=True)
    (CLEAN_DIR / "__init__.py").touch(exist_ok=True)

    if not RAW_DIR.exists():
        print(f"❌ Raw icons directory not found at {RAW_DIR}")
        return

    existing_clean = {f.name for f in CLEAN_DIR.glob(pattern="*.webp")}

    for img_path in RAW_DIR.glob(pattern="*.webp"):
        base_name = img_path.name
        mirrored_name = f"Mirrored_{base_name}"

        if base_name in existing_clean and mirrored_name in existing_clean:
            print(f"⏩ Already exists: {base_name} (skipped)")
            continue

        img = cv2.imread(filename=str(img_path), flags=cv2.IMREAD_UNCHANGED)
        if img is None or img.shape[2] != 4:
            print(f"⚠️ Failed to load or invalid format: {img_path.name}")
            continue

        # Process original
        processed = standardize_image(img=img)
        if base_name not in existing_clean:
            _ = cv2.imwrite(
                filename=str(CLEAN_DIR / base_name),
                img=processed,
                params=[cv2.IMWRITE_WEBP_QUALITY, 90],
            )
            print(f"✅ Created: {base_name}")

        # Process mirrored
        if mirrored_name not in existing_clean:
            mirrored = cv2.flip(src=processed, flipCode=1)
            _ = cv2.imwrite(
                filename=str(CLEAN_DIR / mirrored_name),
                img=mirrored,
                params=[cv2.IMWRITE_WEBP_QUALITY, 90],
            )
            print(f"✅ Created: {mirrored_name}")


def standardize_image(img: MatLike) -> MatLike:
    """Convert to grayscale while preserving alpha, then resize to 40x40."""
    bgr = img[:, :, :3]
    alpha = img[:, :, 3]

    gray = cv2.cvtColor(src=bgr, code=cv2.COLOR_BGR2GRAY)
    gray_rgb = cv2.merge(mv=[gray, gray, gray])
    result = cv2.merge(mv=[gray_rgb, alpha])

    return cv2.resize(src=result, dsize=(40, 40), interpolation=cv2.INTER_AREA)


if __name__ == "__main__":
    print("🔄 Processing agent icons...")
    print("✨ All done!") if process_agent_icons() else print("❌ Failure!")

