from pathlib import Path
import math
exec(Path(r'C:/Users/26079/.codex/visualizations/2026/10/16/01a14296-26af-73e2-8cc2-9f45f690e12f/wire_negative_supply.py').read_text(encoding='utf-8').split('text=FILE.read_text')[0])
for fn in ['POWER','EXT','MCU']:
 r,_=parse((BASE/(fn+'.kicad_sch')).read_text(encoding='utf-8'));libs={n[1]:n for n in children(sub(r,'lib_symbols'),'symbol')}
 print('\nSHEET',fn)
 for n in children(r,'symbol'):
  p={v[1]:v[2] for v in children(n,'property')};ref=p['Reference'];x,y,a=map(float,sub(n,'at')[1:]);
  if fn=='POWER': print(ref,p['Value'],x,y)
  if ref in ['U4','U13','U15']:
   print('TARGET',ref,p['Value'],x,y,a)
   for u in children(libs[sub(n,'lib_id')[1]],'symbol'):
    for pin in children(u,'pin'):
     px,py=map(float,sub(pin,'at')[1:3]);ar=math.radians(a);pos=(round(x+px*math.cos(ar)+py*math.sin(ar),5),round(y+px*math.sin(ar)-py*math.cos(ar),5));nc=any(tuple(map(float,sub(z,'at')[1:3]))==pos for z in children(r,'no_connect'));print(sub(pin,'number')[1],sub(pin,'name')[1],pos,'NC' if nc else '')
 if fn=='EXT':
  for n in children(r,'symbol'):
   p={v[1]:v[2] for v in children(n,'property')};print(p['Reference'],p['Value'],sub(n,'at')[1:])
lib,_=parse((BASE/'GPSDO_Rev1.0.kicad_sym').read_text(encoding='utf-8'))
print('LOCAL PASSIVES',[(n[1], {p[1]:p[2] for p in children(n,'property')}.get('Footprint')) for n in children(lib,'symbol') if n[1].startswith(('R','C','L','+','GND','PWR'))])
