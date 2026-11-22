import subprocess,os
os.chdir('/tmp/claude-0/-home-user-TEST1/513f869e-9292-59bf-9428-803d9243f8db/scratchpad/lev-clips')
def sh(cmd):
    r=subprocess.run(cmd,shell=True,capture_output=True,text=True)
    if r.returncode: raise SystemExit(cmd[:200]+'\n'+r.stderr[-600:])
X='-an -c:v libx264 -preset fast -crf 12 -pix_fmt yuv420p'
def tile(src,ss,play,total,W,H,cx,out,flip=False,still=False):
    sw=round(1280/720*H); x=int(min(max(cx*sw-W/2,0),sw-W)); pad=total-play
    vf=f"fps=30,scale=-2:{H},crop={W}:{H}:{x}:0"+(",hflip" if flip else "")+(f",tpad=stop_mode=clone:stop={pad}" if pad>0 else "")
    sh(f"ffmpeg -nostdin -v error -y -ss {ss} -i {src} -vf \"{vf}\" -frames:v {total} {X} {out}")
def concat(files,out):
    open('b/_l.txt','w').write(''.join(f"file '{f}'\n" for f in files))
    sh(f"ffmpeg -nostdin -v error -y -f concat -safe 0 -i b/_l.txt -c copy {out}")
# ---- top (Lev) ----
def lev(src,ss,n,out,flip=False,hold=False):
    vf="fps=30,scale=1080:1920,crop=1080:1000:0:180"+(",hflip" if flip else "")+(",tpad=stop_mode=clone:stop=%d"%(n-1) if hold else "")
    sh(f"ffmpeg -nostdin -v error -y -ss {ss} -i {src} -vf \"{vf}\" -frames:v {n} {X} {out}")
T=[('L1.mp4',1.0,45,0,1),('L1.mp4',1.0,90,0,0),('L5.mp4',0,72,0,0),('L2.mp4',0,120,0,0),('L5.mp4',2.4,45,0,0),('L3.mp4',0,240,0,0),('L4.mp4',0,114,0,0),('L5.mp4',1.4,75,0,0)]
fs=[]
for i,(s,ss,n,fl,h) in enumerate(T): lev(s,ss,n,f'b/t{i}.mp4',bool(fl),bool(h)); fs.append(f't{i}.mp4')
concat(fs,'b/top.mp4')
import sys
SKIP=os.path.exists('b/bottom.mp4')
# ---- bottom states ----
def state(tiles,labelpng,n,out,mask,fade=False):
    # tiles: list of (mp4,x,y)
    inp=''.join(f"-i b/{t[0]} " for t in tiles)
    k=len(tiles)
    fc=f"color=c=0x0e1a33:s=1080x1920:r=30:d={n/30+1}[bg];"
    cur='bg'
    for i,(f,x,y) in enumerate(tiles):
        fc+=f"[{i}:v]format=yuva420p[a{i}];[{k}:v]format=gray[m{i}];[a{i}][m{i}]alphamerge"+(f",fade=t=in:st=0:d=0.3:alpha=1" if fade else "")+f"[p{i}];[{cur}][p{i}]overlay={x}:{y}:shortest=1[o{i}];"
        cur=f'o{i}'
    fc+=f"[{cur}][{k+1}:v]overlay=0:0:shortest=1,format=yuv420p[v]"
    sh(f"ffmpeg -nostdin -v error -y {inp} -loop 1 -i b/{mask} -loop 1 -i b/{labelpng} -filter_complex \"{fc}\" -map \"[v]\" -frames:v {n} -an -c:v libx264 -preset fast -crf 14 b/{out}")
if not SKIP:
    # big A: Sasha S1a(90)+hold(21) , S1b(150), hold(54), S2(51)
    tile('S1.mp4',0,90,111,1032,850,.65,'b/ba1.mp4')
    tile('S1.mp4',3.0,150,204,1032,850,.65,'b/ba2.mp4')
    tile('S2.mp4',0.9,51,51,1032,850,.65,'b/ba3.mp4')
    concat(['ba1.mp4','ba2.mp4','ba3.mp4'],'b/bigA_tile.mp4')
    state([('bigA_tile.mp4',24,1046)],'big_sasha.png',366,'sA.mp4','mask_big.png')
    # grid
    tile('S2.mp4',2.6,36,141,510,418,.65,'b/g1.mp4')
    sh("ffmpeg -nostdin -v error -y -loop 1 -i ../lev-kids/girl.png -vf \"crop=1184:666:0:110,scale=-2:418,crop=510:418:100:0,fps=30\" -frames:v 141 -an -c:v libx264 -crf 12 -pix_fmt yuv420p b/g2.mp4")
    tile('T1.mp4',0,120,141,510,418,.55,'b/g3.mp4')
    tile('V1.mp4',0,120,141,510,418,.6,'b/g4.mp4')
    state([('g1.mp4',24,1046),('g2.mp4',546,1046),('g3.mp4',24,1478),('g4.mp4',546,1478)],'grid.png',141,'sG.mp4','mask_grid.png',fade=True)
    # S3, G1, S4
    tile('S3.mp4',0,81,81,1032,850,.65,'b/bs3.mp4'); state([('bs3.mp4',24,1046)],'big_sasha.png',81,'sB.mp4','mask_big.png')
    tile('G1.mp4',0,90,90,1032,850,.48,'b/bg1.mp4'); state([('bg1.mp4',24,1046)],'big_girl.png',90,'sC.mp4','mask_big.png')
    tile('S4.mp4',0,96,123,1032,850,.65,'b/bs4.mp4'); state([('bs4.mp4',24,1046)],'big_sasha.png',123,'sD.mp4','mask_big.png')
    concat(['sA.mp4','sG.mp4','sB.mp4','sC.mp4','sD.mp4'],'b/bottom.mp4')

print('segments ok')
# ---- final composite ----
import math
caps=[('c1',0.0,3.0),('c2',3.0,3.65),('c3',3.8,7.7),('c4',8.4,10.6),('c5',11.0,12.2),('c6',13.3,15.0),('c7',15.0,19.55),('c8',19.9,21.6),('c9',23.7,25.3)]
inp="-i b/bottom.mp4 -i b/top.mp4 -loop 1 -i b/pill.png -loop 1 -i b/cursor.png "+''.join(f"-loop 1 -i b/{c[0]}.png " for c in caps)
cx=lambda t:560+260*math.sin(5*t); cy=lambda t:790+70*math.cos(3.5*t)
fc="[0:v][1:v]overlay=0:0:shortest=1[a];[a][2:v]overlay=0:0:shortest=1[b];"
cur='b'
for i,(n,s,e) in enumerate(caps):
    fc+=f"[{cur}][{4+i}:v]overlay=0:0:enable='between(t,{s},{e})':shortest=1[c{i}];"; cur=f'c{i}'
fc+=f"[{cur}][3:v]overlay=x='if(lt(t,24.0),{{}}+0,0)':y=0:enable='0':shortest=1[x]"
# cursor with expressions
xe="if(lt(t,24.0),560+260*sin(5*t),%.1f)"%cx(24.0); ye="if(lt(t,24.0),790+70*cos(3.5*t),%.1f)"%cy(24.0)
fc=fc[:fc.rindex(';')]+f";[{cur}][3:v]overlay=x='{xe}':y='{ye}':enable='between(t,19.9,26.7)':shortest=1,format=yuv420p[v]"
sh(f"ffmpeg -nostdin -v error -y {inp} -filter_complex \"{fc}\" -map \"[v]\" -frames:v 801 -an -c:v libx264 -preset fast -crf 16 b/video.mp4")
print('video ok')
