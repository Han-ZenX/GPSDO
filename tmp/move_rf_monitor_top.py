from pathlib import Path
from datetime import datetime
import shutil
import pcbnew as p

root=Path('hardware/schematic/v1.0/GPSDO_Rev1.0')
path=root/'GPSDO_Rev1.0.kicad_pcb'
backup=root/'.history'/('before_move_rf_monitor_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.kicad_pcb')
shutil.copy2(path,backup)
b=p.LoadBoard(str(path))
assert not list(b.GetTracks())
fs={f.GetReference():f for f in b.GetFootprints()}
signature=lambda: sorted((f.m_Uuid.AsString(),q.m_Uuid.AsString(),q.GetNumber(),q.GetNetname()) for f in fs.values() for q in f.Pads())
before=signature()
for ref,x,y,angle in [('RF2',16.5,3.6,180),('C5',19.7,5.4,0),('R13',22,5.4,0)]:
 f=fs[ref]
 f.SetOrientationDegrees(angle)
 f.SetPosition(p.VECTOR2I(p.FromMM(106.415+x),p.FromMM(63.44+y)))
 f.Reference().SetPosition(f.GetPosition())
 f.Value().SetPosition(f.GetPosition())
 assert not f.Reference().IsVisible()
 q=f.GetBoundingBox(False,False)
 assert p.ToMM(q.GetX())>106.415+.5 and p.ToMM(q.GetY())>63.44+.5
 for other in fs.values():
  if other is f: continue
  assert not q.Intersects(other.GetBoundingBox(False,False)), (ref,other.GetReference())
assert signature()==before
p.SaveBoard(str(path),b)
print('Moved RF2, C5, R13 above OCXO. No body intersections; nets unchanged.')
print('Backup:',backup)
