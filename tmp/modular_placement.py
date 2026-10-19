import pcbnew as p, shutil
from pathlib import Path

root=Path('hardware/schematic/v1.0/GPSDO_Rev1.0')
path=root/'GPSDO_Rev1.0.kicad_pcb'
backup=root/'.history/before_modular_placement_20261019.kicad_pcb'
if not backup.exists(): shutil.copy2(path,backup)
b=p.LoadBoard(str(backup))
assert not list(b.GetTracks()), 'Existing routing requires a different placement operation'
fps={f.GetReference():f for f in b.GetFootprints()}
delta=fps['U5'].GetPosition()-fps['U7'].GetPosition()
X,Y=106.415,63.44
groups={}; positions={}
def module(name,rows):
 refs=[]
 for row in rows.strip().splitlines():
  v=row.split(); ref=v[0]
  assert ref not in positions, ref
  positions[ref]=(float(v[1]),float(v[2]),float(v[3]) if len(v)>3 else 0)
  refs.append(ref)
 groups[name]=refs

module('OCXO_OPTIONS', '''
U7 21 20
U5 21.033 16.563
C23 4.3 17 90
C1 6.5 10.5 90
C2 4 10.5 90
FB4 4 22 90
FB5 6.5 22 90
R5 5 24.8
R22 4 27.5
R23 4 30.5
TP1 2 24.5
TP2 7 28
''')
module('U6_GNSS', '''
U6 60 16 180
RF1 70 10 90
L1 69 13.5 90
R8 69 16
R1 69 21
R2 50.5 18
R3 50.5 19.8
C8 50.5 22.1
R9 47.6 22.1 90
C7 53.6 25
C6 50.5 25
FB8 50.5 27.4
''')
module('U2_CLOCK_BUFFER', '''
U2 23 37.5 -90
R4 21 34.6
R36 18 34.7
R37 18 36.8
C3 23.8 41.1 90
C4 22 40.2
FB3 20.7 42
R6 28.4 36.5
R7 28.4 38.5
''')
module('OCXO_RF_MONITOR', '''
RF2 10 35.2
C5 13.2 37
R13 15.5 37
''')
module('U3_TEMPERATURE', '''
U3 36.5 29
C16 36.5 31.4
R12 35.2 33.2
R16 37.7 33.2
R15 36.5 35
''')
module('U1_TDC7200', '''
U1 44 29 180
JP1 44 23.8
C10 48.7 31.8
C12 46.9 33.5
C9 43.6 33.5
FB2 51 32.5 90
R10 40.5 32.8 90
''')
module('U9_TUNING_FILTER', '''
U9 31 45 90
R17 25.9 44.3 90
C19 25.5 40.5 90
C18 25.6 47.2
C17 25.5 49.2
FB7 29 50.2
R18 36.3 43.2 90
C20 38.6 43.2 90
C21 36.6 48.6
R19 39.2 46.7 90
''')
module('U8_VOLTAGE_REFERENCE', '''
U8 46 42.5
C11 45.4 46.9
C56 41.4 45.4 90
R28 42 48.6
C58 45.5 37.4
C57 49.8 39.6 90
R29 49.8 43.2 90
''')
module('U10_PWM_LEVEL', '''
U10 41 53.5
C22 44 54.5 90
C24 38 54.5 90
R35 44 52.2
''')
module('U15_MCU', '''
U15 61 44 180
C13 66 41 90
C14 55.7 44.8 90
C15 55.7 47 90
C32 58.8 48.8
C33 63.5 49
FB1 58 51
C42 63 38.2
R48 66.5 44
R38 55.7 49.3
R39 57.5 35.5 90
R40 57.5 37.8
R41 60.3 35.5 90
C26 60.3 37.8
J3 70 28
''')
module('MCU_STATUS_LEDS', '''
D3 70.5 51
D4 70.5 55
D5 70.5 59
R21 66.5 51
R24 66.5 55
R25 66.5 59
''')
module('U11_USB_UART', '''
USB1 4.5 40 -90
U11 12 40 90
R11 8.8 36 90
R14 8.8 44 90
C27 12 42.6
C28 12 44.5
FB6 15.7 43.7 90
''')
module('U18_POWER_MUX', '''
CN1 3.8 53.5 -90
F1 6 47.5
U18 11.5 51
C68 8.8 51 90
C69 11.5 48.6
C70 14 51 90
C71 16 51 90
R43 9.5 54
R44 12 54
C25 16 54
C43 13.8 48.6
D8 9 56.4
R45 12 56.4
''')
module('U14_MAIN_3V3_LDO', '''
U14 23.4 52.5
C34 20.3 51.5 90
C37 26.5 51.5 90
C35 20.5 54.7
R26 26.2 54.1
R30 26.2 55.6
C36 28.1 54.8 90
R27 23.4 55.5
D1 22 58
R53 25.2 58
''')
module('U16_OCXO_3V3_LDO', '''
U16 12 62.5
C38 8.9 61.5 90
C41 15.1 61.5 90
C39 9.1 64.7
R32 14.8 64.1
R33 14.8 65.6
C40 16.7 64.8 90
R31 12 65.5
D2 10.5 68
R34 13.7 68
''')
module('U4_BOOST_5V2', '''
U4 33.5 61
L2 30.8 61 90
C72 36 58
C73 35.9 59.7
C74 31 64 180
C75 31 66.5 180
R51 36.2 62.5
R52 36.2 64
R49 38.7 58.6 90
R50 38.7 61 90
''')
module('U13_OUTPUT_DRIVER', '''
U13 47 63 -90
C46 49.5 59.8
C47 52.8 59.8
C48 47 66.5
C49 47 68.5
R42 43.5 61 90
R46 44.5 59.2
R20 43.5 65.3 -90
R47 50.5 65.3 -90
J1 34 71.94 -90
J4 58 71.94 -90
D6 34 67 -90
D9 58 67 -90
''')
module('MOUNTING', '''
H1 4 4
H2 71 4
H3 4 71
H4 71 71
''')
assert set(positions)==set(fps), (set(fps)-set(positions),set(positions)-set(fps))
positions.update({'R11':(8.3,38.5,90),'JP1':(44,23.2,0),
                  'C43':(14.4,48.4,0),'C19':(25.7,41,90),
                  'C17':(24,48.8,0),'FB7':(29.4,49.7,0),
                  'C8':(50.5,21.9,0),'R9':(51.7,23.5,0)})
for ref,(x,y,a) in positions.items():
 f=fps[ref]; f.SetOrientationDegrees(a)
 f.SetPosition(p.VECTOR2I(p.FromMM(X+x),p.FromMM(Y+y)))
 f.Reference().SetVisible(False); f.Value().SetVisible(False)
 # Keep hidden identifiers with their owners for the assembly-layer view.
 f.Reference().SetPosition(f.GetPosition())
 f.Value().SetPosition(f.GetPosition())
fps['U5'].SetPosition(fps['U7'].GetPosition()+delta)

# Explicit editor groups permit moving one complete functional circuit at a time.
for name,refs in groups.items():
 g=p.PCB_GROUP(b); g.SetName(name)
 for ref in refs: g.AddItem(fps[ref])
 b.Add(g)

p.SaveBoard(str(path),b)
Path('tmp/modular_groups.json').write_text(__import__('json').dumps(groups,indent=2),encoding='utf8')
print('Modules:',len(groups),'Footprints:',len(fps),'Backup:',backup)
