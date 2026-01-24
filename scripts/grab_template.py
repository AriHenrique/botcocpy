import cv2
import os
import json
from compat.android import AndroidDevice
from compat.config import TEMPLATE_DIR, SCREENSHOT_FILE

drawing = False
ix, iy = -1, -1
rect = None
rects = []


JSON_PATH = os.path.join(TEMPLATE_DIR, "templates.json")


def mouse_callback(event, x, y, flags, param):
    global ix, iy, drawing, rect

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        rect = (ix, iy, x, y)


def safe_filename(name):
    return "".join(c for c in name if c.isalnum() or c in ("_", "-", "."))


def ensure_png(name):
    if not name.lower().endswith(".png"):
        return name + ".png"
    return name


def unique_path(directory, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    path = os.path.join(directory, filename)

    while os.path.exists(path):
        path = os.path.join(directory, f"{base}_{counter}{ext}")
        counter += 1

    return path


def load_metadata():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_metadata(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    global rect, rects

    os.makedirs(TEMPLATE_DIR, exist_ok=True)
    d = AndroidDevice()

    print("[GRAB] Taking screenshot from emulator...")
    screen = d.screenshot()

    img = cv2.imread(screen)
    clone = img.copy()

    if img is None:
        raise RuntimeError("Failed to load screenshot")

    h, w, _ = img.shape

    metadata = load_metadata()

    cv2.namedWindow("Template Grabber")
    cv2.setMouseCallback("Template Grabber", mouse_callback)

    print("""
[GRAB] CONTROLS:
- Drag mouse = selecionar área
- S = salvar template
- Q = sair
""")

    counter = 1

    while True:
        temp = clone.copy()

        for (x1, y1, x2, y2) in rects:
            cv2.rectangle(temp, (x1, y1), (x2, y2), (0, 200, 0), 1)

        if rect is not None:
            x1, y1, x2, y2 = rect
            cv2.rectangle(temp, (x1, y1), (x2, y2), (0, 255, 0), 2)

        cv2.imshow("Template Grabber", temp)
        key = cv2.waitKey(1) & 0xFF

        # ===== SALVAR =====
        if key == ord("s") and rect is not None:
            default_name = f"template_{counter}"
            raw_name = input(f"Template name [{default_name}]: ").strip()
            if not raw_name:
                raw_name = default_name

            name = ensure_png(safe_filename(raw_name))

            x1, y1, x2, y2 = rect
            crop = clone[min(y1, y2):max(y1, y2),
                   min(x1, x2):max(x1, x2)]

            path = unique_path(TEMPLATE_DIR, name)

            success = cv2.imwrite(path, crop)
            if not success:
                print("[GRAB] ERROR: Failed to save image")
            else:
                print(f"[GRAB] Saved template: {path}")

                # ===== METADATA =====
                use_region_raw = input("Use region for matching? [Y/n]: ").strip().lower()
                use_region = False if use_region_raw == "n" else True

                metadata[os.path.basename(path)] = {
                    "region": [x1, y1, x2, y2],
                    "screen_size": [w, h],
                    "use_region": use_region
                }

                save_metadata(metadata)

                rects.append(rect)
                rect = None
                counter += 1

        elif key == ord("q"):
            break

    cv2.destroyAllWindows()
    print(f"[GRAB] Session finished. {len(rects)} templates saved.")
    print(f"[GRAB] Metadata saved in: {JSON_PATH}")


if __name__ == "__main__":
    main()
