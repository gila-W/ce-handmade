import json
from pathlib import Path

import rawpy
from PIL import Image, ImageOps

SRC = Path(__file__).parent / "images"
OUT = SRC / "web"
CONFIG = Path(__file__).parent / "orientations.json"
GALLERY_DATA = Path(__file__).parent / "gallery-data.js"
MAX_SIZE = 1200
SUPPORTED = {".jpg", ".jpeg", ".png", ".cr2", ".heic", ".heif"}


def load_orientation_rules() -> dict[str, str | int]:
    if not CONFIG.exists():
        return {}
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    return {
        key: value
        for key, value in data.items()
        if not key.startswith("_")
    }


def is_raw_file(path: Path) -> bool:
    return path.read_bytes()[:4] in {b"II*\x00", b"MM\x00*"}


def load_image(path: Path) -> Image.Image:
    if is_raw_file(path):
        with rawpy.imread(str(path)) as raw:
            rgb = raw.postprocess(
                use_camera_wb=True,
                output_bps=8,
                user_flip=raw.sizes.flip,
            )
        return Image.fromarray(rgb)

    image = Image.open(path)
    return ImageOps.exif_transpose(image)


def is_landscape(image: Image.Image) -> bool:
    return image.width >= image.height


def resolve_rule(rules: dict, stem: str, model_number: int) -> str | int | None:
    keys = [stem, f"{model_number:03d}", str(model_number)]
    for key in keys:
        if key in rules:
            return rules[key]
    return None


def apply_orientation(image: Image.Image, rule: str | int | None) -> Image.Image:
    if rule is None:
        return image

    if isinstance(rule, str):
        normalized = rule.strip().lower()
        if normalized in {"landscape", "מאוזן", "אופקי"}:
            if not is_landscape(image):
                image = image.rotate(-90, expand=True)
        elif normalized in {"portrait", "מאונך", "אנכי"}:
            if is_landscape(image):
                image = image.rotate(-90, expand=True)
        elif normalized.isdigit():
            rule = int(normalized)
        elif "+" in normalized:
            parts = [int(part.strip()) for part in normalized.split("+") if part.strip().isdigit()]
            for degrees in parts:
                if degrees % 360 != 0:
                    image = image.rotate(-degrees, expand=True)
            return image
        else:
            return image

    if isinstance(rule, int) and rule % 360 != 0:
        image = image.rotate(-rule, expand=True)

    return image


def save_web_image(image: Image.Image, destination: Path) -> None:
    image = image.convert("RGB")
    image.thumbnail((MAX_SIZE, MAX_SIZE), Image.LANCZOS)
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, "JPEG", quality=82, optimize=True)


def write_gallery_data(images: list[str]) -> None:
    lines = ["  '" + path + "'," for path in images]
    content = "// קובץ זה נוצר אוטומטית – אל תערכו ידנית\nconst IMAGES = [\n"
    content += "\n".join(lines) + "\n];\n"
    GALLERY_DATA.write_text(content, encoding="utf-8")


def cleanup_stale_outputs(active_stems: set[str]) -> None:
    if not OUT.exists():
        return
    for existing in OUT.glob("*.jpg"):
        if existing.stem not in active_stems:
            existing.unlink()
            print(f"Removed stale {existing.name}")


def main() -> None:
    rules = load_orientation_rules()
    sources = sorted(
        path
        for path in SRC.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED
    )

    active_stems = {src.stem for src in sources}
    cleanup_stale_outputs(active_stems)

    web_paths: list[str] = []

    for index, src in enumerate(sources, start=1):
        stem = src.stem
        dst = OUT / f"{stem}.jpg"
        rule = resolve_rule(rules, stem, index)

        print(f"[{index:03d}] {src.name}", end="")
        if rule is not None:
            print(f" -> {rule}", end="")
        print()

        image = load_image(src)
        image = apply_orientation(image, rule)
        save_web_image(image, dst)
        web_paths.append(f"images/web/{dst.name}")

    write_gallery_data(web_paths)
    print(f"\nDone! {len(web_paths)} images ready.")
    print("Refresh index.html in your browser.")


if __name__ == "__main__":
    main()
