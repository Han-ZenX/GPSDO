from pathlib import Path
exec(Path(r'C:/Users/26079/.codex/visualizations/2026/10/16/01a14296-26af-73e2-8cc2-9f45f690e12f/wire_negative_supply.py').read_text(encoding='utf-8').split('text=FILE.read_text')[0])
f=BASE/'POWER.kicad_sch';t=f.read_text(encoding='utf-8');r,s=parse(t);ed=[]
def props(n):return {p[1]:p for p in children(n,'property')}
# Move feedback leg out of sheet title block, preserving all exact junctions.
for n in r[1:]:
 if not isinstance(n,list):continue
 q=None
 if n[0]=='symbol':
  ps=props(n);ref=ps.get('Reference',[None,None,''])[2]
  if ref in ['R51','R52'] or (ps.get('Value',[None,None,''])[2]=='GND' and sub(n,'at')[1:3]==[A('227.33'),A('175.26')]):
   q=__import__('copy').deepcopy(n)
   for a in [sub(q,'at')]+[sub(p,'at') for p in children(q,'property')]:a[1]=atom(float(a[1])-60.96);a[2]=atom(float(a[2])-17.78)
  if ref in ['R49','R50','R51','R52','C72','C73','C74','C75','L2']:
   if q is None:q=__import__('copy').deepcopy(n)
   for p in children(q,'property'):
    if p[1] in ['Reference','Value']:sub(sub(p,'effects'),'font')[1]=node('size',A('0.85'),A('0.85'))
  if ps.get('Value',[None,None,''])[2]=='GND' and sub(n,'at')[1:3]==[A('207.01'),A('149.86')]:
   q=__import__('copy').deepcopy(n)
   for a in [sub(q,'at')]+[sub(p,'at') for p in children(q,'property')]:a[2]=atom(float(a[2])-2.54)
 elif n[0]=='wire':
  pts=children(sub(n,'pts'),'xy');coords=[tuple(map(float,p[1:])) for p in pts]
  if all(x==227.33 and y>=149.86 for x,y in coords):
   q=__import__('copy').deepcopy(n)
   for p in children(sub(q,'pts'),'xy'):p[1]=atom(float(p[1])-60.96);p[2]=atom(float(p[2])-17.78)
  if coords==[(274.32,130.81),(285.75,130.81)]:ed.append((*s[id(n)],''));continue
  if coords==[(207.01,147.32),(207.01,149.86)]:ed.append((*s[id(n)],''));continue
 elif n[0] in ['label','junction']:
  a=sub(n,'at')
  if a[1]==A('227.33') and float(a[2])>=149.86:
   q=__import__('copy').deepcopy(n);sub(q,'at')[1]=atom(float(a[1])-60.96);sub(q,'at')[2]=atom(float(a[2])-17.78)
   if n[0]=='label' and n[1]=='+5V2_DRV':
    q[0]=A('global_label');q.append(node('shape',A('input')))
 elif n[0]=='global_label' and n[1]=='+5V2_DRV':
  q=__import__('copy').deepcopy(n);sub(q,'at')[1:3]=[A('255.27'),A('123.19')]
 elif n[0]=='text' and n[1].startswith('Input 0603;'):ed.append((*s[id(n)],''));continue
 if q is not None:ed.append((*s[id(n)],dump(q,1)))
w=node('wire',node('pts',node('xy',A('255.27'),A('130.81')),node('xy',A('255.27'),A('123.19'))),node('stroke',node('width',A('0')),node('type',A('default'))),node('uuid',uid()))
ix=t.rfind(')');ed.append((ix,ix,dump(w,1)+'\n'))
for a,b,v in sorted(ed,reverse=True):t=t[:a]+v+t[b:]
f.write_text(t,encoding='utf-8',newline='\r\n')
