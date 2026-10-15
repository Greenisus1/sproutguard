#!/usr/bin/env python3
"""Original offline five-lane garden defense. Python standard library only."""
import curses,os,json,random,time,sys
from pathlib import Path
from ui import put,run
import sprites
VERSION='1.0.0'
RECORD=Path.home()/'.local/share/sproutguard/best.json'
COSTS=(50,100,75,150)
NAMES=('Glowflower','Seedspitter','Barkwall','Burstbulb')
class Garden:
 ROWS=5;COLS=9
 def __init__(self,seed=None):
  self.rng=random.Random(seed);self.energy=200;self.wave=0;self.maxwaves=10;self.score=0;self.lives=5;self.plants={};self.enemies=[];self.shots=[];self.fx=[];self.mowers=[True]*5;self.over=False;self.won=False;self.timer=0;self.sky=0;self.gap=3;self.pending=0;self.spawnclock=0;self.message='Plant growers and shooters. First wave in 3 seconds.';self.cool=[0.,0.,0.,0.]
 def place(self,row,col,kind):
  if self.over:return False
  q=(row,col)
  if not (0<=row<5 and 0<=col<9 and kind in range(4)):return False
  if q in self.plants:self.message='That bed is occupied.';return False
  if self.energy<COSTS[kind]:self.message='Need '+str(COSTS[kind])+' glow.';return False
  if self.cool[kind]>0:self.message='Seed packet recharging.';return False
  self.energy-=COSTS[kind];self.cool[kind]=(2,1,5,10)[kind]
  self.plants[q]=dict(kind=kind,hp=(100,100,500,100)[kind],clock=0.)
  self.message=NAMES[kind]+' planted.';return True
 def shovel(self,row,col):
  if self.over:return False
  if (row,col) in self.plants:del self.plants[row,col];self.message='Bed cleared (no refund).';return True
  return False
 def startwave(self):
  if self.over or self.pending or self.enemies:return False
  self.wave+=1;self.pending=4+self.wave*2;self.spawnclock=.1;self.gap=0;self.message='Wave '+str(self.wave)+' incoming!';return True
 def tick(self,dt):
  if self.over:return
  dt=min(.1,max(0,dt));self.timer+=dt;self.sky+=dt;self.cool=[max(0,x-dt) for x in self.cool];self.fx=[(r,x,t-dt) for r,x,t in self.fx if t>dt]
  if self.sky>=5:self.sky-=5;self.energy+=25
  if self.gap>0:
   self.gap=max(0,self.gap-dt)
   if self.gap==0:self.startwave()
  if self.pending:
   self.spawnclock-=dt
   if self.spawnclock<=0:
    lane=self.rng.randrange(5);armor=self.wave>=3 and self.rng.random()<.25;fast=self.wave>=5 and self.rng.random()<.2
    self.enemies.append(dict(row=lane,x=9.2,hp=260 if armor else 100,speed=.24 if fast else .13+.008*self.wave,armor=armor,fast=fast,bite=0));self.pending-=1;self.spawnclock=max(.55,2-self.wave*.1)
  for q,p in list(self.plants.items()):
   p['clock']+=dt;row,col=q
   if p['kind']==0 and p['clock']>=8:p['clock']-=8;self.energy+=25
   if p['kind']==1 and p['clock']>=1.4 and any(e['row']==row and e['x']>=col for e in self.enemies):p['clock']=0;self.shots.append(dict(row=row,x=col+.5,damage=25))
   if p['kind']==3 and p['clock']>=1:
    for e in self.enemies:
     if abs(e['row']-row)<=1 and abs(e['x']-col)<=1.5:e['hp']-=1000
    self.fx.append((row,col,.55));self.plants.pop(q,None);self.message='Burstbulb exploded!'
  for shot in list(self.shots):
   old=shot['x'];shot['x']+=4*dt
   hits=[e for e in self.enemies if e['row']==shot['row'] and old-.1<=e['x']<=shot['x']+.18 and e['hp']>0]
   if hits:
    target=min(hits,key=lambda e:e['x']);target['hp']-=shot['damage'];self.shots.remove(shot)
   elif shot['x']>10:self.shots.remove(shot)
  for e in list(self.enemies):
   if e not in self.enemies:continue
   if e['hp']<=0:self.enemies.remove(e);self.score+=10;continue
   target=next(((q,p) for q,p in self.plants.items() if q[0]==e['row'] and abs(e['x']-q[1])<.45),None)
   if target:
    q,p=target;p['hp']-=30*dt
    if p['hp']<=0:self.plants.pop(q,None)
   else:e['x']-=e['speed']*dt
   if e['x']<-.3:
    lane=e['row']
    if self.mowers[lane]:
     self.mowers[lane]=False;victims=[z for z in self.enemies if z['row']==lane]
     for z in victims:self.enemies.remove(z);self.score+=10
     self.message='Emergency mower cleared lane '+str(lane+1)+'!'
    else:
     self.enemies.remove(e);self.lives-=1;self.message='A shambler reached the house!'
     if self.lives<=0:self.over=True;self.message='The garden fell. R restarts.';return
  if self.wave>0 and not self.enemies and not self.pending and self.gap==0:
   self.score+=100
   if self.wave>=self.maxwaves:self.over=True;self.won=True;self.message='Garden saved! All 10 waves cleared.'
   else:self.gap=8;self.energy+=50;self.message='Wave cleared! +50 glow. Next in 8 seconds.'
def best():
 try:
  if RECORD.is_symlink():return 0
  return max(0,int(json.loads(RECORD.read_text()).get('best',0)))
 except (OSError,ValueError,TypeError,AttributeError):return 0
def save(score):
 try:
  if any(p.is_symlink() for p in [RECORD,*RECORD.parents]):return False
  RECORD.parent.mkdir(parents=True,exist_ok=True,mode=0o700);tmp=RECORD.with_suffix('.tmp');fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_TRUNC|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'w') as f:json.dump({'best':max(score,best())},f)
  tmp.replace(RECORD);return True
 except OSError:return False
def palette():
 if not curses.has_colors():return False
 curses.start_color();curses.use_default_colors()
 values=[(118,22),(153,17),(220,17),(255,17),(208,17),(231,52),(83,17)] if curses.COLORS>=256 else [(2,-1),(6,-1),(3,-1),(7,-1),(1,-1),(7,-1),(2,-1)]
 for i,(fg,bg) in enumerate(values,1):curses.init_pair(i,fg,bg)
 return True
def play(s):
 g=Garden();last=time.monotonic();row=2;col=2;kind=0;paused=False;recorded=False;high=best();pixels=sprites.supported() and '--ascii' not in sys.argv;colors=palette()
 def color(i):return curses.color_pair(i) if colors else 0
 while True:
  s.timeout(90 if pixels else 30);key=s.getch();now=time.monotonic();dt=now-last;last=now;h,w=s.getmaxyx();s.erase()
  if key in (27,ord('q'),ord('Q')):return
  if key in (ord('p'),ord('P')):paused=not paused
  if key in (ord('v'),ord('V')):pixels=not pixels;s.clear()
  if key in (ord('r'),ord('R')):g=Garden();paused=False;recorded=False
  if h<27 or w<80:put(s,1,1,'Resize to 80x27. Simulation paused. Q quits.');s.refresh();continue
  if not paused and not g.over:
   if key in (curses.KEY_UP,ord('w'),ord('W')):row=max(0,row-1)
   if key in (curses.KEY_DOWN,ord('s'),ord('S')):row=min(4,row+1)
   if key in (curses.KEY_LEFT,ord('a'),ord('A')):col=max(0,col-1)
   if key in (curses.KEY_RIGHT,ord('d'),ord('D')):col=min(8,col+1)
   if key in (ord('1'),ord('2'),ord('3'),ord('4')):kind=key-ord('1')
   if key in (ord(' '),10,13):g.place(row,col,kind)
   if key in (ord('x'),ord('X')):g.shovel(row,col)
   if key in (ord('n'),ord('N')):g.gap=0;g.startwave()
   g.tick(dt)
  if g.over and not recorded:g.message+=' Best saved.' if save(g.score) else ' Save unavailable.';recorded=True;high=max(high,best())
  put(s,0,2,'SPROUTGUARD | WAVE '+str(g.wave)+'/10 | GLOW '+str(g.energy)+' | HOUSE '+str(g.lives)+' | SCORE '+str(g.score),color(3)|curses.A_BOLD)
  put(s,1,2,('PAUSED | ' if paused else '')+g.message,color(2))
  packets=' | '.join(('>' if i==kind else '')+str(i+1)+' '+name+' '+str(COSTS[i]) for i,name in enumerate(('Grow','Spit','Wall','Bomb')))
  put(s,2,2,packets,color(4))
  cw=max(7,(w-8)//9);rh=max(3,(h-9)//5);ox=(w-cw*9)//2;oy=4
  if not pixels:
   for rr in range(5):
    for cc in range(9):
     for yy in range(rh):put(s,oy+rr*rh+yy,ox+cc*cw,('['+' '*(cw-2)+']') if (rr,cc)==(row,col) and yy==rh//2 else '.'*cw,color(1))
   for (rr,cc),plant in g.plants.items():put(s,oy+rr*rh+rh//2,ox+cc*cw+2,('SUN','PEW','WALL','BOOM')[plant['kind']],color(3 if plant['kind']==0 else 7))
   for e in g.enemies:put(s,oy+e['row']*rh+rh//2,ox+max(0,min(9*cw-3,round(e['x']*cw))), 'Z#' if e['armor'] else 'Z>' if e['fast'] else 'Z!',color(5))
   for sh in g.shots:put(s,oy+sh['row']*rh+rh//2,ox+max(0,min(9*cw-1,round(sh['x']*cw))), '*',color(7))
  for rr in range(5):put(s,oy+rr*rh+rh//2,0,'M' if g.mowers[rr] else '-',color(3))
  put(s,h-4,2,'SELECT '+str(row+1)+','+str(col+1)+' | '+NAMES[kind]+' ['+str(round(g.cool[kind],1))+'s] | Pending '+str(g.pending)+' | BEST '+str(high),color(3))
  put(s,h-3,2,'Arrows/WASD bed | 1-4 seed | Space/Enter plant | X shovel (no refund)',color(4))
  put(s,h-2,2,'N start wave early | P pause | V pixel/text | R restart | Q quit',color(2))
  put(s,h-1,2,'Glow +25 each 5s; growers +25 each 8s. M = one emergency mower per lane.',color(7));s.refresh()
  if pixels:sys.stdout.write(sprites.frame(g,w,h,row,col));sys.stdout.flush()
if __name__=='__main__':
 if '--version' in sys.argv:print(VERSION)
 else:raise SystemExit(run(play))
