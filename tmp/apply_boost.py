from pathlib import Path
import copy,zipfile,datetime,shutil,math
src=Path(r'C:/Users/26079/.codex/visualizations/2026/10/16/01a14296-26af-73e2-8cc2-9f45f690e12f/wire_negative_supply.py').read_text(encoding='utf-8')
exec(src.split('text=FILE.read_text')[0])
backup=BASE/'.history'/('before_boost_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.zip')
with zipfile.ZipFile(backup,'w',zipfile.ZIP_DEFLATED) as z:
 for f in list(BASE.glob('*.kicad_sch'))+[BASE/'GPSDO_Rev1.0.kicad_sym']:z.write(f,f.name)
refs=set()
for f in BASE.glob('*.kicad_sch'): refs.update(re.findall(r'\(property "Reference" "([^"]+)"',f.read_text(encoding='utf-8')))
def nextref(pre):
 nums=[int(r[len(pre):]) for r in refs if r.startswith(pre) and r[len(pre):].isdigit()];r=pre+str(max(nums+[0])+1);refs.add(r);return r
def props(n):return {p[1]:p for p in children(n,'property')}
canfile=BASE/'GPSDO_Rev1.0.kicad_sym';ct=canfile.read_text(encoding='utf-8');can,cs=parse(ct);defs={n[1]:n for n in children(can,'symbol')}
# Local footprint and real local STEP model for 2.0x1.6mm power inductor.
fp='L_Murata_DFE201610P'
ft=Path('F:/KiCad/10.0/share/kicad/footprints/Inductor_SMD.pretty/'+fp+'.kicad_mod').read_text(encoding='utf-8').replace('${KICAD10_3DMODEL_DIR}/Inductor_SMD.3dshapes/','${KIPRJMOD}/GPSDO_Rev1.0.3dshapes/')
(BASE/'GPSDO_Rev1.0.pretty'/f'{fp}.kicad_mod').write_text(ft,encoding='utf-8')
shutil.copy2(Path('F:/KiCad/10.0/share/kicad/3dmodels/Inductor_SMD.3dshapes')/(fp+'.step'),BASE/'GPSDO_Rev1.0.3dshapes'/(fp+'.step'))
lname='L__L_Murata_DFE201610P';ld=copy.deepcopy(defs['L']);ld[1]=lname
for u in children(ld,'symbol'):u[1]=u[1].replace('L_',lname+'_',1)
props(ld)['Footprint'][2]='GPSDO_Rev1.0:'+fp
props(ld)['Description'][2]='DFE201610P-1R0M=P2; 1uH; 2.0x1.6x1.0mm shielded; 3.1A inductance-decrease rating, 2.2A thermal rating. 200mA boost design, validate startup.'
defs[lname]=ld
# Correct imported all-passive converter pin electrical types.
tps=defs['TPS61023DRLR']
for u in children(tps,'symbol'):
 for p in children(u,'pin'):p[1]=A({'1':'input','2':'input','3':'power_in','4':'power_in','5':'passive','6':'power_out'}[sub(p,'number')[1]])
a,b=cs[id(tps)];ct=ct[:a]+dump(tps,1)+ct[b:];ix=ct.rfind(')');ct=ct[:ix]+'\n'+dump(ld,1)+'\n'+ct[ix:];canfile.write_text(ct,encoding='utf-8',newline='\r\n')
# Reuse diagram primitives, while choosing all symbols from project library.
def setup(fn):
 global FILE,text,root,spans,lib,added,added_libs,edits,path,byref,manifest
 FILE=BASE/(fn+'.kicad_sch');text=FILE.read_text(encoding='utf-8');root,spans=parse(text);lib=sub(root,'lib_symbols');added=[];added_libs=[];edits=[];manifest={};symbols=children(root,'symbol');byref={props(n)['Reference'][2]:n for n in symbols};path=sub(sub(sub(symbols[0],'instances'),'project'),'path')[1]
exec(src[src.index('def effect('):src.index('# Existing ICs retained')])
def ensure_lib(name,source=None):
 if any(n[1]==name for n in children(lib,'symbol')+added_libs):return
 n=copy.deepcopy(defs[name.split(':')[1]]);n[1]=name;added_libs.append(n)
def power(name,x,y,angle=0):
 lid='GPSDO_Rev1.0:'+name;ensure_lib(lid);r=nextref('#PWR');n=inst(lid,r,name,x,y,angle);sub(n,'in_bom')[1]=A('no');ps=props(n);ps['Reference'].append(node('hide',A('yes')));ps['Value'][3]=node('at',atom(x),atom(y+3 if name=='GND' else y-3),A('0'));ps['Value'][-1]=effect(.9);return r
def glabel(name,x,y,shape='input',ang=0):
 added.append(node('global_label',name,node('shape',A(shape)),node('at',atom(x),atom(y),atom(ang)),effect(.9,'left' if ang==0 else 'right'),node('uuid',uid()),prop('Intersheetrefs','${INTERSHEET_REFS}',x,y,False)))
def part(short,ref,val,x,y,ang=0,desc=''):
 lid='GPSDO_Rev1.0:'+short;ensure_lib(lid);n=inst(lid,ref,val,x,y,ang,props(defs[short])['Footprint'][2],desc)
 if ang==90:
  for k in ['Reference','Value']:sub(props(n)[k],'at')[3]=A('90')
 return n
def save():
 if added_libs:
  end=spans[id(lib)][1];edits.append((end-1,end-1,'\n'+''.join('\t\t'+dump(n,2)+'\n' for n in added_libs)))
 ix=text.rfind(')');edits.append((ix,ix,'\n'+''.join('\t'+dump(n,1)+'\n' for n in added)))
 t=text
 for a,b,s in sorted(edits,reverse=True):t=t[:a]+s+t[b:]
 parse(t);FILE.write_text(t,encoding='utf-8',newline='\r\n')
setup('POWER')
assert sub(byref['U4'],'at')[1:3]==[A('224.79'),A('133.35')]
old=next(n for n in children(lib,'symbol') if n[1]=='GPSDO_Rev1.0:TPS61023DRLR');q=copy.deepcopy(tps);q[1]=old[1];edits.append((*spans[id(old)],dump(q,2)))
# input bypass and shared input rail
for x,val,short in [(177.8,'10uF / 10V','C'),(193.04,'100nF','C__C_0402_1005Metric')]:
 ref=nextref('C');part(short,ref,val,x,156.21,desc='X5R/X7R; 10uF effective >=4.7uF at 3.3V; verify selected MPN DC bias' if short=='C' else 'X7R 16V');wire((x,151.13),(x,152.4));gnd(x,160.02)
wire((177.8,151.13),(193.04,151.13),(212.09,151.13),(212.09,135.89),(214.63,135.89));junction(193.04,151.13);power('+3.3V',177.8,151.13)
# inductor above U4, net label avoids crossed chip pins
lref=nextref('L');part(lname,lref,'1uH / DFE201610P',222.25,115.57,90,props(ld)['Description'][2]);wire((218.44,115.57),(213.36,115.57));power('+3.3V',213.36,115.57);wire((226.06,115.57),(234.95,115.57));label('BOOST_SW',234.95,115.57)
wire((234.95,133.35),(238.76,133.35));label('BOOST_SW',238.76,133.35)
wire((234.95,135.89),(241.3,135.89),(241.3,147.32));gnd(241.3,147.32)
# MCU EN, default off
rs=nextref('R');part('R__R_0402_1005Metric',rs,'1K',196.85,133.35,90)
wire((177.8,125.73),(190.5,125.73),(190.5,133.35),(193.04,133.35));glabel('BOOST_EN',177.8,125.73,'input',180)
wire((200.66,133.35),(207.01,133.35),(214.63,133.35));junction(207.01,133.35)
rpd=nextref('R');part('R__R_0402_1005Metric',rpd,'10K',207.01,143.51);wire((207.01,133.35),(207.01,139.7));wire((207.01,147.32),(207.01,149.86));gnd(207.01,149.86)
# output rail and capacitors
wire((234.95,130.81),(255.27,130.81),(274.32,130.81),(285.75,130.81));glabel('+5V2_DRV',285.75,130.81,'output')
for x in [255.27,274.32]:
 ref=nextref('C');part('C__C_0805_2012Metric',ref,'22uF / 10V',x,140.97,desc='X5R/X7R; both output capacitors effective total >=10uF at 5.2V; verify DC bias curve');wire((x,130.81),(x,137.16));gnd(x,144.78);junction(x,130.81)
# feedback separate leg with same net labels
rt=nextref('R');rb=nextref('R');part('R__R_0402_1005Metric',rt,'77.4K 0.1%',227.33,156.21);part('R__R_0402_1005Metric',rb,'10K 0.1%',227.33,171.45)
wire((227.33,152.4),(227.33,149.86));label('+5V2_DRV',227.33,149.86)
wire((227.33,160.02),(227.33,163.83),(227.33,167.64));label('BOOST_FB',227.33,163.83);junction(227.33,163.83);gnd(227.33,175.26)
wire((214.63,130.81),(209.55,130.81));label('BOOST_FB',209.55,130.81,180)
note('3.3V -> 5.2V / ISL55110 VH',175.26,108,1.25)
note('0.595 x (1 + 77.4K/10K) = 5.200V',246.38,156.21,.95)
note('Target 200mA; check ripple / startup',246.38,160.02,.9)
note('EN: PB0; LOW during MCU reset',246.38,163.83,.9)
note('Input 0603; output 0805; R / 100nF 0402',175.26,184.15,.85)
save()
# Replace the VH +5V symbol with the independent global boost rail; preserve all local decoupling.
setup('EXT');old=byref['#PWR058'];x,y=map(float,sub(old,'at')[1:3]);edits.append((*spans[id(old)],''));glabel('+5V2_DRV',x,y,'input');save()
# Route spare MCU PB0 (17) to EN via global net; no change to unrelated user edits.
setup('MCU');pos=(104.14,114.3);ncold=next(n for n in children(root,'no_connect') if tuple(map(float,sub(n,'at')[1:3]))==pos);edits.append((*spans[id(ncold)],''));wire(pos,(114.3,114.3));glabel('BOOST_EN',114.3,114.3,'output');save()
print('BACKUP',backup);print('ADDED',lref,rs,rpd,rt,rb)
