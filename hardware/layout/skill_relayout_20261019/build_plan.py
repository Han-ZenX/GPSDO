from pathlib import Path
import json
here=Path(__file__).resolve().parent
h=json.loads((here/'planning-hints/board-hints.json').read_text())
audit=json.loads((here/'recipe_audit.json').read_text())
roles=dict(h['inferred_roles'])
roles.update({r:'power_regulator' for r in ['U4','U14','U16']})
roles.update({'U18':'power_mux','U6':'rf_module','U7':'oscillator','U5':'oscillator',
 'U1':'ic','U15':'mcu','USB1':'usb_connector','CN1':'power_connector','RF1':'rf_connector','RF2':'rf_connector'})
components={r:{'role':v} for r,v in roles.items()}
for ref,side,rot in [('USB1','left',270),('CN1','left',270),('J1','bottom',270),('J4','bottom',270)]:
 components[ref].update(edge_required=True,access_side=side,rotation=rot,allow_body_outside_board=True,locked=True)
components['J3'].update(edge_required=False,rotation='keep',locked=True)
for ref in ['U5','U7','RF1','RF2']: components[ref].update(rotation='keep',locked=True,edge_required=False)
clusters=[]
for owner in sorted(set(r['owner'] for r in audit['after'])):
 clusters.append(dict(name=owner+'_SUPPORT',anchor=owner,members=[r['ref'] for r in audit['after'] if r['owner']==owner],role='pin_derived_support'))
plan={
 'board':dict(width=75,height=75,origin_x=106.415,origin_y=63.44,units='mm'),
 'fixed':{r:dict(type='corner',corner=c,inset=4) for r,c in zip(['H1','H2','H3','H4'],['top_left','top_right','bottom_left','bottom_right'])},
 'mechanical':{'mounting_holes':{r:dict(corner=c,inset=4) for r,c in zip(['H1','H2','H3','H4'],['top_left','top_right','bottom_left','bottom_right'])}},
 'components':components,'roles':roles,'clusters':clusters,
 'regions':{r:dict(x=v[0],y=v[1],w=v[2]-v[0],h=v[3]-v[1]) for r,v in audit['regions'].items()},
 'keepouts':[],
 'spacing':dict(default=.23,passive_to_passive=.23,passive_to_ic=.23,ic_to_ic=.75,connector_to_component=.5,mechanical_to_component=.5),
 'power_islands':{
  'BOOST_5V2':dict(regulator='U4',input_caps=['C72','C73'],inductor='L2',output_caps=['C74','C75'],feedback=['R51','R52'],switch_node='Net-(U4-SW)'),
  'MAIN_3V3':dict(regulator='U14',input_caps=['C34'],output_caps=['C37'],feedback=['R26','R30']),
  'OCXO_3V3_OPTION':dict(regulator='U16',input_caps=['C38'],output_caps=['C41'],feedback=['R32','R33'])},
 'functional_paths':{
  'USB':dict(type='high_speed_diff',sequence=['USB1','U11'],corridor_width_mm=2,protect_first=False),
  'GNSS_RF':dict(type='rf',sequence=['RF1','U6'],corridor_width_mm=2,protect_first=False),
  'CLOCK_OUTPUT':dict(type='clock',sequence=['U7','U2','U13','J1'],corridor_width_mm=2,protect_first=False)},
 'high_speed':dict(nets=['/MCU/USB_D+','/MCU/USB_D-','/MCU/10MHZ_TDC','/GNSS/PULSE_GNSS','Net-(RF1-SIG)'],interfaces=['USB','GNSS_RF','TDC_CLOCK']),
 'routing':dict(mode='all_nets_constrained'),
 'stackup':dict(layers=[dict(name='F.Cu',type='signal'),dict(name='In1.Cu',type='plane',net='GND'),dict(name='In2.Cu',type='power'),dict(name='B.Cu',type='signal')]),
 'differential_pairs':{'USB':dict(p='/MCU/USB_D+',n='/MCU/USB_D-',impedance_ohms=90)},
 'simulation':dict(openems=dict(enabled=False),ngspice=dict(enabled=False)),
 'provenance':dict(generator='Codex + kicad-pcb-placement pin solver + pcb-plan inspect',
  assumptions=[
   'Placement only. No routing, vias, copper zones or schematic edits.',
   'All components on front. Hidden reference/value fields are retained.',
   'U5 and U7 remain at their original relative offset and are mutually exclusive assembly options; their body overlap is intentional.',
   'RF2, C5 and R13 remain above OCXO as requested.',
   'Edge connector rotations come from measured footprint geometry, not the generic auto-rotation hint.',
   'J3 is an accessible vertical header; it does not require an outward-facing edge mating plane.',
   'NEO-M8T uses an external antenna. L1 is a parallel antenna-bias branch, not a series element in the RF signal path.',
   'No fabricated dielectric stackup supplied; no trace impedance or timing matching is verified.',
   'All 157 candidate roles were reviewed. Role overrides and exact pin-owned recipes replace ambiguous global-rail inference.',
   'The 67 high-speed-name hints include UART and unused pins; only real USB, GNSS RF and clock/TDC paths are promoted to interface intent.',
   'Simulation candidates were reviewed and deferred: this request changes component placement only.',
   'Imported KiCad groups are metadata, not ownership input. Ownership is specified from pin/net connectivity in relayout.py.',
   'Sources: TI TPS61023 sec10.1, TPS7A52 sec10.1, TDC7200 sec10-11, Renesas ISL55110 Bypassing.',
   'Re-running relayout.py replaces unlocked candidate poses; the live PCB is not written by that script.'])
}
(here/'board.pln').write_text(json.dumps(plan,indent=2),encoding='utf8')
