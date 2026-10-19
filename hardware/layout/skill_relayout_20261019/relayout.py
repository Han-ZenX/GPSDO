"""Project placement recipes using the installed KiCad placement skill.

Runs in the work directory and writes a candidate board, never the live PCB.
Numeric limits are project placement targets, not manufacturer guarantees.
"""
from pathlib import Path
import json, math, shutil, sys, types, xml.etree.ElementTree as ET
import pcbnew as p

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'skill_scripts'))
import autoplace as A
import recipes as R
from pcblib import Board

X,Y=106.415,63.44
b=Board(str(HERE),'baseline',size=(75,75),origin=(X,Y),cli='F:/KiCad/10.0/bin/kicad-cli.exe')
b._netlist_root=lambda: ET.parse(HERE/'netlist.xml').getroot()
model=A.Model(b)
A.selftest(b,model)
fps={f.GetReference():f for f in b.board.GetFootprints()}
assert len(fps)==157 and not list(b.board.GetTracks())

# Board/schematic parity is checked pad by pad, excluding unnamed mechanical pads.
parity=[]
for ref,part in model.parts.items():
 for pad in fps[ref].Pads():
  n=pad.GetNumber()
  if n and part.nets.get(n) and pad.GetNetname().replace('{slash}','/')!=part.nets[n]:
   parity.append((ref,n,pad.GetNetname(),part.nets[n]))
assert not parity,parity

sources={
 'U4':'https://www.ti.com/lit/ds/symlink/tps61023.pdf section 10.1',
 'U14':'https://www.ti.com/lit/ds/symlink/tps7a52.pdf section 10.1',
 'U16':'https://www.ti.com/lit/ds/symlink/tps7a52.pdf section 10.1',
 'U1':'https://www.ti.com/lit/ds/symlink/tdc7200.pdf sections 10-11',
 'U13':'https://www.renesas.com/en/document/dst/isl55110-isl55111-datasheet Bypassing/Output Damping',
}
rules=[]
def recipe(owner,rows):
 for line in rows.strip().splitlines():
  ref,pin,limit,priority=line.split()
  rules.append(dict(ref=ref,owner=owner,pin=pin,limit=float(limit),priority=int(priority),
                    source=sources.get(owner,'Project pin/net-derived placement; same-side local support')))

recipe('U4','''
C74 6 1.8 0
L2 5 2.2 1
C73 3 1.5 2
C72 3 3.0 3
C75 6 3.5 4
R51 1 2.0 5
R52 1 2.0 6
R50 2 3.0 7
R49 2 3.5 8
''')
for owner,rows in [('U14','''
C34 1 2.3 0
C37 11 2.3 1
C35 4 2.0 2
R26 9 2.0 3
R30 9 2.0 4
C36 9 2.5 5
R27 8 3.0 6
'''),('U16','''
C38 1 2.3 0
C41 11 2.3 1
C39 4 2.0 2
R32 9 2.0 3
R33 9 2.0 4
C40 9 2.5 5
R31 8 3.0 6
''')]: recipe(owner,rows)
recipe('U13','''
C48 10 1.5 0
C46 1 1.5 1
R20 9 2.5 2
R47 12 2.5 3
C49 10 3.5 4
C47 1 3.5 5
R42 5 3.5 6
R46 4 3.5 7
''')
recipe('U1','''
C12 14 1.5 0
C9 13 1.7 1
C10 14 3.5 2
R10 8 3.5 3
FB2 14 5.0 4
JP1 4 3.5 5
''')
recipe('U15','''
C13 48 1.8 0
C14 23 1.8 1
C15 21 1.8 2
C32 35 1.8 3
C33 1 1.8 4
C42 7 2.5 5
R48 46 3.0 6
FB1 23 5.0 7
R38 22 3.0 8
''')
recipe('U6','''
C7 23 1.8 0
C8 22 2.2 1
C6 23 3.5 2
R2 20 2.5 3
R3 21 3.0 4
R1 3 2.5 5
L1 11 3.5 6
R8 7 3.0 7
R9 22 3.5 8
FB8 23 5.0 9
''')
recipe('U2','''
C4 6 1.5 0
C3 6 3.0 1
R6 8 2.5 2
R7 5 2.5 3
R36 1 2.5 4
R37 1 3.5 5
FB3 6 4.5 6
''')
recipe('U9','''
C18 7 1.5 0
C17 7 3.0 1
C20 3 2.0 2
R18 3 2.5 3
R17 6 2.5 4
C21 6 4.0 5
FB7 7 5.0 6
''')
recipe('U10','''
C22 1 1.5 0
C24 6 1.5 1
R35 3 3.0 2
R19 4 4.0 3
''')
recipe('U8','''
C11 2 1.5 0
C58 6 2.5 1
C57 5 2.5 2
C56 2 3.5 3
R29 6 3.5 4
R28 2 4.0 5
''')
recipe('U11','''
C27 10 1.5 0
C28 10 3.0 1
FB6 7 4.5 2
''')
recipe('USB1','''
R11 A5 3.0 0
R14 B5 3.0 1
''')
recipe('U18','''
C70 2 1.5 0
C68 3 2.3 1
C69 6 2.3 2
C71 7 3.5 3
R43 4 2.5 4
R44 4 2.5 5
C25 7 4.5 6
C43 2 3.0 7
''')
recipe('U3','''
C16 5 1.5 0
R12 6 3.0 1
R16 1 3.0 2
R15 3 3.0 3
''')
assert len({r['ref'] for r in rules})==len(rules)
# Whole-body/courtyard clearance imposes a finite pad-centre separation.
# These package-aware targets are applied equally to baseline and candidate.
package_limits={'C34':2.4,'C38':2.4,'L2':2.5,'C9':2.2,
                'C18':1.9,'C20':2.3,'C11':2.0,'C16':2.0,'C27':1.9}
for r in rules:
 if r['ref'] in package_limits: r['limit']=package_limits[r['ref']]
 if r['owner']=='U4':
  r['priority']={'C74':0,'L2':1,'R51':2,'R52':3,'C73':4,'C72':5,'C75':6,'R50':7,'R49':8}[r['ref']]

original={r:(q.x,q.y,q.rot,q.bottom) for r,q in model.parts.items()}
pos=dict(original)
anchors={'U1':(43,28,180,False),'U2':(19,36.5,270,False),'U3':(36.5,27,0,False),
         'U15':(59,43,180,False),'U8':(47,40,0,False),'U9':(31,45,90,False),
         'U10':(43,52,0,False),'U4':(34,61,0,False),
         'U14':(23.4,53,0,False),'U16':(12,62,0,False)}
pos.update(anchors)
pos.update({'R39':(62,33.5,90,False),'R40':(62,35.8,0,False),
            'R41':(64.8,33.5,90,False),'C26':(64.8,35.8,0,False),
            'R4':(21,33.6,0,False)})

# Explicit rectangular routing islands. Chip-specific support can only move
# within its own island; this prevents the global-rail capacitor pile failure.
regions={
 'U4':(28.5,56.5,40,68), 'U14':(18,49,28.3,59.5),
 'U16':(7.2,58,18,68),'U18':(7.5,47,17.8,57.8),
 'U13':(41.8,57.8,55,69.6),'U1':(38,20.5,49,35),
 'U15':(52,36.5,66,51),'U6':(48,6,73,28),
 'U2':(12,33.2,27.5,42.5),'U3':(34.2,24.5,39.5,33),
 'U9':(24,38.5,40,50),'U10':(38.5,49.5,48,56.2),
 'U8':(40.2,33.8,52.5,47.8),'U11':(8,36,17.7,45.8),
 'USB1':(7.7,35,10.4,45.5)}

# Local full-body extents are combined with skill pad/courtyard extents.
body={}
for ref,q in model.parts.items():
 f=fps[ref]; old=f.GetPosition(); ang=f.GetOrientationDegrees()
 f.SetPosition(p.VECTOR2I(0,0));f.SetOrientationDegrees(0)
 box=f.GetBoundingBox(False,False)
 body[ref]=A.union([q.rect,(p.ToMM(box.GetX()),p.ToMM(box.GetY()),p.ToMM(box.GetRight()),p.ToMM(box.GetBottom()))])
 f.SetPosition(old);f.SetOrientationDegrees(ang)

def extent(ref,pose): return A.xrect(body[ref],*pose)
def intersects(a,c,gap=.23): return A.overlap(A.grow(a,gap/2),A.grow(c,gap/2))

class PinSolver(A.Solver):
 def _member_cost(self,mem,x,y,rot,bottom,frame):
  rule=mem.rule; owner=model.parts[rule['owner']]; part=mem.part
  target=owner.nets[rule['pin']]
  tx,ty=A.pad_xy(owner,rule['pin'],*pos[owner.ref])
  pts=[A.pad_xy(part,n,x,y,rot,bottom) for n,net in part.nets.items() if net==target and n in part.pads]
  d=min(math.hypot(px-tx,py-ty) for px,py in pts)
  d+=max(0,d-rule['limit'])*40
  if part.kind=='C':
   mine=[A.pad_xy(part,n,x,y,rot,bottom) for n,net in part.nets.items() if net in model.ground and n in part.pads]
   grounds=[A.pad_xy(owner,n,*pos[owner.ref]) for n,net in owner.nets.items() if net in model.ground and n in owner.pads]
   if mine and grounds: d+=.35*min(math.dist(a,c) for a in mine for c in grounds)
  # Local non-rail links: close the RC and feedback networks as well as
  # minimizing the distance to the specific pin.
  for net in part.netset()-model.ground-{target}:
   if len(model.nets.get(net,[]))>7: continue
   pts2=[A.pad_xy(part,n,x,y,rot,bottom) for n,nn in part.nets.items() if nn==net and n in part.pads]
   dest=[]
   for ref,pose in frame.items():
    q=model.parts[ref]
    dest += [A.pad_xy(q,n,*pose) for n,nn in q.nets.items() if nn==net and n in q.pads]
   if dest and pts2: d+=.12*min(math.dist(a,c) for a in pts2 for c in dest)
  return d

cfg=types.SimpleNamespace(BOARD_SIZE=(75,75),PART_GAP=.23,BLOCK_GAP=1.5,EDGE_MARGIN=.5)
solver=PinSolver(model,{},cfg)
members={}; blocks={}
for r in rules:
 owner=model.parts[r['owner']];part=model.parts[r['ref']]
 assert r['pin'] in owner.pads and owner.nets[r['pin']] in part.netset(), r
 rc=R.Recipe(owner.value,[],value=owner.value,sources=(r['source'],))
 role=R.Role(r['ref'],part.kind,'*',max_mm=r['limit'],prio=r['priority'])
 mem=A.Member(part,role,rc,([owner.nets[r['pin']]],[]));mem.rule=r
 members[part.ref]=mem
 if owner.ref not in blocks: blocks[owner.ref]=A.Block(owner,rc)
 blocks[owner.ref].members.append(mem)

def exact_audit(poses):
 out=[]
 for r in rules:
  a=model.parts[r['owner']];q=model.parts[r['ref']];net=a.nets[r['pin']]
  target=A.pad_xy(a,r['pin'],*poses[a.ref])
  d=min(math.dist(target,A.pad_xy(q,n,*poses[q.ref])) for n,nn in q.nets.items() if nn==net and n in q.pads)
  out.append(dict(**r,mm=round(d,3),ok=d<=r['limit']+.00001))
 return out

before=exact_audit(original)
pending=set(members)
placed=set(pos)-pending
for owner in ['U4','U13','U1','U15','U6','U2','U8','U9','U10','U14','U16','U18','U11','USB1','U3']:
 for mem in sorted(blocks[owner].members,key=lambda m:m.role.prio):
  rule=mem.rule;ref=mem.part.ref; region=regions[owner]
  def feasible(part,x,y,rot,bottom):
   e=extent(ref,(x,y,rot,bottom))
   if e[0]<region[0] or e[1]<region[1] or e[2]>region[2] or e[3]>region[3]: return False
   if owner=='U4' and ref in {'R51','R52'} and x<pos['U4'][0]+.9: return False
   if owner=='U4' and ref=='L2' and x>pos['U4'][0]-.9: return False
   for other in placed:
    if intersects(e,extent(other,pos[other])): return False
   for hole in ['H1','H2','H3','H4']:
    fp=fps[hole]; box=fp.GetBoundingBox(False,False)
    h=(p.ToMM(box.GetX())-X,p.ToMM(box.GetY())-Y,p.ToMM(box.GetRight())-X,p.ToMM(box.GetBottom())-Y)
    if intersects(e,h): return False
   return True
  frame={r:pos[r] for r in placed if r==owner or (r in members and members[r].rule['owner']==owner)}
  tx,ty=A.pad_xy(model.parts[owner],rule['pin'],*pos[owner])
  best=solver.place_member(mem,frame,feasible,5.5,(tx,ty),(False,))
  if best is None:
   raise RuntimeError('No legal placement in module for '+ref)
  _,x,y,rot,bottom=best
  pos[ref]=(round(x,3),round(y,3),rot,bottom)
  placed.add(ref); pending.remove(ref)
 print('Solved',owner,flush=True)

assert not pending
after=exact_audit(pos)
A.print_audit(A.audit(model,blocks,original),'Skill recipe baseline')
A.print_audit(A.audit(model,blocks,pos),'Skill recipe candidate')
print('EXACT PIN BASELINE',sum(r['ok'] for r in before),'/',len(before),flush=True)
print('EXACT PIN CANDIDATE',sum(r['ok'] for r in after),'/',len(after),flush=True)
json.dump(dict(before=before,after=after,positions=pos,regions=regions,sources=sources),open(HERE/'recipe_audit.json','w'),indent=2)
for ref,pose in pos.items():
 f=fps[ref];x,y,rot,_=pose
 f.SetOrientationDegrees(rot);f.SetPosition(p.VECTOR2I(p.FromMM(X+x),p.FromMM(Y+y)))
 f.Reference().SetVisible(False);f.Value().SetVisible(False)
 f.Reference().SetPosition(f.GetPosition());f.Value().SetPosition(f.GetPosition())
p.SaveBoard(str(HERE/'candidate.kicad_pcb'),b.board)
print('Candidate saved; live board untouched.',flush=True)
