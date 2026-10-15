#!/usr/bin/env python3
"""Original offline garden lane defense. Python standard library only."""
import curses,os,json,random,time,sys
from pathlib import Path
from ui import put,run
import sprites
VERSION='1.1.0'
RECORD=Path.home()/'.local/share/sproutguard/best.json'
COSTS=(50,100,75,150)
NAMES=('Glowflower','Seedspitter','Barkwall','Burstbulb')
UPGRADES=(
 dict(key='soil',name='Rich Soil',cost=100,max=3,desc='Growers make +10 glow each cycle per level.'),
 dict(key='seeds',name='Sharp Seeds',cost=120,max=3,desc='Spitters deal +10 damage per level.'),
 dict(key='walls',name='Steel Roots',cost=100,max=2,desc='New Barkwalls gain +300 health per level.'),
 dict(key='packets',name='Quick Packets',cost=150,max=2,desc='Seed packets recharge 25% faster per level.'),
 dict(key='mowers',name='Spare Mowers',cost=150,max=99,desc='Restore every used emergency mower.'),
 dict(key='heart',name='Extra Heart',cost=200,max=3,desc='+1 house health.'))
def gridsize(h,w):
 if h>=42 and w>=112:return 7,12
 if h>=34 and w>=96:return 6,10
 return 5,9
def minsize(g):return 80+8*(g.cols-9),27+3*(g.rows-5)
class Garden:
 def __init__(self,seed=None,rows=5,cols=9):
  self.rows=rows;self.cols=cols
  self.rng=random.Random(seed);self.energy=200;self.wave=0;self.maxwaves=10;self.score=0;self.lives=5;self.plants={};self.enemies=[];self.shots=[];self.fx=[];self.mowers=[True]*rows;self.over=False;self.won=False;self.timer=0;self.sky=0;self.gap=3;self.pending=0;self.spawnclock=0;self.message='Plant growers and shooters. First wave in 3 seconds.';self.cool=[0.,0.,0.,0.];self.up={}
 def lvl(self,key):return self.up.get(key,0)
 def grower_gain(self):return 25+10*self.lvl('soil')
 def shot_damage(self):return 25+10*self.lvl('seeds')
 def wall_hp(self):return 500+300*self.lvl('walls')
 def cool_mult(self):return 1-.25*self.lvl('packets')
 def buy(self,i):
  if self.over:return False
  if not (0<=i<len(UPGRADES)):return False
  u=UPGRADES[i];lvl=self.lvl(u['key'])
  if u['key']=='mowers':
   if all(self.mowers):self.message='All mowers are ready.';return False
  elif lvl>=u['max']:self.message=u['name']+' is maxed out.';return False
  if self.energy<u['cost']:self.message='Need '+str(u['cost'])+' glow.';return False
  self.energy-=u['cost']
  if u['key']=='mowers':self.mowers=[True]*self.rows;self.message='Every mower is ready again!'
  elif u['key']=='heart':self.up['heart']=lvl+1;self.lives+=1;self.message='House health is now '+str(self.lives)+'.'
  else:self.up[u['key']]=lvl+1;self.message=u['name']+' level '+str(lvl+1)+'.'
  return True
 def place(self,row,col,kind):
  if self.over:return False
  q=(row,col)
  if not (0<=row<self.rows and 0<=col<self.cols and kind in range(4)):return False
  if q in self.plants:self.message='That bed is occupied.';return False
  if self.energy<COSTS[kind]:self.message='Need '+str(COSTS[kind])+' glow.';return False
  if self.cool[kind]>0:self.message='Seed packet recharging.';return False
  self.energy-=COSTS[kind];self.cool[kind]=(2,1,5,10)[kind]*self.cool_mult()
  self.plants[q]=dict(kind=kind,hp=(100,100,self.wall_hp(),100)[kind],clock=0.)
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
    lane=self.rng.randrange(self.rows);armor=self.wave>=3 and self.rng.random()<.25;fast=self.wave>=5 and self.rng.random()<.2
    self.enemies.append(dict(row=lane,x=self.cols+0.2,hp=260 if armor else 100,speed=.24 if fast else .13+.008*self.wave,armor=armor,fast=fast,bite=0));self.pending-=1;self.spawnclock=max(.55,2-self.wave*.1)
  for q,p in list(self.plants.items()):
   p['clock']+=dt;row,col=q
   if p['kind']==0 and p['clock']>=8:p['clock']-=8;self.energy+=self.grower_gain()
   if p['kind']==1 and p['clock']>=1.4 and any(e['row']==row and e['x']>=col for e in self.enemies):p['clock']=0;self.shots.append(dict(row=row,x=col+.5,damage=self.shot_damage()))
   if p['kind']==3 and p['clock']>=1:
    for e in self.enemies:
     if abs(e['row']-row)<=1 and abs(e['x']-col)<=1.5:e['hp']-=1000
    self.fx.append((row,col,.55));self.plants.pop(q,None);self.message='Burstbulb exploded!'
  for shot in list(self.shots):
   old=shot['x'];shot['x']+=4*dt
   hits=[e for e in self.enemies if e['row']==shot['row'] and old-.1<=e['x']<=shot['x']+.18 and e['hp']>0]
   if hits:
    target=min(hits,key=lambda e:e['x']);target['hp']-=shot['damage'];self.shots.remove(shot)
   elif shot['x']>self.cols+1:self.shots.remove(shot)
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
 h,w=s.getmaxyx();rows,cols=gridsize(h,w)
 g=Garden(rows=rows,cols=cols);last=time.monotonic();row=2;col=2;kind=0;paused=False;recorded=False;high=best();pixels=sprites.supported() and '--ascii' not in sys.argv;colors=palette();menu=False;sel=0
 def color(i):return curses.color_pair(i) if colors else 0
 while True:
  s.timeout(90 if pixels else 30);key=s.getch();now=time.monotonic();dt=now-last;last=now;h,w=s.getmaxyx();s.erase()
  if key in (ord('q'),ord('Q')):return
  if key==27:
   if menu:menu=False;s.clear()
   else:return
  if key in (ord('p'),ord('P')):paused=not paused
  if key in (ord('v'),ord('V')):pixels=not pixels;s.clear()
  if key in (ord('u'),ord('U')):menu=not menu;s.clear()
  if key in (ord('r'),ord('R')):
   rows,cols=gridsize(h,w);g=Garden(rows=rows,cols=cols);paused=False;recorded=False;menu=False
   row=min(row,g.rows-1);col=min(col,g.cols-1)
  mw,mh=minsize(g)
  if h<mh or w<mw:put(s,1,1,'Resize to '+str(mw)+'x'+str(mh)+'. Simulation paused. Q quits.');s.refresh();continue
  if menu:
   if key in (curses.KEY_UP,ord('w'),ord('W')):sel=(sel-1)%len(UPGRADES)
   if key in (curses.KEY_DOWN,ord('s'),ord('S')):sel=(sel+1)%len(UPGRADES)
   if key in (ord(' '),10,13):g.buy(sel)
  elif not paused and not g.over:
   if key in (curses.KEY_UP,ord('w'),ord('W')):row=max(0,row-1)
   if key in (curses.KEY_DOWN,ord('s'),ord('S')):row=min(g.rows-1,row+1)
   if key in (curses.KEY_LEFT,ord('a'),ord('A')):col=max(0,col-1)
   if key in (curses.KEY_RIGHT,ord('d'),ord('D')):col=min(g.cols-1,col+1)
   if key in (ord('1'),ord('2'),ord('3'),ord('4')):kind=key-ord('1')
   if key in (ord(' '),10,13):g.place(row,col,kind)
   if key in (ord('x'),ord('X')):g.shovel(row,col)
   if key in (ord('n'),ord('N')):g.gap=0;g.startwave()
  if not paused and not g.over:g.tick(dt)
  if g.over and not recorded:g.message+=' Best saved.' if save(g.score) else ' Save unavailable.';recorded=True;high=max(high,best())
  put(s,0,2,'SPROUTGUARD | WAVE '+str(g.wave)+'/10 | GLOW '+str(g.energy)+' | HOUSE '+str(g.lives)+' | SCORE '+str(g.score),color(3)|curses.A_BOLD)
  put(s,1,2,('PAUSED | ' if paused else '')+g.message,color(2))
  packets=' | '.join(('>' if i==kind else '')+str(i+1)+' '+name+' '+str(COSTS[i]) for i,name in enumerate(('Grow','Spit','Wall','Bomb')))
  put(s,2,2,packets,color(4))
  cw=max(7,(w-8)//(g.cols+1));rh=max(3,(h-9)//g.rows);ox=(w-cw*(g.cols+1))//2;oy=4
  if menu:
   n=len(UPGRADES);bw=min(max(len(u['name'])+len(u['desc'])+28 for u in UPGRADES),w-4)
   bx=(w-bw)//2;by=max(3,(h-(n+6))//2);bar='+'+'-'*(bw-2)+'+'
   put(s,by,bx,bar,color(3));put(s,by+n+5,bx,bar,color(3))
   glows='glow '+str(g.energy)
   put(s,by+1,bx+2,'UPGRADES',color(3)|curses.A_BOLD);put(s,by+1,bx+bw-2-len(glows),glows,color(3))
   for yy in range(2,n+5):put(s,by+yy,bx,'|',color(3));put(s,by+yy,bx+bw-1,'|',color(3))
   for i,u in enumerate(UPGRADES):
    lvl=g.lvl(u['key'])
    if u['key']=='mowers':status='READY' if all(g.mowers) else 'RESTORE';maxed=all(g.mowers)
    else:maxed=lvl>=u['max'];status='MAX' if maxed else 'Lv '+str(lvl)+'/'+str(u['max'])
    afford=not maxed and g.energy>=u['cost']
    line='%-13s %3d glow  %-8s %s'%(u['name'],u['cost'],status,u['desc'])
    attr=color(3) if maxed else color(7) if afford else color(5)
    if i==sel:attr|=curses.A_BOLD
    put(s,by+3+i,bx+2,('> ' if i==sel else '  ')+line,attr)
   put(s,by+n+4,bx+2,'Arrows/WASD choose | Space buy | U/Esc close',color(4))
  else:
   if not pixels:
    for rr in range(g.rows):
     for cc in range(g.cols):
      for yy in range(rh):put(s,oy+rr*rh+yy,ox+(cc+1)*cw,('['+' '*(cw-2)+']') if (rr,cc)==(row,col) and yy==rh//2 else '.'*cw,color(1))
    for (rr,cc),plant in g.plants.items():put(s,oy+rr*rh+rh//2,ox+(cc+1)*cw+2,('SUN','PEW','WALL','BOOM')[plant['kind']],color(3 if plant['kind']==0 else 7))
    for e in g.enemies:put(s,oy+e['row']*rh+rh//2,ox+max(0,min((g.cols+1)*cw-3,round((e['x']+1)*cw))), 'Z#' if e['armor'] else 'Z>' if e['fast'] else 'Z!',color(5))
    for sh in g.shots:put(s,oy+sh['row']*rh+rh//2,ox+max(0,min((g.cols+1)*cw-1,round((sh['x']+1)*cw))), '*',color(7))
    for rr in range(g.rows):
     for yy in range(rh):put(s,oy+rr*rh+yy,ox,('MOW' if yy==rh//2 else '...') if g.mowers[rr] else '...',color(3 if g.mowers[rr] else 5))
  put(s,h-4,2,'LAWN '+str(g.rows)+'x'+str(g.cols)+' | SELECT '+str(row+1)+','+str(col+1)+' | '+NAMES[kind]+' ['+str(round(g.cool[kind],1))+'s] | Pending '+str(g.pending)+' | BEST '+str(high),color(3))
  put(s,h-3,2,'Arrows/WASD bed | 1-4 seed | Space/Enter plant | X shovel (no refund)',color(4))
  put(s,h-2,2,'U upgrades | N start wave early | P pause | V pixel/text | R restart | Q quit',color(2))
  put(s,h-1,2,'Glow +25 each 5s; growers +25 each 8s. Mower strip left of the lawn: one emergency mower per lane.',color(7));s.refresh()
  if pixels and not menu:sys.stdout.write(sprites.frame(g,w,h,row,col));sys.stdout.flush()
if __name__=='__main__':
 if '--version' in sys.argv:print(VERSION)
 else:raise SystemExit(run(play))
