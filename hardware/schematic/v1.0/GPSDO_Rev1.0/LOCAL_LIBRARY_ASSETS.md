# 本地符号、封装与 3D 模型迁移

> 当前状态：已移除 POWER 页的 −5 V 产生电路，包括 U17、U13、L2、D9、R38～R42、C59～C67 及相关连线、网络标签和电源标志。
> EXT 页 U4/U12 仍为 BUF602，输出级的单电源替代方案尚未确定；保留待处理标注，不能按当前状态认定输出已可工作。
> 本地符号、封装和模型库保留，供以后复用。下文迁移统计与0402变更为此前操作记录。


符号库：`GPSDO_Rev1.0.kicad_sym`；封装库：`GPSDO_Rev1.0.pretty`；模型目录：`GPSDO_Rev1.0.3dshapes`。

所有运行时模型引用均使用 `${KIPRJMOD}/GPSDO_Rev1.0.3dshapes/文件名`。

## 迁移统计

- local_footprint_files: 51
- local_model_files: 65
- copied_models: 22
- package_symbol_variants: 8
- rebound_instances: 76

## 符号与多封装绑定

通用 R/C/L 按实际封装建立 `原符号__封装名称` 变体；保持位号、参数、引脚位置、封装焊盘及网络连接。

| 符号 | 默认本地封装 |
| --- | --- |
| BSMD1206C-1300T | GPSDO_Rev1.0:BSMD1206C-1300T |
| BUF602IDBVT | GPSDO_Rev1.0:BUF602IDBVT |
| C | GPSDO_Rev1.0:C_0603_1608Metric |
| CH340E | GPSDO_Rev1.0:CH340E |
| C__C_0402_1005Metric | GPSDO_Rev1.0:C_0402_1005Metric |
| C__C_0805_2012Metric | GPSDO_Rev1.0:C_0805_2012Metric |
| C__C_1210_3225Metric | GPSDO_Rev1.0:C_1210_3225Metric |
| Conn_01x04_Socket | GPSDO_Rev1.0:PinHeader_1x04_P2.54mm_Vertical |
| Conn_Coaxial | GPSDO_Rev1.0:SMA_Amphenol_132289_EdgeMount |
| D_Schottky | GPSDO_Rev1.0:D_SMA |
| FerriteBead | GPSDO_Rev1.0:L_0603_1608Metric |
| FerriteBead_Small | GPSDO_Rev1.0:L_0603_1608Metric |
| KH-IPEX-K501-29 | GPSDO_Rev1.0:KH-IPEX-K501-29 |
| L | GPSDO_Rev1.0:L_0603_1608Metric |
| LAIL-PHC2_54-2P-01-XH-L | GPSDO_Rev1.0:LAIL-PHC2_54-2P-01-XH-L |
| LED | GPSDO_Rev1.0:LED_0603_1608Metric |
| LMK1C1103PWR | GPSDO_Rev1.0:LMK1C1103PWR |
| L__L_0402_1005Metric | GPSDO_Rev1.0:L_0402_1005Metric |
| L__L_Coilcraft_LPS4018 | GPSDO_Rev1.0:L_Coilcraft_LPS4018 |
| MountingHole_Pad | GPSDO_Rev1.0:MountingHole_3.2mm_M3_Pad |
| NEO-M8T | GPSDO_Rev1.0:NEO-M8T-0 |
| NEO-M8T-0 | GPSDO_Rev1.0:NEO-M8T-0 |
| OCXO_20x20mm | GPSDO_Rev1.0:OCXO_20x20mm |
| OCXO_25.4x25.4mm | GPSDO_Rev1.0:DOPFITKR2-10M |
| OPA189IDR | GPSDO_Rev1.0:OPA189IDR |
| OPA388IDR | GPSDO_Rev1.0:OPA388IDR |
| R | GPSDO_Rev1.0:R_0603_1608Metric |
| REF5040 | GPSDO_Rev1.0:REF5040 |
| R__C_0603_1608Metric | GPSDO_Rev1.0:C_0603_1608Metric |
| R__R_0402_1005Metric | GPSDO_Rev1.0:R_0402_1005Metric |
| R__R_0805_2012Metric | GPSDO_Rev1.0:R_0805_2012Metric |
| SN74LVC1T45DBVR | GPSDO_Rev1.0:SN74LVC1T45DBVR |
| STM32G431CBU6 | GPSDO_Rev1.0:STM32G431CBU6 |
| STM32G431CBUx | GPSDO_Rev1.0:QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm |
| STM32G431KBUx | GPSDO_Rev1.0:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm |
| SolderJumper_2_Bridged | GPSDO_Rev1.0:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm |
| TAJB107M010RNJ | GPSDO_Rev1.0:TAJB107M010RNJ |
| TDC7200PWR | GPSDO_Rev1.0:TDC7200PWR |
| TMP117AIDRVR | GPSDO_Rev1.0:TMP117AIDRVR |
| TPD1E10B06DPYR | GPSDO_Rev1.0:TPD1E10B06DPYR |
| TPS63700 | GPSDO_Rev1.0:TPS63700 |
| TPS7A3001DGNR | GPSDO_Rev1.0:TPS7A3001DGNR |
| TPS7A5201RPSR | GPSDO_Rev1.0:TPS7A5201RPSR |
| TYPE-C_16PIN_2MD_073 | GPSDO_Rev1.0:TYPE-C_16PIN_2MD_073 |
| TestPoint | GPSDO_Rev1.0:TestPoint_Pad_D1.0mm |

## 原本不存在或缺失的模型

这些项目保留原有封装，不以不匹配模型代替：

- `L_Coilcraft_LPS4018`：原引用文件不存在：`${KICAD10_3DMODEL_DIR}/Inductor_SMD.3dshapes/L_Coilcraft_LPS4018.step`。
- `MountingHole_3.2mm_M3_Pad`：原封装没有绑定模型。
- `SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm`：原封装没有绑定模型。
- `TestPoint_Pad_D1.0mm`：原封装没有绑定模型。
- `OCXO_20x20mm`：原封装没有绑定模型。
- `TPS7A3001DGNR`：原封装没有绑定模型。

焊桥、焊盘测试点和安装孔为 PCB 几何，本身不要求实体模型。电源符号和 PWR_FLAG 不绑定实体封装。

## 模型来源

迁移文件保留原文件内容及其原始版权信息；下列路径仅作来源记录，不是运行时依赖。

- `SMA_Amphenol_132289_EdgeMount.step` ← `F:\KiCad\10.0\share\kicad\3dmodels\Connector_Coaxial.3dshapes\SMA_Amphenol_132289_EdgeMount.step`
- `C_0402_1005Metric.step` ← `F:\KiCad\10.0\share\kicad\3dmodels\Capacitor_SMD.3dshapes\C_0402_1005Metric.step`
- `C_0603_1608Metric.step` ← `F:\KiCad\10.0\share\kicad\3dmodels\Capacitor_SMD.3dshapes\C_0603_1608Metric.step`
- `R_0402_1005Metric.step` ← `F:\KiCad\10.0\share\kicad\3dmodels\Resistor_SMD.3dshapes\R_0402_1005Metric.step`
- `PinHeader_1x04_P2.54mm_Vertical.step` ← `F:\KiCad\10.0\share\kicad\3dmodels\Connector_PinHeader_2.54mm.3dshapes\PinHeader_1x04_P2.54mm_Vertical.step`
- `R_0603_1608Metric.step` ← `F:\KiCad\10.0\share\kicad\3dmodels\Resistor_SMD.3dshapes\R_0603_1608Metric.step`
- `R_0805_2012Metric.step` ← `F:\KiCad\10.0\share\kicad\3dmodels\Resistor_SMD.3dshapes\R_0805_2012Metric.step`
- `REF5040.wrl` ← `F:\KiCad\Libs\footprints\JLCImport.3dshapes\REF5040.wrl`
- `REF5040.step` ← `F:\KiCad\Libs\footprints\JLCImport.3dshapes\REF5040.step`
- `TAJB107M010RNJ.wrl` ← `F:\KiCad\Libs\footprints\JLCImport.3dshapes\TAJB107M010RNJ.wrl`
- `TAJB107M010RNJ.step` ← `F:\KiCad\Libs\footprints\JLCImport.3dshapes\TAJB107M010RNJ.step`
- `D_SMA.step` ← `F:\KiCad\10.0\share\kicad\3dmodels\Diode_SMD.3dshapes\D_SMA.step`
- `BSMD1206C-1300T.wrl` ← `F:\KiCad\Libs\footprints\JLCImport.3dshapes\BSMD1206C-1300T.wrl`
- `BSMD1206C-1300T.step` ← `F:\KiCad\Libs\footprints\JLCImport.3dshapes\BSMD1206C-1300T.step`
- `C_0805_2012Metric.step` ← `F:\KiCad\10.0\share\kicad\3dmodels\Capacitor_SMD.3dshapes\C_0805_2012Metric.step`
- `C_1210_3225Metric.step` ← `F:\KiCad\10.0\share\kicad\3dmodels\Capacitor_SMD.3dshapes\C_1210_3225Metric.step`
- `QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm.step` ← `C:\Users\26079\.codex\visualizations\2026\10\16\01a14296-26af-73e2-8cc2-9f45f690e12f\model-downloads\QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm.step`
- `C_0201_0603Metric.step` ← `F:\KiCad\10.0\share\kicad\3dmodels\Capacitor_SMD.3dshapes\C_0201_0603Metric.step`
- `C_1206_3216Metric.step` ← `F:\KiCad\10.0\share\kicad\3dmodels\Capacitor_SMD.3dshapes\C_1206_3216Metric.step`
- `R_0201_0603Metric.step` ← `F:\KiCad\10.0\share\kicad\3dmodels\Resistor_SMD.3dshapes\R_0201_0603Metric.step`
- `R_1206_3216Metric.step` ← `F:\KiCad\10.0\share\kicad\3dmodels\Resistor_SMD.3dshapes\R_1206_3216Metric.step`
- `R_1210_3225Metric.step` ← `F:\KiCad\10.0\share\kicad\3dmodels\Resistor_SMD.3dshapes\R_1210_3225Metric.step`

补回的 QFN-48 STEP 来自 [KiCad 官方 6.0.11 模型库](https://gitlab.com/kicad/libraries/kicad-packages3D/-/blob/6.0.11/Package_DFN_QFN.3dshapes/QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm.step)。

PCB 文件当前为空，没有可更新的已放置封装。

## 验证结果

- 282 个已放置符号已检查；152 个实体元件的实例封装、库符号默认封装与缓存符号封装完全一致。
- 45 项 3D 绑定全部指向项目内实际存在的文件，无绝对运行时模型路径。
- 迁移前后网络连接完全一致；原有封装焊盘和图形几何保持一致。
- ERC 保持原有 85 项，无新增问题。

## −5V 电源电阻、电容改用 0402

- R38、R39、R40、R41、R42：绑定 `R__R_0402_1005Metric` → `GPSDO_Rev1.0:R_0402_1005Metric`。
- C60、C61、C63、C66、C67：绑定 `C__C_0402_1005Metric` → `GPSDO_Rev1.0:C_0402_1005Metric`。
- R39～R42：0.1% 精度，温漂不高于 25 ppm/℃。
- C61：4.7nF，C0G/NP0，16V，±5%；C60、C63、C66、C67：X7R，16V。
- C59、C64、C65 继续使用 0805；C62 继续使用 1210。
- 使用现有项目 0402 封装及已绑定的本地 3D 模型。
