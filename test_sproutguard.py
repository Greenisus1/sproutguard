import unittest,tempfile
from pathlib import Path
from unittest.mock import patch
import sproutguard as a

def enemy(row=0,x=5,hp=100):return dict(row=row,x=x,hp=hp,speed=.2,armor=False,fast=False,bite=0)
class Tests(unittest.TestCase):
 def test_initial(self):
  g=a.Garden(1);self.assertEqual(g.energy,200);self.assertEqual(g.lives,5)
 def test_place(self):
  g=a.Garden();self.assertTrue(g.place(0,0,0));self.assertEqual(g.energy,150);self.assertFalse(g.place(0,0,1));self.assertFalse(g.place(0,1,0))
 def test_bounds_cost(self):
  g=a.Garden();self.assertFalse(g.place(-1,0,0));g.energy=0;self.assertFalse(g.place(0,0,1))
 def test_sun(self):
  g=a.Garden();g.gap=999;g.place(0,0,0)
  for _ in range(81):g.tick(.1)
  self.assertEqual(g.energy,200)
 def test_shoots(self):
  g=a.Garden();g.gap=999;g.place(0,0,1);g.enemies=[enemy()]
  for _ in range(15):g.tick(.1)
  self.assertTrue(g.shots)
 def test_lane(self):
  g=a.Garden();g.gap=999;g.place(0,0,1);g.enemies=[enemy(row=1)]
  for _ in range(20):g.tick(.1)
  self.assertFalse(g.shots)
 def test_bullet(self):
  g=a.Garden();g.gap=999;g.enemies=[enemy(x=1,hp=25)];g.shots=[dict(row=0,x=.8,damage=25)];g.tick(.1);self.assertFalse(g.enemies);self.assertEqual(g.score,10)
 def test_bite(self):
  g=a.Garden();g.gap=999;g.place(0,1,2);g.enemies=[enemy(x=1)];g.tick(.1);self.assertEqual(g.plants[0,1]['hp'],497)
 def test_bomb(self):
  g=a.Garden();g.gap=999;g.place(2,3,3);g.enemies=[enemy(2,3),enemy(1,3),enemy(0,3)]
  for _ in range(11):g.tick(.1)
  self.assertEqual(len(g.enemies),1);self.assertNotIn((2,3),g.plants)
 def test_mower(self):
  g=a.Garden();g.gap=999;g.enemies=[enemy(0,-.5),enemy(0,4)];g.tick(.1);self.assertFalse(g.mowers[0]);self.assertFalse(g.enemies);self.assertEqual(g.lives,5)
 def test_house(self):
  g=a.Garden();g.gap=999;g.mowers[0]=False;g.enemies=[enemy(0,-.5)];g.tick(.1);self.assertEqual(g.lives,4)
 def test_loss(self):
  g=a.Garden();g.gap=999;g.lives=1;g.mowers[0]=False;g.enemies=[enemy(0,-.5)];g.tick(.1);self.assertTrue(g.over)
 def test_wave(self):
  g=a.Garden(1);g.gap=0;self.assertTrue(g.startwave());self.assertEqual(g.pending,6);g.tick(.1);self.assertEqual(len(g.enemies),1)
 def test_clear(self):
  g=a.Garden();g.wave=1;g.gap=0;g.tick(.1);self.assertEqual(g.gap,8);self.assertEqual(g.score,100)
 def test_win(self):
  g=a.Garden();g.wave=10;g.gap=0;g.tick(.1);self.assertTrue(g.won);self.assertTrue(g.over)
 def test_shovel(self):
  g=a.Garden();g.place(0,0,0);g.shovel(0,0);self.assertFalse(g.plants);self.assertEqual(g.energy,150)
 def test_record(self):
  with tempfile.TemporaryDirectory() as d,patch.object(a,'RECORD',Path(d)/'best.json'):
   self.assertTrue(a.save(111));a.save(2);self.assertEqual(a.best(),111)
 def test_art(self):
  import sprites
  for name,rows in sprites.ART.items():self.assertEqual(len(rows),8);self.assertTrue(all(len(r)==8 for r in rows));self.assertTrue(all(c in sprites.PALETTE for r in rows for c in r))
 def test_frame(self):
  import sprites
  for w,h in ((80,27),(110,40),(180,65)):self.assertIn('38;2;',sprites.frame(a.Garden(),w,h,2,2))
if __name__=='__main__':unittest.main()
