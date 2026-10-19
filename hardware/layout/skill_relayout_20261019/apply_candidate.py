from pathlib import Path
from datetime import datetime
import shutil,json
import pcbnew as p

work=Path(__file__).resolve().parent
live=work.parents[1]/'schematic/v1.0/GPSDO_Rev1.0/GPSDO_Rev1.0.kicad_pcb'
baseline=p.LoadBoard(str(work/'baseline.kicad_pcb'))
current=p.LoadBoard(str(live))
candidate=p.LoadBoard(str(work/'candidate.kicad_pcb'))
def signature(board):
 return sorted((f.m_Uuid.AsString(),f.GetReference(),f.GetValue(),
                q.m_Uuid.AsString(),q.GetNumber(),q.GetNetname())
               for f in board.GetFootprints() for q in f.Pads())
assert signature(current)==signature(candidate)==signature(baseline)
assert not list(current.GetTracks()) and not list(current.Zones())
assert candidate.GetCopperLayerCount()==4
old={f.GetReference():f for f in current.GetFootprints()}
new={f.GetReference():f for f in candidate.GetFootprints()}
assert len(new)==157 and all(f.GetLayer()==p.F_Cu for f in new.values())
for ref in ['U5','U7','USB1','J1','J4','RF1','RF2','C5','R13','H1','H2','H3','H4']:
 a,c=old[ref].GetPosition(),new[ref].GetPosition()
 assert abs(p.ToMM(a.x-c.x))<.001 and abs(p.ToMM(a.y-c.y))<.001,ref
settings=candidate.GetDesignSettings();original_settings=current.GetDesignSettings()
settings.SetAuxOrigin(original_settings.GetAuxOrigin())
settings.SetGridOrigin(original_settings.GetGridOrigin())
backup=live.parent/'.history'/('before_skill_relayout_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.kicad_pcb')
shutil.copy2(live,backup)
p.SaveBoard(str(live),candidate)
check=p.LoadBoard(str(live)); assert signature(check)==signature(current)
print('Saved live PCB:',live)
print('Backup:',backup)
print('157 front-side parts; nets and mechanical anchors verified; no routing added.')
