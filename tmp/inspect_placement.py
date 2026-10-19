import pcbnew as p, json
from pathlib import Path
path=Path('hardware/schematic/v1.0/GPSDO_Rev1.0/GPSDO_Rev1.0.kicad_pcb')
b=p.LoadBoard(str(path))
def mm(v): return round(p.ToMM(v),3)
data=[]
for f in b.GetFootprints():
 q=f.GetBoundingBox(False,False)
 data.append(dict(ref=f.GetReference(),value=f.GetValue(),pos=[mm(f.GetPosition().x),mm(f.GetPosition().y)],angle=f.GetOrientationDegrees(),box=[mm(q.GetX()),mm(q.GetY()),mm(q.GetWidth()),mm(q.GetHeight())],sheet=f.GetSheetname(),pads=[dict(n=x.GetNumber(),net=x.GetNetname(),pos=[mm(x.GetPosition().x),mm(x.GetPosition().y)]) for x in f.Pads()]))
out={'footprints':data,'edges':[dict(shape=str(x.GetShape()),start=[mm(x.GetStart().x),mm(x.GetStart().y)],end=[mm(x.GetEnd().x),mm(x.GetEnd().y)]) for x in b.GetDrawings() if x.GetLayer()==p.Edge_Cuts],'tracks':len(list(b.GetTracks())),'zones':len(list(b.Zones()))}
Path('tmp/placement_inventory.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='footprints'}))
for f in sorted(data,key=lambda x:x['sheet']+x['ref']): print(f['ref'],f['value'],f['sheet'],f['pos'],f['angle'],f['box'][2:])
