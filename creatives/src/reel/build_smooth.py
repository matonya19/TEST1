"""Плавная версия ролика: стабилизированные видео (vidstab), более длинные кадры, мягкие переходы xfade."""
import subprocess, pathlib
HERE = pathlib.Path(__file__).parent
SEG = HERE / "seg"; SEG.mkdir(exist_ok=True)
OUT = HERE.parent.parent / "video" / "sila-tbilisi-reel-9x16.mp4"
ENC = ["-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p"]
def ff(*a): subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *a], check=True)

# 1) слова — резкие смены, как в образце
cards = []
for i in range(7):
    p = SEG / f"c{i}.mp4"; ff("-loop", "1", "-i", f"cards/w{i}.png", "-t", "0.567", *ENC, str(p)); cards.append(p)

# 2) «приходи» поверх зала + нарезка + финал — всё через плавные переходы
X = 0.35   # длительность перехода
parts = []
p = SEG / "over.mp4"
ff("-ss", "0.2", "-i", "proxy2/IMG_3091.mp4", "-i", "cards/w_over.png", "-t", "1.5",
   "-filter_complex", "[0][1]overlay=0:0", *ENC, str(p)); parts.append((p, 1.5))
CUTS = [("IMG_2967", 0.4), ("IMG_2975", 1.2), ("IMG_2983", 0.4), ("IMG_2985", 0.6),
        ("IMG_6566", 0.6), ("IMG_2995", 1.6), ("IMG_2975", 4.4), ("IMG_3091", 1.4)]
for k, (f, t) in enumerate(CUTS):
    p = SEG / f"v{k}.mp4"; ff("-ss", str(t), "-i", f"proxy2/{f}.mp4", "-t", "1.3", *ENC, str(p)); parts.append((p, 1.3))
p = SEG / "pool.mp4"; ff("-ss", "1.0", "-i", "proxy2/IMG_3064.mp4", "-t", "3.0", *ENC, str(p)); parts.append((p, 3.0))
p = SEG / "end.mp4"; ff("-loop", "1", "-i", "cards/end.png", "-t", "3.4", *ENC, str(p)); parts.append((p, 3.4))

inp, flt, prev, off = [], [], "0:v", 0.0
for i, (p, d) in enumerate(parts):
    inp += ["-i", str(p)]
for i in range(1, len(parts)):
    off += parts[i - 1][1] - X
    lab = f"x{i}"
    flt.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={X}:offset={off:.3f}[{lab}]")
    prev = lab
tail = SEG / "tail.mp4"
ff(*inp, "-filter_complex", ";".join(flt), "-map", f"[{prev}]", *ENC, str(tail))

lst = SEG / "list.txt"
lst.write_text("".join(f"file '{p.name}'\n" for p in cards + [tail]))
ff("-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(OUT))
print(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(OUT)], capture_output=True, text=True).stdout)
