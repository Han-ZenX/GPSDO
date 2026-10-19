# Generate board.pln from planning hints

You are generating `board.pln`, the **authoritative design-intent document** for
a PCB. The files in this `planning-hints/` directory are *facts and candidate
hints* extracted by `pcb-plan inspect` — they are not authoritative and contain
no placement ownership or final floorplan. Your job is to reason about them and
produce intentional `board.pln` design decisions.

## What board.pln must contain

- mechanical constraints (mounting holes, board outline/keepouts)
- edge-required components, connector orientation, and access sides
- placement regions
- power islands (electrical topology, not type piles)
- high-speed corridors and functional paths (signal-flow topology)
- ownership (exactly one owner per ref; groups are metadata only)
- routing classes and SI constraints
- stackup assumptions and simulation triggers

## Board summary

- size: 75.0 x 75.0 mm (source: cli)
- components: 157, nets: 150
- differential pairs: 1, high-speed nets: 67

## Component counts by candidate role

- capacitor: 44
- connector: 2
- debug_header: 1
- decoupling_cap: 11
- ferrite: 8
- ic: 15
- inductor: 2
- led: 6
- mcu: 1
- mounting_hole: 4
- pullup: 18
- series: 35
- testpoint: 2
- unknown: 8

## High-speed interfaces / candidate paths

- none detected; confirm there are no high-speed interfaces

## Candidate power islands

- none detected

## Mechanical constraints

- H1: top_left
- H2: top_right
- H3: bottom_left
- H4: bottom_right

## Edge connectors to confirm

- J1: access bottom, rotation(auto) 180.0 deg, edge_required hint True
- J3: access right, rotation(auto) 90.0 deg, edge_required hint True
- J4: access bottom, rotation(auto) 180.0 deg, edge_required hint True

## Stackup assumptions

- candidate: 4-layer (4_layer_signal_gnd_pwr_signal)
- Stackup template applied: layer roles/reference planes are placement/routing intent only. Controlled impedance requires the actual fabricator stackup; do not trust template thickness/er values for impedance.

## Placement risks and simulation triggers

- openems_candidate: True
- ngspice_candidate: False
- si_candidate: True
- Heuristic hints cannot verify impedance, return paths, plane splits, thermal, or EMI.
- KiCad groups in imported_kicad_groups are metadata only; do not use them for placement.

## Output

Write a complete `board.pln` (YAML). Resolve every hint into an explicit
decision or drop it with a rationale. Prefer encoding intent in `board.pln`
over later `placement.ppl` overrides. Validate with `pcb-plan check`.

