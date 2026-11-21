"""Динамичная версия: слова -> «приходи» -> быстрая нарезка (видео + фото, ~0.45 с, резкие склейки) -> бассейн -> мягкий переход в финал."""
import subprocess, pathlib
HERE = pathlib.Path(__file__).parent
SEG = HERE / "seg"; SEG.mkdir(exist_ok=True)
OUT = HERE.parent.parent / "video" / "sila-tbilisi-reel-9x16.mp4"
ENC = ["-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p"]
def ff(*a): subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *a], check=True)
seq = []
def still(img, d, txt=None):
    p = SEG / f"{len(seq):03d}.mp4"
    if txt: ff("-loop", "1", "-i", img, "-i", f"cards/{txt}.png", "-t", str(d), "-filter_complex", "[0]scale=1080:1920[b];[b][1]overlay=0:0", *ENC, str(p))
    else: ff("-loop", "1", "-i", img, "-t", str(d), "-vf", "scale=1080:1920", *ENC, str(p))
    seq.append(p)
def clip(src, t, d, txt=None):
    p = SEG / f"{len(seq):03d}.mp4"
    if txt: ff("-ss", str(t), "-i", f"proxy2/{src}.mp4", "-i", f"cards/{txt}.png", "-t", str(d), "-filter_complex", "[0][1]overlay=0:0", *ENC, str(p))
    else: ff("-ss", str(t), "-i", f"proxy2/{src}.mp4", "-t", str(d), *ENC, str(p))
    seq.append(p)

for i in range(7): still(f"cards/w{i}.png", 0.567)
p = SEG / f"{len(seq):03d}.mp4"
ff("-ss", "0.2", "-i", "proxy2/IMG_3091.mp4", "-i", "cards/w_over.png", "-t", "1.2", "-filter_complex", "[0][1]overlay=0:0", *ENC, str(p)); seq.append(p)

D = 0.45   # длина кадра в нарезке
CUTS = [("IMG_9067", 0.3), ("IMG_2967", 0.4), ("shots/s00.jpg", 0), ("IMG_8032", 0.2), ("IMG_2975", 1.2),
        ("IMG_3091", 1.0), ("IMG_2983", 0.4), ("shots/s03.jpg", 0), ("IMG_9067", 1.6), ("IMG_2967", 2.0),
        ("IMG_6566", 0.6), ("shots/s08.jpg", 0), ("IMG_2985", 4.4), ("IMG_8032", 0.8), ("IMG_2975", 4.4),
        ("IMG_9067", 2.6), ("IMG_3091", 1.8)]
TXT = ["t1"] * 3 + ["t2"] * 3 + ["t3"] * 3 + ["t4"] * 3 + ["t5"] * 3 + ["t6"] * 2   # фраза держится ~3 кадра
for (src, t), txt in zip(CUTS, TXT):
    still(src, D, txt) if src.endswith(".jpg") else clip(src, t, D, txt)

# бассейн -> финал с мягким переходом
pool = SEG / "pool.mp4"; ff("-ss", "1.0", "-i", "proxy2/IMG_3064.mp4", "-i", "cards/t7.png", "-t", "2.6", "-filter_complex", "[0][1]overlay=0:0", *ENC, str(pool))
end = SEG / "end.mp4"; ff("-loop", "1", "-i", "cards/end.png", "-t", "3.4", *ENC, str(end))
tail = SEG / "tail.mp4"
ff("-i", str(pool), "-i", str(end), "-filter_complex", "[0][1]xfade=transition=fade:duration=0.35:offset=2.25", *ENC, str(tail))
seq.append(tail)

(SEG / "list.txt").write_text("".join(f"file '{p.name}'\n" for p in seq))
ff("-f", "concat", "-safe", "0", "-i", str(SEG / "list.txt"), "-c", "copy", str(OUT))
print(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(OUT)], capture_output=True, text=True).stdout)
