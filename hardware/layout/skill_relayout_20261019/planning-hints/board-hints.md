# Board hints

Facts and **candidate hints** extracted by `pcb-plan inspect`. These are not
authoritative: an AI or human turns them into `board.pln`. Hints never assign
placement ownership or a final floorplan.

## Board geometry

- size: 75.0 x 75.0 mm
- origin: (106.415, 63.44)
- source: cli (Edge.Cuts available: False)

## Counts

- components: 157
- nets: 150
- differential_pairs: 1
- high_speed_nets: 67
- power_nets: 3
- ground_nets: 1

## Candidate roles

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

## Candidate high-speed paths

- none

## Candidate power islands

- none

## Candidate edge connectors

- J1: access bottom, edge_required hint True
- J3: access right, edge_required hint True
- J4: access bottom, edge_required hint True

## Imported KiCad groups (metadata only)

KiCad groups are preserved for information only and must not drive placement.

- 'U10_PWM_LEVEL': C22, C24, R35, U10
- 'U3_TEMPERATURE': C16, R12, R15, R16, U3
- 'U9_TUNING_FILTER': C17, C18, C19, C20, C21, FB7, R17, R18, R19, U9
- 'OCXO_OPTIONS': C1, C2, C23, FB4, FB5, R22, R23, R5, TP1, TP2, U5, U7
- 'U11_USB_UART': C27, C28, FB6, R11, R14, U11, USB1
- 'OCXO_RF_MONITOR': C5, R13, RF2
- 'U6_GNSS': C6, C7, C8, FB8, L1, R1, R2, R3, R8, R9, RF1, U6
- 'U18_POWER_MUX': C25, C43, C68, C69, C70, C71, CN1, D8, F1, R43, R44, R45, U18
- 'U1_TDC7200': C10, C12, C9, FB2, JP1, R10, U1
- 'U13_OUTPUT_DRIVER': C46, C47, C48, C49, D6, D9, J1, J4, R20, R42, R46, R47, U13
- 'U8_VOLTAGE_REFERENCE': C11, C56, C57, C58, R28, R29, U8
- 'MOUNTING': H1, H2, H3, H4
- 'U16_OCXO_3V3_LDO': C38, C39, C40, C41, D2, R31, R32, R33, R34, U16
- 'U4_BOOST_5V2': C72, C73, C74, C75, L2, R49, R50, R51, R52, U4
- 'U14_MAIN_3V3_LDO': C34, C35, C36, C37, D1, R26, R27, R30, R53, U14
- 'U2_CLOCK_BUFFER': C3, C4, FB3, R36, R37, R4, R6, R7, U2
- 'U15_MCU': C13, C14, C15, C26, C32, C33, C42, FB1, J3, R38, R39, R40, R41, R48, U15
- 'MCU_STATUS_LEDS': D3, D4, D5, R21, R24, R25

## Warnings

- no semantic aliases found in netlist; tried json: Expecting value: line 1 column 1 (char 0)
