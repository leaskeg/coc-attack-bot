import cv2
import os

OUTPUT_DIR = r"C:\Users\Leask\Desktop\Bots\coc-attack-bot\troop_templates"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Each entry: (image_path, prefix, cols, rows_config)
# rows_config = list of (row_y_start, row_y_end) for each row of icons
IMAGES = [
    (
        r"C:\Users\Leask\AppData\Local\Temp\zencoder\pasted\files\Skrmbillede2026-05-06213719-20260506193743-8sk308..png",
        "siege", 4,
        [(2, 110), (112, 220)],
    ),
    (
        r"C:\Users\Leask\AppData\Local\Temp\zencoder\pasted\files\Skrmbillede2026-05-06213643-20260506193743-g8fczh..png",
        "elixir", 7,
        [(2, 91), (92, 183), (225, 316)],
    ),
    (
        r"C:\Users\Leask\AppData\Local\Temp\zencoder\pasted\files\Skrmbillede2026-05-06213700-20260506193743-d35m45..png",
        "super1", 7,
        [(2, 91), (92, 183), (225, 316)],
    ),
    (
        r"C:\Users\Leask\AppData\Local\Temp\zencoder\pasted\files\Skrmbillede2026-05-06213713-20260506193743-9j7oyy..png",
        "super2", 7,
        [(2, 91), (92, 183), (225, 316)],
    ),
]

icon_count = 0

for img_path, prefix, cols, rows_config in IMAGES:
    img = cv2.imread(img_path)
    if img is None:
        print(f"[SKIP] {img_path}")
        continue

    h, w = img.shape[:2]
    cell_w = w / cols

    print(f"\n[{prefix}] {w}x{h}, {cols} cols, {len(rows_config)} rows")

    for row_idx, (y0, y1) in enumerate(rows_config):
        for col_idx in range(cols):
            x0 = int(col_idx * cell_w)
            x1 = int((col_idx + 1) * cell_w)

            crop = img[y0:y1, x0:x1]
            if crop.size == 0:
                continue

            name = f"{prefix}_{icon_count:03d}.png"
            cv2.imwrite(os.path.join(OUTPUT_DIR, name), crop)
            print(f"  {name}  row={row_idx} col={col_idx}  ({x0},{y0})-({x1},{y1})")
            icon_count += 1

print(f"\nDone. {icon_count} icons saved to {OUTPUT_DIR}")
