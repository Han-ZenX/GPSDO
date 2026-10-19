import pcbnew as p, json, shutil
from pathlib import Path
from datetime import datetime

root=Path('hardware/schematic/v1.0/GPSDO_Rev1.0')
path=root/'GPSDO_Rev1.0.kicad_pcb'
backup=root/'.history'/'before_placement_20261019.kicad_pcb'
backup.parent.mkdir(exist_ok=True)
if not backup.exists(): shutil.copy2(path,backup)
b=p.LoadBoard(str(backup))
fps={f.GetReference():f for f in b.GetFootprints()}
ocxo_delta=fps['U5'].GetPosition()-fps['U7'].GetPosition()
b.SetCopperLayerCount(4)
X,Y=106.415,63.44
positions={}
def group(items):
 for line in items.strip().splitlines():
  a=line.split(); positions[a[0]]=(float(a[1]),float(a[2]),float(a[3]) if len(a)>3 else 0)

# Coordinates are millimetres relative to the existing top-left board corner.
# Keep the two OCXO footprints' original translation and orientation relationship.
group('''
U7 21 20
U5 21.033 16.563
H1 4 4
H2 71 4
H3 4 71
H4 71 71
U6 60 16 180
RF1 70 10 90
L1 69 13.5 90
R1 69 22 0
R8 69 16 0
R2 50 18.7 0
R3 50 21 0
C8 50 23.3 0
R9 46 23.3 0
C7 51.3 25 0
C6 49.5 27.2 0
FB8 53 29.3 90
USB1 3 41 -90
U11 12 41 90
R11 8 37 90
R14 8 45 90
FB6 14 46 0
C27 11.3 44.2 0
C28 11.5 47.7 0
CN1 3.8 53 -90
F1 7 48.8 0
U18 12 52 0
C68 9 51.5 90
C69 12 49 0
C70 14.7 52 90
C71 16.7 52 90
R43 9 55 0
R44 12 55 0
C25 17 48.7 0
C43 17 46.7 0
D8 8 64 0
R45 8 61.5 0
U14 23 52 0
C34 20 50.5 90
C37 26.5 50.5 90
C35 20.5 54 0
R26 26 53.2 0
R30 26 55 0
C36 28.8 53.2 90
R27 22.5 55 0
D1 23 59 0
R53 23 57 0
U16 15 61 0
C38 12 59.5 90
C41 18.5 59.5 90
C39 12.5 63 0
R32 18 62.3 0
R33 18 64.1 0
C40 20.8 62.3 90
R31 14.5 64.1 0
R22 15 67 0
R23 19.5 67 0
D2 11 68 0
R34 11 66 0
U4 33 57.5 0
L2 30 57.5 90
C72 35.8 54 0
C73 35.7 55.9 0
C74 30 60.4 0
C75 30 63.2 0
R51 35.7 59 0
R52 35.7 60.8 0
R50 39 57.5 90
R49 39 54.8 0
U13 46 62 -90
C46 48 58.7 0
C47 51.7 58.7 0
C48 45.8 65.5 0
C49 45.8 67.5 0
R42 42.5 59 90
R46 44.5 58.2 90
R20 42 65 90
R47 50 65 90
J1 34 71.94 -90
J4 58 71.94 -90
D6 34 67.5 -90
D9 58 67.5 -90
U15 57 45 180
C13 62 41.8 90
C14 52 43.5 90
C15 52 46.3 90
C32 54.3 50 0
C33 62 46.2 90
FB1 54 52.3 0
C42 57 40 0
R48 62.4 42.8 0
R38 51.5 49.2 0
J3 70 54.5 0
D3 71 37 0
D4 71 41 0
D5 71 45 0
R21 67.5 37 0
R24 67.5 41 0
R25 67.5 45 0
U1 43 29 180
JP1 43 23 0
C12 45.7 33.1 0
C10 46.3 35.3 0
C9 42.5 33.5 0
R10 39.5 32.8 90
FB2 49.8 33.5 90
U2 20 37.5 -90
C3 20.8 41.5 90
C4 19 40.1 0
FB3 16.5 41.5 0
R6 25 36.8 0
R7 25 39.3 0
R36 14 35 0
R37 16.5 35 0
R4 19 34.7 0
R13 10.5 34.8 90
C5 7.5 34.8 0
RF2 4.2 31 0
U3 35.7 32.5 0
C16 36 35 0
R12 33 36.5 0
R15 33 38.5 0
R16 36 37 0
U8 44 41 0
R28 40.7 46 0
C56 44 46 0
C11 43.3 44 0
C57 46.8 36.9 90
C58 42.5 36.6 0
R29 46.5 39 90
U9 33 44 90
U10 43 50 0
C22 46 51 90
C24 40 51 90
R35 46 48 0
R19 39 47.5 90
R18 36 42 90
C20 38.5 42 90
C21 36 46 0
R17 29.2 42.5 90
C19 28.3 39 90
C17 29 46 0
C18 29 44 0
FB7 29 48.5 0
R39 30 35.8 90
R40 30 33.5 0
R41 33 34.5 90
C26 36.2 38.8 0
C23 4 17 90
C1 6.4 10.5 90
C2 4 10.5 90
FB4 4 21.8 90
FB5 6.8 21.8 90
R5 5 25.5 0
TP1 4 6.8 0
TP2 7 6.8 0
''')
group('''
TP1 3 27.5
TP2 7 28
C12 45.7 33.5
C10 44 35.5
C57 48.5 37 90
R29 48.5 40 90
C11 40 44.5 90
C56 39.4 36.8
R28 39.5 39
U9 31 44 90
C21 35.8 48.2
R17 26.5 43 90
C19 26 40 90
C17 25.5 48
C18 26.3 45.7
FB7 29.5 50
R6 26 35
R7 26 37
R37 17 34.5
R4 21 34.5
F1 7 47
C69 12 49.5
C25 18 44.5
C35 20.5 54.6
C39 11.9 63.5
R48 64 43.5
D6 34 66.5 -90
D9 58 66.5 -90
''')
group('''
TP1 2 27.5
F1 6 48
CN1 3.8 54 -90
R29 48.5 40.5 90
C10 47 31.8
R17 26.5 43.4 90
USB1 4.5 41 -90
R11 8.8 37 90
R14 8.8 45 90
C10 47.7 31.8
FB2 50.5 33.5 90
C14 50.5 45.5 90
C33 59.8 50.3
R20 42 65 -90
R47 50 65 -90
C74 30 60.4 180
C75 30 63.2 180
''')
assert set(positions)==set(fps), ('missing',set(fps)-set(positions),'extra',set(positions)-set(fps))
for ref,(x,y,angle) in positions.items():
 f=fps[ref]
 f.SetOrientationDegrees(angle)
 f.SetPosition(p.VECTOR2I(p.FromMM(X+x),p.FromMM(Y+y)))
 f.Value().SetVisible(False)
 r=f.Reference(); r.SetVisible(True); r.SetTextSize(p.VECTOR2I(p.FromMM(.8),p.FromMM(.8)));r.SetTextThickness(p.FromMM(.12));r.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
 q=f.GetBoundingBox(False,False)
 r.SetPosition(p.VECTOR2I(f.GetPosition().x,q.GetY()-p.FromMM(.9)))

fps['U5'].SetPosition(fps['U7'].GetPosition()+ocxo_delta)

# Fit readable reference fields into available space; dense passives retain
# their reference on the assembly layer instead of printing on nearby pads.
def rect(q,margin=0):
 return [p.ToMM(q.GetX())-margin,p.ToMM(q.GetY())-margin,p.ToMM(q.GetRight())+margin,p.ToMM(q.GetBottom())+margin]
def overlap(a,c): return a[0]<c[2] and c[0]<a[2] and a[1]<c[3] and c[1]<a[3]
occupied=[rect(f.GetBoundingBox(False,False),.2) for f in fps.values()]
labels=[]; fab=[]
for f in sorted(fps.values(),key=lambda f:(not f.GetReference().startswith(('U','J','CN','RF','D')),f.GetReference())):
 r=f.Reference(); r.SetLayer(p.F_SilkS)
 q=rect(f.GetBoundingBox(False,False)); cx=p.ToMM(f.GetPosition().x); cy=p.ToMM(f.GetPosition().y)
 width=.8*len(f.GetReference())*.85+.25
 candidates=[]
 for gap in [.8,1.4,2,2.8]:
  for shift in [0,-1.5,1.5,-3,3]:
   candidates += [(cx+shift,q[1]-gap),(cx+shift,q[3]+gap),(q[0]-width/2-gap,cy+shift),(q[2]+width/2+gap,cy+shift)]
 placed=False
 for x,y in candidates:
  r.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)))
  box=rect(r.GetBoundingBox(),.22)
  if box[0]<X+.3 or box[2]>X+74.7 or box[1]<Y+.3 or box[3]>Y+74.7: continue
  if any(overlap(box,t) for t in occupied+labels): continue
  labels.append(box); placed=True; break
 if not placed:
  r.SetLayer(p.F_Fab); r.SetPosition(f.GetPosition()); fab.append(f.GetReference())

p.SaveBoard(str(path),b)
print('Placed',len(fps),'footprints. Backup:',backup)
print('Dense reference fields on assembly layer:',fab)
