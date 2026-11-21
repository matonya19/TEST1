#!/bin/bash
# Ролик из видео: слова на карточках -> «приходи» поверх видео -> нарезка -> статичный финал
set -e
cd "$(dirname "$0")"
mkdir -p seg; rm -f seg/*.mp4 list.txt
n=0
next(){ out=$(printf 'seg/%03d.mp4' $n); printf "file '%s'\n" "$out" >> list.txt; n=$((n+1)); }
still(){ next; ffmpeg -nostdin -v error -y -loop 1 -i "$1" -t "$2" -r 30 -vf "scale=1080:1920,format=yuv420p" -c:v libx264 -preset veryfast -crf 18 "$out"; }
clip(){ next; ffmpeg -nostdin -v error -y -ss "$2" -i "proxy/$1.mp4" -t "$3" -r 30 -vf "format=yuv420p" -c:v libx264 -preset veryfast -crf 18 "$out"; }
for i in 0 1 2 3 4 5 6; do still cards/w$i.png 0.567; done
# «приходи» поверх зала
next; ffmpeg -nostdin -v error -y -ss 0.4 -i proxy/IMG_2967.mp4 -i cards/w_over.png -t 1.2 -r 30 -filter_complex "[0][1]overlay=0:0,format=yuv420p" -c:v libx264 -preset veryfast -crf 18 "$out"
# нарезка
while read f t; do clip $f $t 0.6; done <<CUTS
IMG_3091 0.3
IMG_2875 1.0
IMG_2975 1.0
IMG_2983 0.5
IMG_2985 0.6
IMG_6566 0.5
IMG_2995 1.5
IMG_3091 1.5
IMG_2975 4.6
IMG_2985 4.0
IMG_2995 4.6
IMG_6566 3.6
IMG_2875 3.6
CUTS
still cards/end.png 3.2     # финал без движения
ffmpeg -nostdin -v error -y -f concat -safe 0 -i list.txt -c copy ../../video/sila-tbilisi-reel-9x16.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 ../../video/sila-tbilisi-reel-9x16.mp4
