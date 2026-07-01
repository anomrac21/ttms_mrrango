#!/usr/bin/env python3
"""Download section images (Pexels + client promos) and update content/*/_index.md."""
from __future__ import annotations

import re
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = ROOT / "static" / "images"
CONTENT = ROOT / "content"
PROMOS = IMAGES_DIR / "promos"

PEX = "https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg?auto=compress&cs=tinysrgb&w=900"

CLIENT_JPG: dict[str, str] = {
    "hero.webp": "fiesta-fridays.jpg",
    "promotions.webp": "happy-hour.jpg",
}

PEXELS: dict[str, tuple[str, str]] = {
    "appetizers.webp": (PEX.format(id="2087742"), "Pexels #2087742"),
    "salads.webp": (PEX.format(id="1279330"), "Pexels #1279330"),
    "dips.webp": (PEX.format(id="1639557"), "Pexels #1639557"),
    "soups.webp": (PEX.format(id="539451"), "Pexels #539451"),
    "tacos.webp": (PEX.format(id="2092500"), "Pexels #2092500"),
    "burritos-quesadillas.webp": (PEX.format(id="209406"), "Pexels #209406"),
    "sides.webp": (PEX.format(id="410648"), "Pexels #410648"),
    "kids.webp": (PEX.format(id="699953"), "Pexels #699953"),
    "burgers.webp": (PEX.format(id="769289"), "Pexels #769289"),
    "sandwiches.webp": (PEX.format(id="1630757"), "Pexels #1630757"),
    "pasta.webp": (PEX.format(id="2097090"), "Pexels #2097090"),
    "entrees.webp": (PEX.format(id="691114"), "Pexels #691114"),
    "specialty.webp": (PEX.format(id="958545"), "Pexels #958545"),
    "desserts.webp": (PEX.format(id="2089718"), "Pexels #2089718"),
    "cocktails.webp": (PEX.format(id="274192"), "Pexels #274192"),
    "mocktails.webp": (PEX.format(id="1267325"), "Pexels #1267325"),
    "beer-and-non-alcoholic.webp": (PEX.format(id="1304540"), "Pexels #1304540"),
    "shots.webp": (PEX.format(id="1126728"), "Pexels #1126728"),
    "wines.webp": (PEX.format(id="1283219"), "Pexels #1283219"),
    "alcoholic.webp": (PEX.format(id="696218"), "Pexels #696218"),
    "slideshow-tacos.webp": (PEX.format(id="2087742"), "Pexels #2087742"),
    "slideshow-cocktails.webp": (PEX.format(id="274192"), "Pexels #274192"),
}

SECTIONS: dict[str, str] = {
    "promotions": "promotions.webp",
    "appetizers": "appetizers.webp",
    "salads": "salads.webp",
    "dips": "dips.webp",
    "soups": "soups.webp",
    "tacos": "tacos.webp",
    "burritos-quesadillas": "burritos-quesadillas.webp",
    "sides": "sides.webp",
    "kids": "kids.webp",
    "burgers": "burgers.webp",
    "sandwiches": "sandwiches.webp",
    "pasta": "pasta.webp",
    "entrees": "entrees.webp",
    "specialty": "specialty.webp",
    "desserts": "desserts.webp",
    "cocktails": "cocktails.webp",
    "mocktails": "mocktails.webp",
    "beer-and-non-alcoholic": "beer-and-non-alcoholic.webp",
    "shots": "shots.webp",
    "wines": "wines.webp",
    "alcoholic": "alcoholic.webp",
}


def img(name: str) -> str:
    return f"images/{name}"


def convert_jpg_to_webp(src: Path, dest: Path) -> bool:
    from PIL import Image

    if not src.exists():
        return dest.exists()
    Image.open(src).save(dest, "WEBP", quality=85)
    print(f"OK {dest.name} (from {src.name})")
    return True


def download_pexels(filename: str, url: str) -> bool:
    from PIL import Image

    webp = IMAGES_DIR / filename
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        print(f"SKIP {filename}: HTTP {e.code}")
        return webp.exists()
    Image.open(BytesIO(data)).save(webp, "WEBP", quality=85)
    print(f"OK {filename}")
    return True


def body_after_frontmatter(raw: str) -> str:
    if raw.count("---") < 2:
        return raw.strip()
    return raw.split("---", 2)[2].strip()


def update_section_index(section: str, image_file: str) -> None:
    path = CONTENT / section / "_index.md"
    if not path.exists():
        return
    raw = path.read_text(encoding="utf-8")
    title_m = re.search(r"^title:\s*(.+)$", raw, re.M)
    weight_m = re.search(r"^weight:\s*(.+)$", raw, re.M)
    title = title_m.group(1).strip().strip('"') if title_m else section.replace("-", " ").title()
    weight = weight_m.group(1).strip().strip('"') if weight_m else "1"
    body = body_after_frontmatter(raw)

    lines = [
        "---",
        f"title: {title}",
        f"weight: {weight}",
        f"icon: {img(image_file)}",
        "images:",
        f"    primary: {img(image_file)}",
        "---",
    ]
    if body:
        lines.extend(["", body])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def update_home_index() -> None:
    path = CONTENT / "_index.md"
    body = body_after_frontmatter(path.read_text(encoding="utf-8"))
    if not body.strip():
        body = (
            "<p>Mr. Rango Cookhouse Ltd. — full menu.</p>\n\n"
            "<p><strong>Prices are subject to 10% service charge and 12.5% VAT.</strong></p>"
        )
    text = (
        "---\n"
        'title: "Mr Rango Cookhouse"\n'
        f"image: {img('hero.webp')}\n"
        "images:\n"
        f"    - image: {img('hero.webp')}\n"
        f"    - image: {img('tacos.webp')}\n"
        f"    - image: {img('burgers.webp')}\n"
        f"    - image: {img('cocktails.webp')}\n"
        "slideshow:\n"
        f"    - image: {img('hero.webp')}\n"
        f"    - image: {img('slideshow-tacos.webp')}\n"
        f"    - image: {img('entrees.webp')}\n"
        f"    - image: {img('slideshow-cocktails.webp')}\n"
        f"    - image: {img('promotions.webp')}\n"
        f"    - image: {img('desserts.webp')}\n"
        "---"
    )
    text += f"\n\n{body}\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    credits: list[str] = []

    for dest, src_name in CLIENT_JPG.items():
        src = PROMOS / src_name
        if convert_jpg_to_webp(src, IMAGES_DIR / dest):
            credits.append(f"- {dest} — Mr Rango (client promo, from promos/{src_name})")

    for filename, (url, credit) in PEXELS.items():
        if download_pexels(filename, url):
            credits.append(f"- {filename} — {credit}")

    missing = [s for s, f in SECTIONS.items() if not (IMAGES_DIR / f).exists()]
    if missing:
        print("Missing:", ", ".join(missing))
        return

    for section, image_file in SECTIONS.items():
        update_section_index(section, image_file)

    if (IMAGES_DIR / "hero.webp").exists():
        update_home_index()

    (IMAGES_DIR / "IMAGE_CREDITS.txt").write_text(
        "Section photos:\n" + "\n".join(credits) + "\n",
        encoding="utf-8",
    )
    print("Section headers updated.")


if __name__ == "__main__":
    main()
