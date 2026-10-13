# GPSDO 功能需求文档

> **数据来源与可信度声明。** 本文梳理一台 GPSDO（GNSS 驯服振荡器）通常要实现的功能，依据是公开的商用产品手册、规格书、NIST 的第三方评测与 time-nuts 社区讨论，逐条来源列在第 10 节。**数据性质不一**：Trimble ThunderBolt 用户手册与 NIST 论文为一手原文，本文直接引用；Jackson Labs 的 SCPI 命令只拿到了命令名与取值范围，未拿到完整说明；各厂商的性能数字是规格书标称值，测试条件互不相同，**不能横向直接比较**。第 9 节对照本项目 Rev1.0 原理图的部分，以 2026-10-13 保存的 `hardware/schematic/v1.0/GPSDO_Rev1.0` 为准。

---

## 1. 结论摘要

| 问题 | 回答 |
| --- | --- |
| GPSDO 的本质 | 用 GNSS 的 1PPS 提供**长期**准确度，用本地 OCXO 提供**短期**稳定度，两者通过一个慢速控制环路结合。环路时间常数就是两者的分界点 |
| 最核心的功能 | 输出 10 MHz 与 1PPS、驯服环路、**保持（Holdover）**、锁定与告警指示。缺任何一项都不能算完整的 GPSDO |
| 区分"能用"与"好用"的功能 | 位置保持（Position Hold）、天线线缆时延补偿、锯齿波（qErr）修正、温度与老化补偿、可查询的状态与告警、逐秒数据记录 |
| 最值得照抄的参考 | **Trimble ThunderBolt** 的状态机（上电、正常、保持、恢复）与告警位定义，见第 4 节与第 6 节。它是 time-nuts 社区的事实标准，手册公开且完整 |
| NIST 评测的教训 | 被测的四台商用 GPSDO**没有一台在所有方面都优秀**。常见问题有：自测量引入大时间误差、偶发超过 100 ns 的相位跳变、缺少诊断信息、1PPS 与 10 MHz 不同相。见第 8 节 |
| 本项目 Rev1.0 的差距 | 硬件已具备 TDC7200、TMP117、以 10 MHz 作 MCU 时钟这三项进阶基础；缺 1PPS 输出、状态 LED、天线短路与开路检测、VCTRL 回读。固件从零开始。见第 9 节 |

---

## 2. 基本原理（一页说明）

GNSS 接收机输出的 1PPS 在长期上与 UTC 对齐，在 1 秒量级上却有几十 ns 的抖动；OCXO 恰好相反，短期非常稳，长期会因老化和温度漂走。GPSDO 的做法是：

1. 用时间间隔计数器（TIC）每秒测量"本地 1PPS"（由 OCXO 分频得到）相对"GNSS 1PPS"的相位差。
2. 控制器（通常为 PI，或 PI 加积分器的三阶环）根据相位差计算 OCXO 的压控电压（EFC）。
3. 环路时间常数取在 OCXO 的 Allan 方差与 GNSS 1PPS 噪声的交点附近，典型值为 **100 至 1000 秒**。比这更短，输出会继承 GNSS 噪声；比这更长，输出会继承 OCXO 漂移。

@fig:fr_loop 图 1　GPSDO 基本原理框图

@fig:gpsdo_adev 图 2　各类振荡器与 GNSS 1PPS 的典型 ADEV，以及 GPSDO 输出的合成包络（典型量级示意）

ThunderBolt 手册把这种"只调频率、不跳 1PPS，靠频率慢慢把相位拉回来"的工作方式称为**相位锁定（phase locking）**，并指出整机绝大部分时间都处于此模式。

---

## 3. 功能总表

优先级定义：**P0** 为没有就不是 GPSDO；**P1** 为合格产品应有；**P2** 为进阶或可选。

@fig:fr_features 图 3　GPSDO 功能地图（按类别与优先级）

### 3.1 输出

| 功能 | 优先级 | 说明与参考 |
| --- | --- | --- |
| 10 MHz 频率输出 | P0 | 正弦或方波，50 欧驱动。NIST 测试的四台全部具备，其中两台为多路 |
| 1PPS 时间输出 | P0 | 3.3 V CMOS 或 TTL，上升沿小于几 ns。Fury 标称上升时间小于 2 ns |
| 多路 10 MHz 输出 | P1 | 各路之间需要隔离，一路短路不能影响其他路 |
| 输出端 ESD 与 TVS 保护 | P1 | SMA 接口直接暴露在外，参考设计（Carsten Andrich）每路都加了 TVS |
| 1PPS 与 10 MHz 同相 | P1 | 1PPS 的边沿应对齐 10 MHz 的某个过零点。NIST 发现两台被测设备不同相（见第 8 节） |
| 未锁定时静默或标记输出 | P2 | 未锁定或保持超时后关闭 1PPS，或通过告警位声明输出不可信 |
| 可编程频率输出 | P2 | 如 Leo Bodnar 的 1 Hz 至 1.1 GHz 可编程输出，属于另一类产品 |

### 3.2 GNSS 接收与定时模式

| 功能 | 优先级 | 说明与参考 |
| --- | --- | --- |
| 定时模式：自测量（Survey-in） | P0 | 静止安装时先累积若干定位结果求平均位置。ThunderBolt 默认 2000 次定位，约 1 小时。u-blox 定时型模块用 UBX-CFG-TMODE2（M8T）配置 |
| 位置保持（Position Hold） | P0 | 位置确定后不再解算位置，只解时间，**单颗卫星即可授时**。NIST 称其为"所有用作时频标准的 GPSDO 都非常需要的功能"，四台被测设备全部具备 |
| 手动输入已知坐标 | P1 | 已知精确坐标时跳过自测量。注意存储精度：ThunderBolt 用单精度浮点，会引入数英尺误差 |
| 位置存入非易失存储 | P1 | 掉电重启后直接进入位置保持，省去一小时自测量 |
| 天线移动检测 | P1 | ThunderBolt 在检测到位置偏差（可达 1 英里级别）时置告警位，并建议清除旧位置重新测量 |
| 天线线缆时延补偿 | P1 | 以 ns 为单位输入，分辨率 1 ns（NIST 测试中三台为此方式，一台要求输入线缆长度的厘米数，被批评为不便）。线缆时延约 1.25 ns 每英尺 |
| 仰角掩码（Mask Angle） | P1 | 典型 10 度。ThunderBolt 手册指出低仰角卫星频繁进出会造成授时跳变 |
| 锯齿波修正（qErr） | P2 | 接收机 1PPS 被其内部时钟量化，误差可达数十 ns。u-blox 通过 UBX-TIM-TP 报告下一个脉冲的量化误差，固件在 TIC 结果中扣除即可。只在 1 Hz 下可信 |
| UTC 与 GPS 时间、闰秒 | P1 | 1PPS 对齐 UTC 还是 GPS 时间可选；闰秒预告需上报（ThunderBolt 次要告警位 7） |
| 天线馈电与开路、短路检测 | P1 | 通过检测天线 LNA 的电流判断。ThunderBolt 提供开路与短路两个告警位，且短路保护能承受 0 至 12 V |
| 卫星与信噪比信息 | P1 | NIST 把"不显示信号强度与跟踪卫星"列为缺点，因为它们是诊断安装问题的主要依据 |

### 3.3 驯服环路

| 功能 | 优先级 | 说明与参考 |
| --- | --- | --- |
| 时间间隔测量（TIC） | P0 | 测本地 1PPS 与 GNSS 1PPS 的相位差。分辨率从 100 ns（定时器以 10 MHz 计数）到几十 ps（TDC7200）不等 |
| PI 或三阶控制器 | P0 | ThunderBolt 默认时间常数 100 s、阻尼 1.2；Jackson Labs 以 EFCScale（比例增益，0 至 500）与 EFCDamping（2 至 4000）两个参数表示 |
| EFC 增益与极性 | P0 | OCXO 的 Hz 每伏斜率及正负号。ThunderBolt 默认 -5.0 Hz/V；Jackson Labs 为 SERVo:SLOPe POS 或 NEG。**极性设反会使环路变成正反馈而发散** |
| EFC 上下限与初始值 | P0 | ThunderBolt 设最小和最大控制电压及上电初值 |
| 1PPS 有效性检查 | P0 | 剔除丢失、重复或明显离群的 1PPS，避免一次坏测量把 EFC 打飞 |
| 快速锁定（变增益） | P1 | 上电时先用大增益快速收敛，再逐渐降到正常值。Jackson Labs：FASTlock 1 至 20 倍，FALEngth 为降回 1 倍所用的时间。手册提醒大增益会增加相位噪声 |
| 频率锁定转相位锁定 | P1 | 先只按频率偏差调整，同时把 1PPS 直接移到位，频率接近后再转入相位锁定（ThunderBolt 上电流程） |
| 1PPS 输出偏移 | P1 | 让输出 1PPS 相对 UTC 有一个可设的偏移。Jackson Labs：SERVo:1PPSoffset，单位 ns，范围正负 5 000 000 |
| 手动 EFC（禁用环路） | P2 | ThunderBolt 的 Disabled 状态允许用户直接设置控制电压，用于生产测试与 OCXO 特性测量 |

---

## 4. 状态机

下面的状态划分取自 ThunderBolt 用户手册第 5 章，并补充了常见的自测量阶段：

@fig:fr_states 图 4　GPSDO 驯服状态机

| 状态 | 行为 |
| --- | --- |
| Power-Up | OCXO 预热到足够稳定；先按频率偏差粗调，同时把 1PPS 直接移到位；频率接近后转入相位锁定并逐渐稳定，之后进入 Normal |
| Normal | 只靠调频率维持相位锁定。只要 GNSS 信号与测量有效就一直保持。同时**学习 OCXO 的稳定性特征**，供保持时使用 |
| Auto Holdover | GNSS 信号丢失时自动进入，信号恢复后自动离开 |
| Manual Holdover | 用户命令进入，用于测试；必须由用户命令退出。退出时如果 GNSS 无效，则转入 Auto Holdover |
| Recovery | 消除保持期间积累的相位与频率偏差。两种手段：**跳步同步（jam sync）**直接移动 1PPS，或**限速调频**让 1PPS 慢慢滑回 |
| Disabled | 环路完全停止，允许手动设定控制电压 |

**恢复策略是一个需要让用户选择的取舍。** ThunderBolt 手册明确说明：若要快速恢复，就允许跳步同步；若要保证每个 1PPS 之间严格是 10 000 000 个 10 MHz 周期（对下游计数类设备很重要），就禁用跳步同步，并把最大频率偏移设到可容忍的值。默认参数为跳步门限 300 ns、最大频率偏移 50 ppb。

---

## 5. 保持（Holdover）

保持是 GPSDO 与"带 GNSS 的普通晶振"最根本的区别，其性能决定 GNSS 中断时还能维持多久的可用精度。

| 功能 | 优先级 | 说明与参考 |
| --- | --- | --- |
| 冻结 EFC 于历史平均值 | P0 | 最简单的做法。Lars Walenius 的方案在 1PPS 丢失时保持最近的 DAC 值，并维护过去 12 小时的 5 分钟平均和过去 18 天的 3 小时平均 |
| 老化补偿 | P1 | 按学习到的老化斜率在保持期间持续修正 EFC。Jackson Labs：SERVo:AGINGcompensation |
| 温度补偿 | P1 | 记录 EFC 与温度的关系，保持期间按当前温度修正。Jackson Labs：SERVo:TEMPCOmpensation |
| 卡尔曼滤波学习 | P2 | ThunderBolt 用卡尔曼滤波记录 OCXO 随时间与温度的行为，**至少需要 24 小时**训练才有良好效果 |
| 保持时长上报 | P0 | ThunderBolt 在状态包中给出保持时长（秒）；不在保持时给出上一次的时长。Jackson Labs：SYNChronization:HOLDover:DURation? |
| 保持超时告警 | P1 | 超过设定时长后置告警，提示输出精度已不可信 |

影响保持性能的主要因素是**老化与温度**，其次是气压、湿度等环境量。剔除确定性部分后，剩下的随机漂移用 Allan 方差或 TDEV 描述。

典型保持指标（规格书标称，条件各不相同）：

| 产品 | 振荡器 | 24 小时保持 |
| --- | --- | --- |
| Jackson Labs LC 1x1 | OCXO | 小于正负 15 us（25 摄氏度，无运动与气流，已锁定 5 天以上） |
| VIAVI Fury | 双恒温 OCXO | 优于 7 us |
| VIAVI CSAC GPSDO | 芯片原子钟 | 小于正负 2 us |
| VIAVI 铷钟 GPSDO | 铷钟 | 小于正负 0.6 us |
| Ettus USRP X3x0 GPSDO | OCXO | 3 小时内小于 20 us |

电信侧的参照是 ITU-T G.8272.1（ePRTC）：锁定时与 UTC 相差 30 ns 以内，保持 14 天内 100 ns 以内。这需要铯钟或高等级铷钟才能达到，**不适用于 OCXO 类 GPSDO**，列出来只作为量级参照。

---

## 6. 告警与指示

### 6.1 告警位（以 ThunderBolt 为模板）

ThunderBolt 把告警分为**严重**（会严重影响功能）与**次要**（应提醒用户，但不一定影响功能）两级，用位域上报，这套定义可以直接照搬：

| 级别 | 告警 | 本项目可否实现 |
| --- | --- | --- |
| 严重 | ROM 校验错误 | 可：上电对 Flash 做 CRC |
| 严重 | RAM 自检失败 | 可 |
| 严重 | 电源电压失效 | 需 ADC 监测电源轨 |
| 严重 | **EFC 已到达上下限**（OCXO 再也调不动，需要换 OCXO） | 可：在固件中判断 PWM 占空比是否到达限值 |
| 次要 | **EFC 接近上下限**（OCXO 两年内将调不动，起因是晶体老化） | 可 |
| 次要 | 天线开路（LNA 电流过小） | Rev1.0 **无电流检测电路** |
| 次要 | 天线短路（LNA 电流过大） | 同上 |
| 次要 | 无可用卫星 | 可：解析接收机消息 |
| 次要 | 未在驯服 | 可 |
| 次要 | 自测量进行中 | 可 |
| 次要 | 无存储位置 | 可 |
| 次要 | 闰秒预告 | 可：u-blox 提供 |
| 次要 | 处于测试模式 | 可 |
| 次要 | 位置可疑（疑似天线被移动） | 可：比较当前解算位置与存储位置 |
| 次要 | 非易失参数损坏，已恢复出厂值 | 可：参数区带 CRC |
| 次要 | 星历或历书不完整 | 可 |

除告警位外，ThunderBolt 的状态包还同时给出：接收机模式、驯服状态、自测量进度百分比、保持时长、驯服活动、1PPS 偏移（ns）、10 MHz 偏移（ppb）、DAC 值、温度。这一组字段就是一个合格 GPSDO 状态输出的样板。

### 6.2 硬件指示

| 形式 | 例子 |
| --- | --- |
| LED | BG7TBL 用三颗：Alarm、GPS Lock、Run |
| 告警输出引脚 | Connor-Winfield FTS250 提供三路独立告警输出：失锁、保持、天线故障，便于接入上位设备 |
| 逐秒状态行 | TruePosition 每秒输出一行：10 MHz 好坏、1PPS 好坏、天线状态、保持时长、跟踪卫星数、锁定或恢复状态 |

---

## 7. 通信、配置与维护

| 功能 | 优先级 | 说明与参考 |
| --- | --- | --- |
| 串口命令行 | P0 | 商用产品两大流派：Trimble 的二进制 TSIP 协议，与 Jackson Labs、Symmetricom 等的 **SCPI 风格文本命令**。自研产品推荐后者，人和脚本都能直接用 |
| 状态查询 | P0 | 锁定、卫星、告警、保持时长等。Symmetricom 示例：`LED:GPSLock?`、`GPS:SATellite:TRACking?`、`SYSTem:STATus?` |
| 环路参数可调 | P1 | 时间常数、阻尼、增益、EFC 极性与上下限、快速锁定 |
| NMEA 透传 | P1 | 让上位软件（如 Lady Heather、gpsd）直接拿到接收机数据。Ettus USRP 通过传感器接口暴露 GPRMC 与 GPGGA |
| 参数非易失存储 | P0 | 带校验，损坏时恢复默认值并置告警（见 6.1） |
| 固件升级 | P1 | 串口或 USB 进入 Bootloader。Jackson Labs：`SYSTem:ISP` 命令，或上电时拉低 ISP 引脚 |
| 上电自检 | P1 | ROM、RAM、电源轨，结果计入严重告警 |

### 7.1 SCPI 命令组参考（Jackson Labs 风格）

下表的命令名与取值范围摘自 Jackson Labs Micro-JLT 手册，**部分命令的详细语义未取得**，仅供设计命令集时参考：

| 命令组 | 代表命令 | 用途 |
| --- | --- | --- |
| GPS | `GPS:SURVey ONCE`、`GPS:REFerence:ADELay`（时延，正负 32767 ns） | 自测量、天线时延 |
| SYNChronization | `SYNC:HOLDover:DURation?`、`SYNC:HOLDover:STATe?`、`SYNC:FEEstimate?`、`SYNC:HEALth?` | 保持、频率误差估计、健康状态 |
| SERVo | `EFCScale`、`EFCDamping`、`SLOPe`、`1PPSoffset`、`FASTlock`、`FALEngth`、`TEMPCOmpensation`、`AGINGcompensation`、`TRACe` | 环路参数与补偿 |
| PTIME | 日期、闰秒、时间戳 | 时间信息 |
| SYSTem | `SYSTem:ISP` | 固件升级 |

Jackson Labs 还允许通过命令手动进入和退出保持（`SYNC:HOLDover:INITiate` 与 `SYNC:HOLDover:RECovery:INITiate`），并且在手动保持期间 `SYNC:TINT?` 的相位数据仍然有效，可以直接用来画 OCXO 自由运行时的 ADEV。这一点很实用，建议照做。

### 7.2 数据记录

GPSDO 的调试与验收几乎全靠数据。建议每秒输出一行，至少包含：时间戳、TIC 相位差、qErr、EFC 值、温度、卫星数、驯服状态。格式做成 TimeLab 可直接导入，就能画出 ADEV 曲线。AndrewBCN 的 STM32-GPSDO 也把"大量记录运行参数以便日后调优软件"列为主要特性之一。

---

## 8. NIST 评测指出的常见问题

NIST 2005 年把四台商用 GPSDO（两台 OCXO、两台铷钟）接同一天线，以 UTC(NIST) 为参考连续测量两个 60 天。总结中列出的问题，正好可以作为设计检查清单：

| 问题 | 对设计的启示 |
| --- | --- |
| 设备内部时延可能远大于线缆时延 | 内部时延要校准，不能只补偿线缆 |
| 天线自测量可能引入很大的时间误差 | 自测量时间要足够长；能用已知坐标就用已知坐标。time-nuts 社区建议自测量跨越 24 小时，以平均掉卫星与大气的周期性 |
| 偶发超过 100 ns 的相位跳变，原因不明 | 环路要有离群值剔除；要有逐秒数据记录，才能事后定位 |
| 不显示信号强度与跟踪卫星 | 状态输出必须包含这些诊断信息 |
| 坐标与时延的输入方式不规范 | 时延用 ns 输入，坐标用度或 ECEF，不要用线缆长度 |
| 有的设备驯服间隔很长，不能紧密跟随 GNSS | 时间常数要可调，并给出合理默认值 |
| 1PPS 与 10 MHz 不同相 | 1PPS 由 10 MHz 分频产生，保证边沿对齐 |

NIST 的结论是：好的设备在校准线缆时延后可以把时间做到距 UTC(NIST) 100 ns 以内，在 1 秒处的频率短稳达到 1e-12 量级；但"厂商规格可能只是实际性能的粗略指示"。

### 8.1 典型性能指标量级（规格书标称）

| 指标 | 典型值与出处 |
| --- | --- |
| 1PPS 相对 UTC | VIAVI CSAC 与铷钟 GPSDO：正负 15 ns RMS（位置保持模式）；Jackson Labs LC 1x1：正负 35 ns RMS；Ettus USRP：抖动小于 50 ns |
| 锁定后 ADEV | Fury：0.1 s 以上小于 1e-11；Ettus USRP：24 小时以上 5e-11 |
| 10 MHz 相位噪声 | Jackson Labs LC 1x1：1 Hz 处 -90、10 Hz 处 -120、1 kHz 处 -150 dBc/Hz |
| 预热 | Jackson Labs LC 1x1：OCXO 3 分钟以内，整机 9 分钟以内达到 5e-9 |
| 冷启动首次定位 | Jackson Labs LC 1x1：小于 45 秒 |
| ThunderBolt 冷启动全过程 | 约 20 分钟预热，加约 1 小时自测量，然后进入驯服（用户实测描述） |

---

## 9. 对照本项目 Rev1.0

| 功能 | 优先级 | Rev1.0 硬件现状 | 结论 |
| --- | --- | --- | --- |
| 10 MHz 输出 | P0 | 1 路，经 BUF602 驱动 | 有，但 BUF602 单 5 V 供电的偏置问题待解决 |
| 1PPS 输出 | P0 | **无** | **缺**，需要从 MCU 定时器引出并加驱动 |
| 输出 TVS | P1 | 无 | 缺 |
| TIC | P0 | TDC7200，加上 10 MHz 作为 MCU 时钟后用定时器捕获 | 优于大多数开源方案 |
| EFC | P0 | PWM 加二阶有源低通 | 有；基准缓冲门与运放共模范围待改 |
| 定时模式与位置保持 | P0 | NEO-M8T 定时型模块 | 支持，固件配置 TMODE2 即可 |
| qErr 锯齿波修正 | P2 | NEO-M8T 输出 UBX-TIM-TP | 支持，纯固件工作 |
| 温度补偿 | P1 | TMP117 | 硬件已具备 |
| 天线开路与短路检测 | P1 | 无电流检测 | 缺；若需要，在天线馈电路径上加电流检测 |
| 状态 LED | P1 | 只有电源指示 | 缺；建议 PC10、PC11、PC4 驱动三颗 |
| EFC 到达或接近上下限告警 | P0 | 固件可由占空比判断 | 可做；VCTRL 的 ADC 回读可作为旁证（可选） |
| 串口命令行 | P0 | CH340E 转 USB | 硬件已具备 |
| 参数存储 | P0 | 片内 Flash | 可做 |
| 固件升级 | P1 | SWD；USB 串口可配合 ST 系统 Bootloader | 可做 |

建议的固件实现顺序：

1. 串口命令行、状态行、数据记录（先有观测手段）。
2. 接收机配置：定时模式、自测量、位置保持、TIM-TP。
3. TIC 与 1PPS 有效性检查。
4. PI 环路、快速锁定、状态机（Power-Up、Normal、Holdover、Recovery）。
5. 告警位、LED、参数存储。
6. qErr 修正、温度与老化补偿、保持性能优化。

---

## 10. 来源

一手资料：

- Trimble, ThunderBolt GPS Disciplined Clock User Guide（2002 版）：https://xdevs.com/doc/Thunderbolt/Thunderbolt_Users_Guide_2002-v4.pdf ，第 5 章状态机与卡尔曼滤波、附录 A 的出厂参数与告警位定义
- M. A. Lombardi, A. N. Novick, V. S. Zhang, "Characterizing the Performance of GPS Disciplined Oscillators with Respect to UTC(NIST)", NIST, 2005：https://tf.nist.gov/general/pdf/2086.pdf
- Jackson Labs Micro-JLT GNSS User Manual（ManualsLib 第 54 页）：https://www.manualslib.com/manual/1894038/Jackson-Labs-Micro-Jlt-Gnss.html?page=54
- Ettus Research, USRP X3x0 GPSDO 文档：https://uhd.readthedocs.io/en/latest/page_gpsdo_x3x0.html

规格书：

- VIAVI Fury GPSDO 规格书：https://www.viavisolutions.com/en-us/literature/secure-upnt-fury-gpsdo-data-sheets-en.pdf
- VIAVI CSAC GPSDO 规格书：https://viavisolutions.com/en-uk/literature/csac-chip-scale-atomic-clock-gpsdo-frequency-standard-data-sheets-en.pdf
- VIAVI 铷钟 GNSS 驯服频率标准规格书：https://viavisolutions.com/en-us/literature/ln-rubidium-gnss-disciplined-frequency-standard-data-sheets-en.pdf
- Jackson Labs LC 1x1 规格书：https://gps-world.biz/wp-content/uploads/2023/10/LC_1x1_Specsheet_Single_Oven.pdf

社区与二手资料：

- time-nuts，Jackson Labs 手动保持命令：https://www.febo.com/pipermail/time-nuts/2016-March/096714.html
- time-nuts，自测量时长与线缆时延：https://www.febo.com/pipermail/time-nuts/2009-August/040167.html
- time-nuts，线缆时延不改变 1PPS 与 10 MHz 的相位关系：https://www.febo.com/pipermail/time-nuts/2009-September/040778.html
- time-nuts，Lars 方案的保持做法：https://lists.febo.com/pipermail/time-nuts/2015-April/091518.html
- time-nuts，u-blox qErr 与 TIM-TP：https://febo.com/pipermail/time-nuts_lists.febo.com/2022-December/107094.html
- u-blox Timing AppNote GPS.G6-X-11007：https://mikrocontroller.net/attachment/546526/Timing_AppNote__GPS.G6-X-11007_.pdf
- TruePosition GPSDO 状态行格式：https://wiki.millerjs.org/trueposition_gpsdo
- Symmetricom GPSDO 命令示例：https://eevblog.com/forum/projects/a-look-at-my-symmetricom-gpsdo-(ocxo-furuno-receiver)
- BG7TBL GPSDO 指示灯：https://www.eevblog.com/forum/testgear/bg7tbl-gpsdo-master-reference/msg4967932/
- AndrewBCN STM32-GPSDO README：https://github.com/AndrewBCN/STM32-GPSDO
- Wikipedia, Holdover in synchronization applications：https://en.wikipedia.org/wiki/Holdover_in_synchronization_applications
- Calnex, ITU-T G.8272.1（ePRTC）摘要：https://calnexsolutions.atlassian.net/wiki/spaces/GDW/pages/10518876/ITU-T+G.8272.1+ePRTC+One-Page+Summary
