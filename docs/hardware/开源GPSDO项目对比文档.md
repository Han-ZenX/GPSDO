# 开源 GPSDO 项目对比文档

> **数据来源与可信度声明。** 本文所有项目信息来自各项目的仓库、作者在 time-nuts 邮件列表与 EEVblog 论坛的公开陈述，逐条来源列在第 9 节。**不同项目的性能数据性质差别很大**：有的是第三方实测、有的是作者自述、有的只是设计目标，本文在每个条目上标注了数据性质，请按此判断可信度。各项目的 star 数与状态为查询时的快照。第 3 节的 ADEV 曲线是**典型量级示意，不是任何具体项目的实测曲线**。

---

## 1. 结论摘要

| 问题 | 回答 |
| --- | --- |
| 开源 GPSDO 一共有多少 | 真正完整的硬件加固件开源**设计**约十个，另有二十余个 GitHub 仓库是周边工具（协议解析、分配放大器、监控软件） |
| **最值得参考的一个** | **Carsten Andrich 的 STM32G4 + ZED-F9T + TDC7200 方案**。它和本项目**用同一系列的 MCU**，架构是目前公开方案里最先进的，设计思路可以直接借鉴 |
| **社区最成熟、资料最多** | **Lars Walenius GPSDO**。2011 年至今的事实基准，EEVblog 主帖阅读量三十余万，有大量第三方复现与实测数据 |
| **最容易上手、成本最低** | **AndrewBCN/STM32-GPSDO**，不到 30 欧元，GPL-3.0，106 star，开源 GPSDO 里 star 最高 |
| **时间分辨率最高** | 用 TI **TDC7200** 的那一类，**55 到 60 ps**，比 Lars 的 1 ns 方案高约 20 倍，比本项目当前的定时器捕获方案高约 100 倍 |
| **精度最高（有实测依据）** | Lars 方案与铷钟 GPSDO 对比测试中，在 tau = 1000 s 处约 **2e-12**。这是本次调研中找到的**有公开实测支撑**的最好数字 |
| 一个重要的认识 | **时间分辨率高不直接等于输出精度高。** 分辨率只决定短 tau 段，输出 ADEV 由 OCXO、环路、GNSS 共同决定，见第 3 节 |

### 1.1 本项目的定位

本项目 v1.0 当前是 **STM32G431 加 SKG123N 加 PWM 控压 OCXO**。硬件上 OCXO 的 10 MHz 进 PA0、1PPS 进 PA1，**要测 OCXO 就必须拿 10 MHz 当计数时基，因此单次分辨率是 100 ns**，靠相位连续累积换取等效分辨率。只有改板把 10 MHz 同时送进 OSC_IN，让 MCU 以 OCXO 为系统时钟，才能拿到 1/170 MHz = 5.9 ns。

对照下来，**本项目的架构与 AndrewBCN/STM32-GPSDO 同级**（都是 MCU 定时器捕获加 Arduino 级固件复杂度），而**与 Carsten Andrich 的方案差了一个 TDC7200 加一套锯齿波修正**。这两处正是最值得补的短板。

---

## 2. 项目全景

### 2.1 第一梯队：TDC 架构（分辨率最高）

| 项目 | 架构 | 分辨率 | 数据性质 | 要点 |
| --- | --- | --- | --- | --- |
| **Carsten Andrich 方案** | STM32G4 + u-blox ZED-F9T + TDC7200 + 低 g 敏感 OCXO | TDC7200 约 50 ps | **设计目标**，未见完整实测 | 目标是在 10 km 半径内移动时相对精度优于 10 ns；避免对 OCXO 输出做数字分频；用低抖动时钟 IC；**在调谐 DAC 之后加 1 Hz 有源低通，以获得优于 16 bit 的等效调谐分辨率**；成本目标单台 500 欧元以内（不含 OCXO）。原理图 PDF 公开，是否完整开源未确认 |
| **thinkfat (Matthias Welwarsky) 方案** | STM32 + TDC7200 | 单次 55 ps，长观测区间约 60 ps（TDC7200 极限） | **作者自述加论坛实测** | 受 Lars 方案启发但走了更精密的路线，用专用 TDC 取代 4046 加 ADC。EEVblog 长帖有完整开发记录，是否发布完整设计文件未确认 |
| **TAPR TICC**（John Ackermann N8UR） | Arduino Mega 2560 + 双路 TDC7200 | 单次小于 60 ps，抖动小于 100 ps | **产品化指标** | **严格说这不是 GPSDO 而是时间间隔计数器**，但它是构建与评测高精度 GPSDO 的关键工具：双通道，约 100 次每秒，无需校准，与 TimeLab 实时兼容，需外部 10 MHz 参考。**BSD 许可，完整开源**，TAPR 有成品卖 |

### 2.2 第二梯队：经典 1 ns 级模拟 TIC（最成熟）

| 项目 | 架构 | 分辨率 | 数据性质 | 要点 |
| --- | --- | --- | --- | --- |
| **Lars Walenius GPSDO** | Arduino + HC390 + HC4046 + 一个二极管加无源件 | **约 1 ns**，量程 1 us | **实测，有第三方复现** | 2011 年的设计，**只用两片 HCMOS 逻辑加一个二极管**就做到 1 ns：HC390 给 HC4046 送 1 MHz，相位比较器输出经二极管和 RC 网络直接进 Arduino 的 10 bit ADC。实测 ADEV：配 M12 接收机的 position hold 模式，1 s 处 2e-8，1000 s 处 2e-11；**与 LPRO 铷钟 GPSDO 对比测试中 tau = 1000 s 处约 2e-12**；用作纯时间间隔计数器并在 EEPROM 里写入线性化参数后，1 s 处可到 8e-10 |
| **jimharman/Arduino-GPSDO** | 基于 Lars 的硬件与代码 | 同上 | 衍生项目 | Lars 方案的整理与再发布版本，适合想直接照着做的人 |

> **为什么 Lars 方案值得单独研究。** 它用极少的元件达到了 1 ns，核心技巧是**把相位比较器的输出变成一个模拟电压再用 ADC 读**，而不是去数时钟周期。对于不想加 TDC 芯片的设计，这是性价比最高的一条路——本项目如果不打算上 TDC7200，这个方案能把分辨率从 5.9 ns 提到 1 ns，成本只有两片逻辑加几个无源件。

### 2.3 第三梯队：低成本易复现

| 项目 | 架构 | 成本与性能 | 许可 | 要点 |
| --- | --- | --- | --- | --- |
| **AndrewBCN/STM32-GPSDO**（André Balsa） | STM32F411CEU6 Black Pill + u-blox Neo-M8 + 10 MHz OCXO | **低于 30 欧元**；**正负 1 ppb 开箱性能**（作者自述） | GPL-3.0 | **开源 GPSDO 里 star 最高（106）**。C++ / Arduino IDE + STM32duino；仓库含 docs、schematics、software；可选 OLED 显示温度 UTC 运行时间状态频率；带蓝牙接口与运行参数日志；5 V @1 A USB-C 供电。作者在 2022 年的 time-nuts 介绍帖中表示当时尚无 ADEV 图 |
| **ahhuhtal/gpsdo** | 驯服 **OSC5A2B02** OCXO | 未公开量化指标 | 见仓库 | 含源码与 PCB 设计文件。用的就是 OCXO 选型文档里提到的那颗经典廉价件，**和本项目的器件选择最接近**，PCB 可直接参考 |
| **YannickTurcotte/GPSDO-YT** | OCXO + u-blox NEO-M8N，**全 AVR 汇编** | 单周期精度（作者自述） | 见仓库 | 极简主义路线，所有定时逻辑与控制用汇编写到单周期精度。适合研究如何把控制环做到确定性时序 |
| **dfannin/gpsdo** | Arduino | 10 MHz / 1 MHz / 10 kHz 三路输出 | 见仓库 | 入门友好 |
| **xiedidan/gpsdo-alpha** | 面向音频与 HAM DIY | 原型级 | 见仓库 | 目标是让任何人在家能做出来 |
| **glenoverby/gpsdo** | GPSDO 控制器 | 未公开 | 见仓库 | 控制器方向 |
| **SomerledDesign/GPSDO** | 基于 Trimble Thunderbolt 模块 | 取决于 Thunderbolt | 见仓库 | 不是从零设计，是给成品 GPSDO 做控制与显示 |

### 2.4 周边工具（做 GPSDO 必然会用到）

| 名称 | 作用 | 说明 |
| --- | --- | --- |
| **TimeLab**（KE5FX John Miles） | **ADEV 绘图与分析的事实标准** | 免费但非开源。做 GPSDO 必装，TICC 可与它实时对接 |
| **Lady Heather** | GPSDO 监控与控制的经典软件 | GitHub 上有 LadyHeatherGPS 等维护分支 |
| **TAPR TICC** | 测量工具，见 2.1 | 评测自己做的 GPSDO 必须有比它更好的参考 |
| **cracl** | C++ 库，统一接口 u-blox 接收机、振荡器、原子钟、时间间隔计数器 | 做上位机软件时可省很多力 |
| **trueposition_gpsdo_usb_oled** | TruePosition GPSDO 控制器固件加隔离分配放大器 | 拆机 GPSDO 改造方向 |
| **10mhz_distributor** | 三路 10 MHz 分配放大器与低通滤波 | 针对 BG7TBL GPSDO 设计，可独立参考 |
| **esp32-gps-pps-ntp-server** | ESP32 的 GPS/PPS 驯服 NTP 服务器，带 Web 面板与 OTA | 如果目标是授时而非频标，这条路更省事 |

---

## 3. 精度到底由什么决定

@fig:gpsdo_adev 图 1　各类振荡器与 GPS 1PPS 的典型 ADEV，以及 GPSDO 输出的合成包络（典型量级示意）

### 3.1 读图的三个要点

1. **GPSDO 的输出不会比两条曲线中较低的那条更好。** 短 tau 段由振荡器决定（GPS 1PPS 在这里很差，2e-8 量级），长 tau 段由 GPS 决定（OCXO 在这里因老化与温漂而变差）。**GPSDO 的全部意义就是把两者各自的好处拼起来。**
2. **交越点的位置就是环路时间常数。** 设得太短，GPS 的短期噪声会灌进输出；设得太长，OCXO 的漂移来不及被修正。典型取 100 到 1000 s。这是 GPSDO 固件里最重要的一个参数。
3. **换更好的 OCXO 只改善交越点左边，换更好的 GNSS 只改善右边。** 这解释了一个常见困惑：为什么给廉价 GPSDO 换上高端 OCXO，长期指标却没变好——因为长期段本来就由 GPS 决定。

### 3.2 决定精度的四个环节，按影响排序

| 环节 | 影响哪一段 | 本项目现状 | 可改进空间 |
| --- | --- | --- | --- |
| **OCXO 质量** | 短 tau（交越点以左） | 待选型，见 OCXO 选型文档 | 普通 OCXO 1e-11 到高端 1e-12，差一个数量级 |
| **GNSS 1PPS 质量加锯齿波修正** | 长 tau（交越点以右） | SKG123N 导航级，**无锯齿波修正** | 换定时级模组加做 qErr 修正，可改善一个数量级。见 GNSS 选型文档 |
| **时间差测量分辨率** | 短 tau，以及环路能否稳定收敛 | 以 10 MHz 为时基，单次 100 ns | 改板送 OSC_IN 到 5.9 ns，用 Lars 模拟方案到 1 ns，加 TDC7200 到 55 ps |
| **环路设计与时间常数** | 交越点位置与形状 | 待实现 | 这是纯固件工作，零成本，但最需要实测调参 |

> **性价比排序很明确：先做锯齿波修正（纯固件，零硬件成本），再换定时级 GNSS 模组，再提升 TIC 分辨率，最后才是升级 OCXO。** 本项目当前最大的短板是第二项，因为完全没做。

---

## 4. 时间差测量架构对比

@fig:gpsdo_tic 图 2　开源 GPSDO 用过的三种时间差测量架构

@fig:gpsdo_res_bar 图 3　各项目的时间差测量分辨率，对数横轴（注意这不等于输出 ADEV）

### 4.1 三种架构怎么选

| 如果你的情况是 | 选 | 理由 |
| --- | --- | --- |
| 先把系统跑通，验证整条链路 | MCU 定时器捕获 | 零外部器件，本项目已经是这个方案，先用它把固件和环路做对。注意本项目当前单次分辨率是 100 ns 而非 5.9 ns，原因见 1.1 节 |
| 不想加芯片但要提升分辨率 | Lars 的模拟相位比较 | 两片 HCMOS 加几个无源件换来约 6 倍分辨率提升，性价比最高 |
| 要做到公开方案的最好水平 | TDC7200 | 55 ps，无需校准，但多一颗芯片加 SPI 加一套固件 |

### 4.2 一个容易被忽略的细节

Carsten Andrich 的方案里有一条很值得借鉴的做法：**在调谐 DAC 之后加一级 1 Hz 有源低通滤波器，以获得优于 16 bit 的等效调谐分辨率**。

这和本项目的做法思路一致——本项目用的是 PWM 加二阶 RC（截止频率 0.80 Hz），本质是同一个技巧。区别在于他用的是有源滤波，顺便解决了源阻抗问题；而本项目是纯无源 RC，源阻抗 40 k 欧，这正是 OCXO 选型文档里标记的**风险 A**。**他的方案等于把那个风险提前解决了，值得照搬。**

---

## 5. 推荐

### 5.1 按目的推荐

| 你的目的 | 推荐项目 | 怎么用 |
| --- | --- | --- |
| **借鉴架构设计**（本项目当前最需要） | **Carsten Andrich 的 STM32G4 方案** | 同为 STM32G4，看他的原理图 PDF 与 time-nuts 帖子，重点看 TDC7200 接法、DAC 后有源滤波、以及为什么不对 OCXO 输出做数字分频 |
| **学控制环与 TIC 原理** | **Lars Walenius GPSDO** | 读 EEVblog 主帖。他的 1 ns 模拟 TIC 和 PI 环参数整定过程是最好的教材，且有大量实测数据可对照 |
| **快速做出一台能用的** | **AndrewBCN/STM32-GPSDO** | GPL-3.0，直接拿代码跑。架构和本项目几乎一样，固件可大段参考 |
| **参考 PCB 与器件选择** | **ahhuhtal/gpsdo** | 它驯服的 OSC5A2B02 就是 OCXO 选型文档里的经典廉价件，PCB 可直接比对 |
| **评测自己做的 GPSDO** | **TAPR TICC** 加 **TimeLab** | 没有比被测对象更好的参考，就测不出真实性能。TICC 是 BSD 开源的，可以自己做 |

### 5.2 对本项目的三条具体建议

1. **立刻补锯齿波修正。** 纯固件工作，零硬件成本，是当前投入产出比最高的一项。前提是换成支持该消息的 GNSS 模组，见 GNSS 选型文档——NEO 系列的 UBX-TIM-TP 或 SkyTraq 的 PSTI,00。
2. **把 Lars 的模拟 TIC 作为中期升级选项。** 在不加 TDC 芯片的前提下，两片 HCMOS 就能把分辨率从 5.9 ns 提到 1 ns。如果 PCB 还有改版机会，这个改动很值。
3. **照搬 Andrich 的 DAC 后有源滤波。** 它同时解决了调谐分辨率和 EFC 源阻抗两个问题，正好对应 OCXO 选型文档里的风险 A。

### 5.3 不建议走的路

- **直接照抄某个项目的完整设计。** 本项目是电池供电便携方案，而上述所有开源项目都是台式供电，没有一个考虑过功耗预算与电池续航。架构可以借鉴，供电与热设计必须自己做。
- **在没有比被测对象更好的参考源之前相信自己的测量结果。** 用本项目的 MCU 去测本项目的 OCXO，测到的是两者误差的组合，不是 OCXO 的真实性能。
- **把分辨率当成精度。** 见第 3 节。55 ps 的 TDC 配一颗差的 OCXO 和一个导航级 GNSS，输出照样很差。

---

## 6. 复现与测量的现实提醒

| 事项 | 说明 |
| --- | --- |
| 参考源问题 | 要验证 1e-12 量级的性能，需要一个比它更好的参考——铷钟、另一台已知良好的 GPSDO，或者长时间与 GPS 比对取统计。**这是 DIY GPSDO 最大的门槛，不是电路** |
| 测量时长 | 要看清 tau = 1000 s 处的 ADEV，至少需要连续采集十小时以上；要看 tau = 1e4 s，需要数天 |
| 温度是最大干扰 | 实验室环境的昼夜温度变化会直接出现在 ADEV 曲线的长 tau 段。公开实测数据之间不可比，除非说明了环境条件 |
| 数据性质要分清 | 本文第 2 节各项目的指标，**作者自述、设计目标、第三方实测三者可信度差别很大**，已逐条标注 |

---

## 7. 关键数值汇总

| 项目 | 数值 |
| --- | --- |
| 本项目当前 TIC 分辨率 | 单次 100 ns（以 OCXO 10 MHz 为 TIM2 时基）；改板送 OSC_IN 后可达 5.9 ns |
| Lars 方案 TIC 分辨率 | 约 1 ns，量程 1 us |
| TDC7200 单次分辨率 | 55 ps；长观测区间极限约 60 ps |
| TAPR TICC 指标 | 单次分辨率小于 60 ps，抖动小于 100 ps，约 100 次每秒 |
| Lars 方案实测 ADEV | 1 s 处 2e-8；1000 s 处 2e-11；与铷钟对比时 1000 s 处约 2e-12 |
| AndrewBCN 方案 | 低于 30 欧元，正负 1 ppb 开箱性能 |
| Andrich 方案设计目标 | 10 km 半径内相对精度优于 10 ns；GNSS 的 ADEV 约 5e-11 @10 s |
| 典型环路交越点 | 100 到 1000 s |

---

## 8. 待办

1. 读 Carsten Andrich 在 time-nuts 的原帖与原理图 PDF，整理出可借鉴的具体电路（TDC7200 接法、DAC 后有源滤波、时钟分配）。
2. 评估给本项目加 TDC7200 的代价：PCB 面积、SPI 占用、固件工作量，与改用 Lars 模拟 TIC 的方案做定量对比。
3. 下载 AndrewBCN/STM32-GPSDO 的固件，研究其环路实现与参数，作为本项目固件的起点（注意 GPL-3.0 的传染性，若要闭源需自行实现）。
4. 比对 ahhuhtal/gpsdo 的 PCB 与本项目 v1.0 的 OCXO 供电与 EFC 部分。
5. 装 TimeLab，确定本项目的 ADEV 测量与数据导出格式。
6. 评估参考源方案：是否需要购置一台已知良好的 GPSDO 或铷钟作为测量基准。

---

## 9. 参考来源

```
GitHub gpsdo topic 仓库列表
  https://github.com/topics/gpsdo
AndrewBCN/STM32-GPSDO
  https://github.com/AndrewBCN/STM32-GPSDO
ahhuhtal/gpsdo
  https://github.com/ahhuhtal/gpsdo
YannickTurcotte/GPSDO-YT
  https://github.com/YannickTurcotte/GPSDO-YT
dfannin/gpsdo
  https://github.com/dfannin/gpsdo
xiedidan/gpsdo-alpha
  https://github.com/xiedidan/gpsdo-alpha
glenoverby/gpsdo
  https://github.com/glenoverby/gpsdo
SomerledDesign/GPSDO (基于 Trimble Thunderbolt)
  https://github.com/SomerledDesign/GPSDO
jimharman/Arduino-GPSDO (基于 Lars 的设计)
  https://github.com/jimharman/Arduino-GPSDO
TAPR TICC 项目主页
  https://www.febo.com/pages/TICC/
TAPR TICC 源码 (BSD)
  https://github.com/TAPR/TICC
time-nuts: New Timestamping / Time Interval Counter: the TICC
  https://www.febo.com/pipermail/time-nuts/2016-November/102235.html
time-nuts: Arduino GPSDO with 1ns res TIC (Lars 原始发布)
  https://febo.com/pipermail/time-nuts/2014-March/083326.html
  https://www.febo.com/pipermail/time-nuts/2014-February/082820.html
time-nuts: Lars GPSDO on EEVblog
  https://febo.com/pipermail/time-nuts_lists.febo.com/2018-September/094020.html
EEVblog: Lars DIY GPSDO with Arduino and 1ns resolution TIC
  https://eevblog.com/forum/projects/lars-diy-gpsdo-with-arduino-and-1ns-resolution-tic/
EEVblog: DIY GPSDO project w/ STM32, TDC7200 (thinkfat)
  https://eevblog.com/forum/projects/diy-gpsdo-project-w-stm32-tdc7200/
time-nuts: GPSDO/GNSSDO project: STM32G4 + u-blox ZED-F9T + TDC7200 (Andrich)
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-August/106228.html
time-nuts: The STM32 GPSDO, a short presentation (Balsa)
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-March/105383.html
N8UR: GPS 接收机定时性能评测 (HamSCI 2021)
  https://hamsci.org/sites/default/files/publications/2021_HamSCI/
  20210319_1320z-John_Ackermann_N8UR.pdf
SepticElectronics/High-Speed-Timer (TDC7200 + FPGA, 55 ps)
  https://github.com/SepticElectronics/High-Speed-Timer
```
