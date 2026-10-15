"""Original 8x8 garden sprites rendered with ANSI RGB half blocks."""
import os
PALETTE={'.':None,'K':(15,26,35),'W':(236,246,220),'Y':(255,211,56),'O':(230,127,44),'G':(83,189,77),'D':(28,99,59),'B':(87,138,168),'P':(192,118,161),'R':(225,68,71),'T':(148,103,67),'S':(165,190,143)}
ART={
 'grower':('..Y.Y...','.YYYYY..','YYYOOYY.','.YOKOY..','YYYOOYY.','.YYYYY..','...DD...','..GDGG..'),
 'shooter':('..GGGG..','.GWWGGG.','GGKGGKKG','.GGGGKKG','..GGGGG.','...DD...','.GGDGG..','..DDD...'),
 'wall':('..TTTT..','.TTWTTT.','TTWTTTTT','TTKTKTTT','TTTTTTTT','TTTKKTTT','.TTTTTT.','..TTTT..'),
 'bomb':('...GY...','..GG....','.RR..RR.','RRRRRRRR','RWKRRKWR','RRRRRRRR','.RRRRRR.','..RRRR..'),
 'enemy':('..SSSS..','.SWWSSS.','.SKKSKS.','..SSSS..','.PBBBP..','SSBBBBSS','..BKKB..','.KK..KK.'),
 'armor':('..OOOO..','.OOOOOO.','.SKKSKS.','..SSSS..','.PBBBP..','SSBBBBSS','..BKKB..','.KK..KK.'),
 'fast':('..RRRR..','.SSSSSS.','.SKKSKS.','..SSSS..','.PBBBP..','SSBBBBSS','..BKKB..','KK....KK'),
 'burst':('Y..RR..Y','.YRRRRY.','..RWWR..','RRWWWWRR','RRWWWWRR','..RWWR..','.YRRRRY.','Y..RR..Y')}
def supported():return os.environ.get('COLORTERM','').lower() in ('truecolor','24bit') or 'direct' in os.environ.get('TERM','').lower()
def frame(g,w,h,row,col):
 cw=max(7,(w-8)//9);rh=max(3,(h-9)//5);width=cw*9;height=rh*5*2;ox=(w-width)//2;oy=4
 canvas=[[(32,89,47) if (x//cw+y//(2*rh))%2 else (39,108,54) for x in range(width)] for y in range(height)]
 # Seed-bed boundaries and a clear selected-bed outline.
 for r in range(5):
  for c in range(9):
   border=(255,219,83) if (r,c)==(row,col) else (42,120,60)
   for x in range(c*cw,(c+1)*cw):canvas[r*rh*2][x]=border;canvas[(r+1)*rh*2-1][x]=border
   for y in range(r*rh*2,(r+1)*rh*2):canvas[y][c*cw]=border;canvas[y][(c+1)*cw-1]=border
 def stamp(lane,x,name):
  art=ART[name];sw=min(8,cw-1);sh=min(8,rh*2-1);left=round(x*cw)+(cw-sw)//2;top=lane*rh*2+(rh*2-sh)//2
  for yy in range(sh):
   for xx in range(sw):
    color=PALETTE[art[min(7,yy*8//sh)][min(7,xx*8//sw)]]
    if color is not None and 0<=left+xx<width and 0<=top+yy<height:canvas[top+yy][left+xx]=color
 for (r,c),p in g.plants.items():stamp(r,c,('grower','shooter','wall','bomb')[p['kind']])
 for e in g.enemies:stamp(e['row'],e['x'],'armor' if e['armor'] else 'fast' if e['fast'] else 'enemy')
 for s in g.shots:
  x=round(s['x']*cw);y=s['row']*rh*2+rh
  if 0<=x<width:canvas[y][x]=(194,252,91)
 for r,x,t in g.fx:
  for rr in range(max(0,r-1),min(5,r+2)):stamp(rr,x,'burst')
 out=[]
 for y in range(0,height,2):
  out.append(f'\x1b[{oy+y//2+1};{ox+1}H');fg=bg=None
  for x in range(width):
   a,b=canvas[y][x],canvas[y+1][x]
   if a!=fg:out.append('\x1b[38;2;'+ ';'.join(map(str,a))+'m');fg=a
   if b!=bg:out.append('\x1b[48;2;'+ ';'.join(map(str,b))+'m');bg=b
   out.append('▀')
 out.append('\x1b[0m');return ''.join(out)
