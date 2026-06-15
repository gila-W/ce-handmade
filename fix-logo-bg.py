from pathlib import Path

from PIL import Image

LOGO = Path(__file__).parent / "logo.png"
SOURCES = [
    Path(__file__).parent / "logo-new-temp.png",
    Path(r"C:\Users\משתמש\.cursor\projects\c-Users-Downloads\assets\logo-new.png"),
]


def is_background_pixel(r: int, g: int, b: int, a: int) -> bool:
    if a < 20:
        return True
    brightness = (r + g + b) / 3
    if brightness > 248:
        return True
    if abs(r - g) < 12 and abs(g - b) < 12 and brightness > 185:
        return True
    return False


def make_transparent(source: Path, destination: Path) -> None:
    image = Image.open(source).convert("RGBA")
    pixels = image.load()
    width, height = image.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if is_background_pixel(r, g, b, a):
                pixels[x, y] = (r, g, b, 0)

    image.save(destination, "PNG")
    print(f"Saved transparent logo to {destination}")


if __name__ == "__main__":
    for source in SOURCES:
        if source.exists():
            make_transparent(source, LOGO)
            break
    else:
        make_transparent(LOGO, LOGO)
