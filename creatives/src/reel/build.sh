#!/bin/bash
# Сборка ролика: карточки-слова -> слово на фото -> нарезка фото -> финальная карточка
set -e
cd "$(dirname "$0")"
FPS=30
seg(){ # $1 input png/jpg, $2 frames, $3 zoom speed, $4 out
  ffmpeg -v error -y -loop 1 -i "$1" -vf "scale=1188:2112,zoompan=z='1+$3*on':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=$FPS,format=yuv420p" -frames:v $2 -c:v libx264 -preset veryfast -crf 18 "$4"
}
rm -f seg/*.mp4 list.txt
n=0; add(){ printf "file 'seg/%03d.mp4'\n" $n >> list.txt; seg "$1" "$2" "$3" "$(printf 'seg/%03d.mp4' $n)"; n=$((n+1)); }
for i in 0 1 2 3 4 5 6; do add cards/w$i.png 17 0; done        # слова по ~0.57 с
add cards/w_photo.png 30 0.003                                   # «приходи» на фото, 1 с
for f in shots/*.jpg; do add "$f" 14 0.004; done                # нарезка ~0.47 с
add cards/end.png 105 0.0006                                     # финал 3.5 с
ffmpeg -v error -y -f concat -safe 0 -i list.txt -c copy ../../video/sila-tbilisi-reel-9x16.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 ../../video/sila-tbilisi-reel-9x16.mp4
