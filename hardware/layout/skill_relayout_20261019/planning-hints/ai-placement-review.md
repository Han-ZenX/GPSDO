# AI placement review checklist

Use this after generating `board.pln` to confirm the design intent captures the
hints from `pcb-plan inspect`. Hints are candidates; this checklist drives the
review/optimization loop, not automated placement.

## Confirm

- [ ] Board geometry matches Edge.Cuts / mechanical drawing
- [ ] Every edge connector has a confirmed access_side, rotation, and edge_required
- [ ] Mounting holes are at intended corners/locations
- [ ] Each high-speed path has a corridor and flow-through protection ordering
- [ ] Power islands reflect electrical topology, not type piles
- [ ] Every ref has exactly one placement owner (groups are metadata only)
- [ ] Routing classes / SI constraints set for high-speed and differential nets
- [ ] Stackup assumptions confirmed with the fabricator for controlled impedance
- [ ] Simulation triggers (OpenEMS / ngspice / SI) reviewed

## Candidate items requiring a decision

- edge connector J1: access bottom, edge_required hint True
- edge connector J3: access right, edge_required hint True
- edge connector J4: access bottom, edge_required hint True

## KiCad groups (metadata only; must not drive placement)

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

