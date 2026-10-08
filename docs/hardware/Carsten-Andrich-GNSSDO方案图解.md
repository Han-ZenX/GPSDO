# Carsten Andrich GNSSDO 方案图解

> **资料来源与可信度声明。** 本文的电路细节全部取自作者公开的两版原理图 PDF（v1：2022-08-05；v2：2022-08-10 至 08-11）和 v2 版图 PDF，设计思路取自作者在 time-nuts 邮件列表与 EEVblog 论坛的两个讨论串（2022-08-05 至 2022-09-03），逐条来源列在第 13 节。**截至作者最后一条公开帖（2022-09-03），整机没有发布任何实测结果，固件与 KiCad 工程也未公开**，只有原理图与版图的 PDF。文中的滤波器 f0、Q、群时延与幅频曲线是本文按原理图元件值**自行计算**的；标注"推断"的内容是本文根据帖子描述整理，作者并未明说。

---

## 1. 方案速览

| 项目 | 内容 |
| --- | --- |
| 作者 | Carsten Andrich，自述职业为射频工程师 |
| 发布 | 2022-08-05 同时发到 time-nuts 与 EEVblog；08-11 更新原理图并发布版图 |
| 用途 | 移动车辆之间的精确时间同步，服务于分布式 SDR 的相干采样与毫米波变频器。载体主要是汽车，也可能上飞机 |
| 为什么自己做 | 作者在工作中用过 Ministd、Jackson Labs LC_XO、SRS FS740，移动中都不满足要求 |
| 指标目标 | 10 km 半径内、移动中相对时间误差 < 10 ns，**期望 < 1 ns**。只要求相对同步，不关心绝对 UTC 误差 |
| 成本目标 | 单台器件与制造费用 < 500 欧元，**不含 OCXO** |
| 开发优先级 | 性能 > 简洁 > 性价比（作者原话的顺序） |
| 核心器件 | ZED-F9T（用 RCB-F9T 评估板）、TDC7200、STM32G474RE、Abracon AOCJY OCXO、LMK1C1103、AD5542A、ADR4533、OPA189、BUF602 x5、TMP117；v2 加 IIM-42652 IMU |
| 板子 | 100 x 100 mm，5 路 SMA，三路电源全部外供 |
| 进度 | 原型设计定稿；TDC7200 死区问题已用面包板实测验证；**整机性能未见公开** |

@fig:ca_usecase 图 1　应用场景：基准站播发差分修正，各车辆上的 GNSSDO 彼此相对同步

### 1.1 作者明确提出的三处改进

作者说明这套架构受 thinkfat（Matthias Welwarsky）的 STM32 + TDC7200 方案启发，并在三处做了改动：

| 方面 | thinkfat 的做法 | Andrich 的做法 | 理由（作者自述） |
| --- | --- | --- | --- |
| OCXO 输出给 TDC | 经 74HC390 分频 | **10 MHz 直接送 TDC7200**，不分频 | 分频器的传播延迟随温度变化 |
| 时钟分配器件 | 74 系列逻辑 | **只用 LMK1C110x 这类低抖动时钟芯片** | 74 系列没有抖动与相噪指标 |
| 调谐电压 | DAC 直接送 OCXO | **DAC 后加 1 Hz 有源低通** | 一是压低电源、基准、DAC 送进 EFC 的噪声；二是为在 16 bit 之上叠加 PWM 扩展分辨率留出条件 |

---

## 2. 系统架构

@fig:ca_system 图 2　系统总框图（v2 原理图），颜色区分信号类型

整机分成四块：**GNSS 接收**（RCB-F9T 板插在主板上）、**时间测量**（MCU 定时器 + TDC7200）、**OCXO 及其调谐**（DAC、基准、有源滤波、OCXO、时钟分配）、**输出驱动**（5 路 BUF602）。

### 2.1 关键器件

| 位号 | 器件 | 作用 | 关键参数 |
| --- | --- | --- | --- |
| U201 | STM32G474RETx | 主控 | 170 MHz；TIM2 为 32 bit，单拍 5.88 ns；HRTIM 等效 184 ps |
| U231 | TDC7200 | 时间间隔测量 | 单次约 55 ps；模式 1 量程 12 ns 起；外部时钟 1 至 16 MHz |
| U321 | Abracon AOCJY | 10 MHz OCXO | 3.3 V 供电；原理图标注预热峰值电流 1.1 A |
| U331 | LMK1C1103 | 1 分 3 时钟缓冲 | 通道偏斜 <= 50 ps（-40 至 125 摄氏度），上升沿 <= 0.7 ns（作者引用） |
| U302 | AD5542A | 16 bit 调谐 DAC | 无缓冲 R-2R 输出，内阻约 6.25 k 欧，与码值无关 |
| U301 | ADR4533 | DAC 电压基准 | 3.3 V；可用 JP302 改接 OCXO 自身的 VREF 输出 |
| U311 | OPA189 | 二阶有源低通 | 零漂移运放，+5 V 单电源供电 |
| U341 | TMP117 | 温度传感器 | 放在 OCXO 塑料罩内 |
| U401 至 U491 | BUF602 x5 | 50 欧输出驱动 | 每路串 49.9 欧源端匹配 + TVS |
| J102 | RCB-F9T | ZED-F9T 评估板 | 2x4 排针叠插：V_ANT、VCC、TXD、RXD、RST、TP1、TP2、GND |
| J103 | IIM-42652 子板 | 6 轴 IMU（v2 新增） | SPI3 + MCU 提供的外部时钟 |

**电源：** 主板上**没有任何稳压器**。+5 V、+3.3 V、-5 V 三路由 J101 四针端子外供：+5 V 给 OPA189、ADR4533 与天线偏置，+3.3 V 给 MCU、TDC、DAC、OCXO、LMK、F9T，+/-5 V 给 BUF602。

---

## 3. 时钟与脉冲分配

@fig:ca_clock_tree 图 3　10 MHz 与各路脉冲的完整路径（v2），按相干域与异步域分区

这张图是理解整个方案的关键，要点有四：

1. **只有 GNSS 脉冲是异步信号。** TDC 的时基、MCU 的全部定时器、对外输出的脉冲，全部来自同一个 OCXO，经同一片 LMK1C1103 分出。MCU 通过 PF0（OSC_IN）以 HSE 旁路方式直接吃 10 MHz，再由 PLL 倍频到 170 MHz，因此 TIM2 每 100 ns 恰好走 17 拍，与 10 MHz 严格同相。
2. **全程不分频、不同步。** 作者拒绝 74 系列的理由有具体数字：74HC74 在 5 V 下传播延迟典型 14 ns、最大约 40 ns；即使 74AHC74 在全温区也有 1.0 至 8.5 ns 的跨度，这个不确定性会直接落在"TDC 测到的沿"与"SMA 输出的沿"之间。LMK1C1103 的通道间偏斜全温区不超过 50 ps，**各通道一起漂，相互抵消**。
3. **上升沿速度。** TDC7200 要求 START、STOP、CLOCK 的上升时间标称 1 ns。74HC74 的转换时间典型 7 ns、最大 19 ns，不满足；LMK1C110x 的上升沿不超过 0.7 ns。
4. **输出脉冲由 OCXO 派生，不直接用 GNSS 脉冲。** GNSS 原始脉冲 TP2 另走一路 BUF602 送到 SMA，只作对照。

> **v2 的一处细节：** LMK 到 MCU、到 TDC 的两路各加了一个 0 欧串联电阻 R331、R332（v1 没有）。作者没说明用途，推断是预留的阻尼或调试断点。

---

## 4. 时间间隔测量：TIM2 粗测 + TDC7200 细测

### 4.1 原理

@fig:ca_tic_timing 图 4　两级时间测量时序。情形 A 是常规情况，情形 B 是 10 MHz 沿落进 TDC 死区的情况

TDC7200 的模式 1 只能测十几到几百 ns 的短间隔，而且单次误差随间隔线性增大（见 4.3 节）。作者的做法是：

- **START 接 GNSS 脉冲，STOP 与 CLOCK 都接连续的 10 MHz**（经 JP231 短接）。于是 TDC 测到的是"脉冲到其后第一个可用 10 MHz 沿"的时间 tau，范围 12 至 112 ns，这是**周期内的精细相位**。
- **TIM2 的 32 bit 输入捕获（PB11，TIM2_CH4）同时给出粗时刻 t_c**，分辨率 5.88 ns，用来判定"是哪一个 10 MHz 周期"，即解决 TDC 读数的 100 ns 周期模糊。
- 组合：k = round((t_c + tau) / 100 ns)，脉冲精确时刻 t = k x 100 ns - tau。

**一个容易忽略的好处：粗测的误差只要小于正负 50 ns 就不影响取整。** 所以 TIM2 输入同步造成的几个时钟周期的固定延迟完全无关紧要，粗测不需要标定到 ns 级。

### 4.2 TDC7200 死区之争与作者的解法

@fig:ca_tdc 图 5　左：周期性 STOP 下的读数折叠关系；右：作者面包板实测的单次标准差

发帖次日，vk3jpk 指出 TDC7200 模式 1 的最小可测间隔是 12 ns，脉冲落在 10 MHz 沿之前 0 至 12 ns 的情况（约 12% 的时间）会出问题，并建议照 TAPR TICC 的思路加一级 D 触发器同步器。thinkfat 也提到他用 74HC74 把 STOP 延迟一个周期。社区里的三种方案：

| 方案 | 做法 | 代价 |
| --- | --- | --- |
| 同步器（TICC 思路） | D 触发器链把脉冲同步到 10 MHz，TDC 测脉冲到同步器输出 | 多器件，触发器延迟随温度变化，需从 TDC 结果中消掉 |
| STOP 延迟一周期（thinkfat） | 74HC74 把 STOP 推后 100 ns | 多器件，上升沿慢 |
| **作者的方案 A：利用周期性** | 不加任何器件。第一个沿落进死区就被忽略，TDC 自然测到下一个沿，读数从 0 至 12 ns 折叠到 100 至 112 ns | 折叠区的读数长了 100 ns，单次误差略大 |
| 作者的方案 B | TDC7200 寄存器 CLOCK_CNTR_STOP_MASK = 1，开始后等一个时钟周期再接受 STOP | 方案 A 失败时的后备 |

作者坚持方案 A 的理由：数据手册没有任何地方说 STOP 落在死区或先于 START 会影响后续测量；而且他不愿为一个"没有坚实技术理由"的同步器引入额外的温度相关延迟。

**他随后用实测验证了这个假设（2022-08-28）。** 做了一块 TDC7200 转接板插在 Nucleo-G474RE 上，用 TIM2 产生间隔可编程的 START/STOP（正间隔每点测 10 万次，负间隔每点 1 万次）：

| 结果 | 说明 |
| --- | --- |
| STOP 先于或等于 START | **100% 判为溢出无效，不产生错误读数**，下一次测量不受影响 |
| 设定间隔 5.88 ns | 仍有 99.8% 有效，平均读数 6.71 ns。说明标称 12 ns 是保证值，实际门限更低；设计上仍应按 12 ns 处理 |
| 设定间隔 >= 11.76 ns | 100% 有效 |
| 单次标准差 | 随间隔近似线性增长，拟合斜率约 0.87 ps/ns；12 至 112 ns 工作区内约 13 至 75 ps |

### 4.3 实测中发现的一个坑：GPIO 输出速度

2022-09-03 作者补充：START/STOP 由 MCU 的 GPIO 产生时，**GPIO 输出速度档位明显影响 TDC 的单次标准差**。下表摘自他发布的原始数据（TIM2 运行在 160 MHz，TDC 时钟为 160 MHz 经 MCO 16 分频的 10 MHz，单位 ps）：

| 设定间隔 | 速度档 0（低） | 档 1 | 档 2（高） | 档 3（最高） |
| --- | --- | --- | --- | --- |
| 12.5 ns | 217 | 75 | 54 | 42 |
| 50 ns | 227 | 64 | 55 | 47 |
| 150 ns | 233 | 115 | 101 | 114 |
| 500 ns | 258 | 240 | 241 | 426 |
| 2000 ns | 547 | 520 | 520 | 1209 |

最低档最差，最高档在长间隔反而劣化，作者暂定用"高"档，原因尚未用示波器查明。**对 GNSSDO 本身影响不大**——在整机里 START 来自 F9T、STOP 来自 LMK，都不是 MCU 的 GPIO；但对用 MCU 产生测试信号做标定的场景是个实用提醒。

### 4.4 分辨率不是瓶颈

论坛里多人（WatchfulEye、thinkfat）指出，在环路关心的带宽内，**ZED-F9T 定时脉冲本身的噪声比 TDC7200 高几个数量级**。作者也认同，并据此放弃了功能更强但更贵的 ScioSense AS6500——用 AS6500 虽然可以省掉 MCU 定时器的粗测，但生成稳定输出脉冲仍需要一个同步到 OCXO 的 MCU 定时器，收益不大。WatchfulEye 还给了一个技巧：可以"借用"模式 2，只取时钟计数与 TIME1 的小数部分，丢掉 TIME2，避免两次测量噪声相加。

---

## 5. OCXO 调谐链路

### 5.1 电路

@fig:ca_dac_sch 图 6　按作者原理图重绘的调谐电压链路，元件值按"v1 / v2"标注

信号路径：**ADR4533（3.3 V）或 OCXO 自身 VREF → AD5542A 16 bit DAC → 二阶 Sallen-Key 有源低通（单位增益，OPA189）→ 无源 RC（100 欧 + 10 uF）→ OCXO 的 VCTL**。几个设计细节：

- **基准二选一（JP302）。** 用 OCXO 自带的 VREF 时，DAC 输出与 OCXO 内部基准成比例，基准漂移被抵消一部分；用 ADR4533 时噪声与温漂由独立的精密基准决定。
- **AD5542A 的 LDAC 接地**，数据在 CS 上升沿直接锁存，只需 SPI1 的三根线（不读回）。
- **为什么有源级后面还要一级无源 RC。** 在几 kHz 以上，C313 近似短路，输入电流经 R311 直接灌到运放输出端；运放的闭环输出阻抗随频率升高，于是有源级的衰减到某个频率后不再增加，反而以 +20 dB/十倍频回升，原理图上标注为"斜率在 3 至 4 kHz 处反转"。后面那级 159 Hz 的 RC 把这段回升压平。
- **R313 只取 100 欧。** 作者解释：12 k 欧的电阻在 300 K 时热噪声约 14 nV/根号Hz，已高于 OPA189 的输出噪声，所以第二级用小电阻大电容"宁可保守"。
- **OCXO 罩在 Hammond 1551P 塑料盒里挡气流**，罩内放 TMP117 测温。

### 5.2 两版参数与本文计算

| 参数 | v1（2022-08-05） | v2（2022-08-11） |
| --- | --- | --- |
| R311 / R312 | 13 k / 10 k | 8.2 k / 15 k |
| C313 / C314 | 20 uF / 10 uF | 2.2 uF / 1 uF |
| f0（按原理图） | **0.99 Hz** | **9.68 Hz** |
| Q | 0.70（接近巴特沃斯） | 0.71 |
| 群时延：直流 / 峰值 | 0.23 s / 0.28 s（0.62 Hz 处） | 0.024 s / 0.029 s（6.2 Hz 处） |
| 计入 DAC 内阻 6.25 k 后的 f0 与 Q | **0.81 Hz**，Q 0.67 | **7.29 Hz**，Q 0.74 |
| 计入 DAC 内阻后的群时延峰值 | 0.33 s | 0.039 s |
| 作者标注的斜率反转点 | 3 至 4 kHz | 约 10 kHz |
| 本文模型算出的反转点 | 3.2 kHz | 12.6 kHz |

@fig:ca_lpf_bode 图 7　两版调谐滤波器的幅频响应（按原理图元件值计算）

> **一个旁证：** 作者在帖子中给出 v1 的 PSpice 结果"群时延在约 0.5 Hz 处达到峰值约 0.27 s"，与本文**不计 DAC 内阻**时算出的 0.28 s @ 0.62 Hz 吻合，计入内阻后则是 0.33 s。可见作者仿真时把 DAC 当成了理想电压源（他也说明用的是"2 V 直流偏置 + 1 mV 交流"的激励源）。

### 5.3 为什么要更细的调谐分辨率

@fig:ca_tuning 图 8　DAC 一个 LSB 的频率步进在 tau 内累积出的时间误差

作者的算例：假设 OCXO 调谐范围 2 ppm 全部落在 16 bit DAC 的满量程内，一个 LSB 对应 30.5 ppt；持续 10 s 就累积 305 ps，**已经比 TDC7200 的约 50 ps 分辨率粗了 6 倍**。所以他希望在 DAC 之上再叠加 PWM 或 PAM（用 STM32G4 的定时器或 DAC 的循环 DMA）扩展有效位数——这正是 1 Hz 低通的第二个用途。

这个设计在 time-nuts 上引发了一轮讨论：

| 观点 | 提出者 | 要点 |
| --- | --- | --- |
| 滤波器时延会带来环内相移和噪声峰化 | Bob kb8tq | 控制环不分模拟数字，时延就是时延，无法"补偿掉" |
| 群时延对慢环路可忽略 | 作者 | 0.27 s 的群时延对 10 s 以上的环路时间常数可忽略；1PPS 驱动的环路时间常数本来就不可能小于 1 s；数字环可把滤波器传函和死区时间显式计入 |
| 其实几乎不用滤波 | WatchfulEye | 按窄带调频近似，VCTL 噪声引起的相噪约为 20 log10(S x Nv(f) / 2f)。以 0 至 4 V 调 +/-2 ppm 的廉价 OCXO（S = 10 Hz/V）为例，1 LSB 方波扰动在 10 Hz 偏移处约 -122 dBc/Hz，远低于廉价 OCXO 自身相噪 |
| PWM 抖动比 DAC 更便宜 | MIS42N | 用 PIC 的 10 bit PWM 逐脉冲抖动扩到 24 bit，FET 对管缓冲加无源滤波，粒度优于 1 uV |

v2（08-11）把截止频率从 1 Hz 提到 10 Hz，群时延随之降为原来的十分之一。作者没有说明改动原因，时间上紧随上述讨论。

### 5.4 本文发现的两处需要注意的地方

以下两点作者在帖子和原理图中都没有讨论，是本文根据器件数据手册推断的，**移植时应先核实**：

1. **AD5542A 的内阻会改变滤波器参数。** 它是无缓冲 R-2R 输出，内阻约 6.25 k 欧，与 R311 串联。结果是 f0 比设计值低约 18% 至 25%，群时延相应变大（见 5.2 节表格）。直流精度不受影响，因为运放同相端几乎不取电流。移植时应把 R311 减去约 6.25 k 欧，或在 DAC 后加缓冲。
2. **OPA189 的输入共模范围可能不够。** TI 数据手册给出的输入共模上限比正电源低约 2.5 V（典型值）。OPA189 用 +5 V 单电源时，同相端最高约 2.5 V；而 DAC 满量程是 3.3 V，**码值的上部约 24% 会使单位增益跟随器超出共模范围**。如果 OCXO 的实际工作点在 2.5 V 以下就不受影响——作者仿真时用的 2 V 偏置恰好在范围内，所以仿真不会暴露这个问题。本项目 v1.1 计划 HW-B 选的 OPA333、OPA192 都是输入轨到轨型，不存在此问题。

---

## 6. 控制环（推断）

@fig:ca_loop 图 9　数字锁相环的信号流（按帖子描述整理，作者未公开固件）

作者没有公开固件，下面是根据帖子能确定的部分：

| 环节 | 能确定的内容 | 来源 |
| --- | --- | --- |
| 相位比较 | GNSS 脉冲时刻与本地 OCXO 派生脉冲时刻之差，全部在 OCXO 相干时钟域内完成 | 架构本身 |
| 环路时间常数 | 作者按"大于 10 s"考虑，并认为 1PPS 驱动下小于 1 s 不现实 | time-nuts 讨论 |
| 滤波器时延 | 由数字环显式计入 | time-nuts 讨论 |
| 锯齿波修正 | 用 F9T 的 UBX-TIM-TP 中的 qErr。F9T 内部时钟据社区估计约 128 MHz，量化步长约 7.8 ns | 推断；时钟频率为 Marek 的估计，未见官方确认 |
| 差分授时 | 一台固定的 F9T 以时间模式、已测坐标运行，向移动端发送 RTCM 3 MSM7；移动端 F9T 用这些码与载波相位修正改善授时 | time-nuts 讨论 |
| IMU 用途 | v2 加了 IMU，作者未说明用途。推断用于 OCXO 加速度敏感度补偿或运动状态记录 | 推断 |
| 温度 | TMP117 放在 OCXO 罩内，可用于温度前馈 | 推断 |

### 6.1 社区指出的 ZED-F9T 风险

这些风险直接影响移动场景，作者表示要靠原型实测来回答：

- **定时指标只在固定位置模式下规定。** F9T 数据手册的 5 ns 绝对、2.5 ns 差分的脉冲精度只针对固定位置模式；移动时的运行极限是 4 g、500 m/s。作者承认移动中可能劣化，验证这一点正是做原型的目的之一。
- **能否用 RTK 修正有争议。** John Ackermann（N8UR）认为只有 F9P 能内部做 RTK，F9T 只能当基准站；作者引数据手册反驳：F9T 的差分授时功能本身就使用 RTCM 10403 中的码与载波相位修正，不需要做 RTK 定位。
- **位置误差不等于时间误差。** 作者用 F9P 双天线基线长度误差的统计（98% 小于 30 cm，约合 1 ns）来类比，Bob kb8tq 认为时间误差很可能比这个类比更差。目前双方都没有数据。
- **模块对温度、冲击、姿态敏感。** Thomas Abbott 实测：把裸模块翻转、升温 5 至 10 摄氏度、甚至用力敲桌子，脉冲都会跳几个 ns，10 至 20 s 后恢复。他判断是内部 TCXO 受扰后各个环路在重新收敛。**这对车载是直接威胁。**
- **qErr 偶发回绕。** Thomas Abbott、Marek、Bob 都观察到时间脉冲偏移修正偶尔出现约 7 ns 的"跳点"，2019 年的固件与 TIM 2.21 固件上都有人遇到，固件里必须做跳变检测。
- **不要开 SBAS。** 作者引用了 u-blox 的建议：授时应用应关闭 SBAS。

---

## 7. 输出驱动

@fig:ca_output 图 10　BUF602 输出级：源端 49.9 欧匹配，可驱动 50 欧或高阻负载

5 路输出电路完全相同：**BUF602 → 49.9 欧串联 → TVS → SMA**。2 路 10 MHz 来自 LMK 的 Y0，2 路稳定脉冲来自 MCU 的 PA9，1 路是 F9T 的 TP2 原始脉冲。

作者为什么用缓冲运放而不用 74 逻辑门，在同期的 RCB-F9T 转接板讨论中解释得很清楚：

| 理由 | 说明 |
| --- | --- |
| 上升沿 | BUF602 压摆率 8 V/ns，上升沿 < 0.5 ns；逻辑门的规格书都不给 1 ns 以下的上升时间 |
| 电源抑制 | BUF602 的 PSRR 在 1 MHz 以内 > 45 dB；逻辑门基本不标 |
| 源端匹配 | 运放输出阻抗低且确定，串 49.9 欧即成 50 欧源；逻辑门不标输出阻抗，驱动 50 欧要并联多个输出 |
| 可预期的噪声 | 附加噪声主要来自输入电压噪声 4.8 nV/根号Hz，约合 -153 dBm/Hz（50 欧），可以照数据手册算；逻辑门没有抖动指标 |
| 工程成本 | Bob kb8tq 认为分立方案更便宜；作者认为为每种信号分别验证一套方案的工程成本更高，手焊 SMA 的成本已经超过器件差价 |

作者还指出输出电平恰好符合 ITU G.703 的要求。在单独的 RCB-F9T 转接板上，-5 V 由 LM27761 电荷泵产生（驱动 5 路 50 欧负载的平均电流 < 100 mA）；主板上则由 J101 外供。

---

## 8. MCU 引脚分配

@fig:ca_pinmap 图 11　STM32G474RET6 在 v2 原理图中的引脚分配

几个值得注意的选择：

- **PF0 接 10 MHz（HSE 旁路）**，这是"MCU 与 OCXO 同源"的关键一根线。
- **PA9 输出稳定脉冲。** 它在原理图上标为 TIM2_CH3，但 PA9 同时是 HRTIM1_CHA2，可改用 HRTIM 获得约 184 ps 的边沿定位分辨率，这就是作者说的"约 200 ps 可调延迟"。
- **GNSS 脉冲进 PB11（TIM2_CH4）**，与输出脉冲共用 32 bit 的 TIM2，粗测与生成在同一个计数器上，没有跨定时器的同步问题。
- **PC13 至 PC15 一律不用。** v2 原理图特意注明：这三脚由电池域的 3 mA 电源开关供电，最高 2 MHz @ 30 pF，且不能输出电流。
- **TDC 的 INTB 加了 4.7 k 上拉**（v2 的 R231）。作者在 08-07 读 thinkfat 的帖子时发现 v1 漏了这个上拉——原理图注释"Only INT is open-drain"。

---

## 9. PCB 布局

@fig:ca_board 图 12　v2 版图的器件分区（按作者版图 PDF 量取，示意）

- 板框 100 x 100 mm（含 SMA 底座），可直接装进常见的铝制 PCB 外壳。
- **OCXO 在左上角，罩在 Hammond 1551P 塑料盒里**，TMP117 也在罩内，用于在无外壳使用时挡住气流。
- **RCB-F9T 用 2x4 排针叠插在右上方**，MCU 与 TDC7200 就在它下面紧挨着，GNSS 脉冲走线最短。
- 基准、DAC、有源滤波夹在 OCXO 罩与 MCU 之间；LMK1C1103 紧贴 OCXO 输出脚。
- 5 路 SMA 全部排在下沿，BUF602 驱动级一字排开在其上方。
- IMU 子板放在板中央（v2 新增）。

---

## 10. 两版原理图差异

| 项目 | v1（2022-08-05） | v2（各页 08-09 至 08-11） |
| --- | --- | --- |
| 有源低通 | 13 k / 10 k / 20 uF / 10 uF，约 1 Hz，反转 3 至 4 kHz | 8.2 k / 15 k / 2.2 uF / 1 uF，约 10 Hz，反转约 10 kHz |
| LMK 输出分配 | Y0 到 MCU，Y1 到 TDC，Y2 到输出 | Y0 到输出，Y1 经 R331 到 MCU，Y2 经 R332 到 TDC |
| TDC INTB | **无上拉**（作者事后发现） | R231 4.7 k 上拉 |
| TDC 供电 | 直接接 +3.3 V | 经 FB231 600 欧磁珠 |
| TDC ENABLE / INTB 引脚 | PC8 / PC9 | PC7 / PC6 |
| TMP117 | I2C4（PC6 / PC7），上拉 5 k | I2C3（PC8 / PC9），上拉 4.7 k |
| IMU | 无 | IIM-42652 子板，SPI3 + TIM4_CH1 时钟 |
| 指示灯 | 无 | PA0 至 PA2 接绿 / 黄 / 红 LED |
| SWD | 无保护 | 加 SMF05C ESD 阵列 |
| JP301（基准供电跳线） | 在磁珠与 ADR4533 输入之间 | 移到磁珠与 +5 V 之间 |
| 安装孔 | 4 个 | 8 个 |

---

## 11. 作者在讨论中回应过的其他问题

| 问题 | 提出者 | 作者回应 |
| --- | --- | --- |
| OCXO 的加速度敏感度 | Bob kb8tq | 原型先用一颗容易买到的普通 OCXO；下一版换最坏轴 < 0.2 ppb/g 的型号。他找到的最好约 0.05 ppb/g/轴，但很贵或体积大、不是贴片 |
| MCU 输出抖动 | WatchfulEye（在 SAMD51 上测到 PLL 抖动约 5 ns） | STM32G474 数据手册给出的 PLL 抖动约正负 25 ps，且 MCU 与 TDC 同源，预计影响可忽略。未实测 |
| 加气压传感器 | thinkfat | OCXO 是密封外壳，应对气压不敏感，暂不加 |
| 怎样测移动中的性能 | Theboel | 之前测 LC_XO 的做法：同一辆车里放多台 GPSDO，各用一根朝向不同的天线，行驶中直接比对各自输出。跨车辆比对需要视距无线链路，太复杂 |

---

## 12. 对本项目的借鉴

| Andrich 的做法 | 本项目现状 | 建议 | 对应 v1.1 计划 |
| --- | --- | --- | --- |
| 10 MHz 进 OSC_IN，MCU 与 OCXO 同源 | 10 MHz 只进 PA0，HSE 是独立晶振 | **照做**，单次分辨率从 100 ns 提到 5.9 ns，只加一条走线 | HW-H |
| TDC7200 的 STOP、CLOCK 直接接 10 MHz，靠周期折叠避开死区 | 无 TDC | 若将来上 TDC，可直接沿用这种无同步器接法，作者已实测验证 | HW-J |
| 粗测只需正负 50 ns，TIM2 与 TDC 组合 | 无 | 写 TIC 固件时按 4.1 节的公式组合，粗测不用精细标定 | M3 |
| DAC 后接有源二阶低通 + 无源 RC | PWM + 两级无源 RC，源阻抗 40 k 欧 | 借鉴结构，但**运放选输入轨到轨型**，并把 PWM 或 DAC 的源阻抗算进滤波器 | HW-B |
| 截止频率从 1 Hz 改到 10 Hz | 0.8 Hz | 本项目若在 16 bit PWM 上做抖动扩位，需要足够低的截止频率滤掉抖动；不做扩位时可参考 v2 适当提高 | HW-B |
| LMK1C1103 三路同相分配，无 74 逻辑 | 已有 LMK1C1102，但输入幅度与 VDD 有问题 | 先修正 v1.1 已列出的两个问题 | v1.1 第 2 节 |
| OCXO 罩盒挡气流 + 罩内测温 | 热设计尚未做 | 可直接借鉴，便携场景更需要 | HW-L |
| qErr 修正并做跳变检测 | 固件为空 | 实现 M4 时加入回绕检测 | M4 |

**不建议照搬的部分：**

- **供电方式。** 他的板子需要外部 +5 V、+3.3 V、-5 V 三路电源，没有任何板载稳压，OCXO 预热峰值 1.1 A @ 3.3 V。本项目是电池便携方案，必须自己做电源。
- **BUF602 + +/-5 V。** 需要负电源，功耗也不小。本项目若只需驱动高阻负载，没必要上。
- **把 ZED-F9T 当作移动授时一定可行。** 社区对此有实质性质疑（第 6.1 节），作者自己也没有数据。

---

## 13. 参考来源

```
Original post, time-nuts 2022-08-05 (v1 schematic STM32G4_GNSSDO.pdf attached)
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-August/106228.html
Author replies on time-nuts (F9T specs, differential timing, LPF group delay,
  0.05 ppb/g OCXO, F9P baseline error, updated schematic)
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-August/106235.html
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-August/106246.html
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-August/106249.html
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-August/106250.html
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-August/106265.html
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-August/106277.html
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-August/106290.html
Community feedback on time-nuts (Bob kb8tq, John Ackermann, Thomas Abbott, Marek)
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-August/106236.html
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-August/106237.html
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-August/106257.html
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-August/106267.html
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-August/106311.html
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-August/106325.html
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-August/106329.html
EEVblog thread (v2 schematic + layout, TDC7200 dead-time test, GPIO speed test)
  https://www.eevblog.com/forum/projects/gpsdognssdo-stm32g4-u-blox-zed-f9t-tdc7200/
  https://www.eevblog.com/forum/projects/gpsdognssdo-stm32g4-u-blox-zed-f9t-tdc7200/25/
RCB-F9T adapter board thread (why BUF602, LM27761 negative rail, G.703 levels)
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-August/106347.html
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-August/106375.html
  https://febo.com/pipermail/time-nuts_lists.febo.com/2022-August/106387.html
thinkfat: DIY GPSDO with STM32 + TDC7200 (the design that inspired this one)
  https://www.eevblog.com/forum/projects/diy-gpsdo-project-w-stm32-tdc7200/
Part data used in this document
  OPA189 datasheet (input common-mode headroom)
    https://www.ti.com/product/OPA189
  AD5542A output impedance (CN-0169)
    https://www.analog.com/CN0169
  STM32G474 pin map: PA9 = HRTIM1_CHA2
    https://docs.embassy.dev/embassy-stm32/git/stm32g474re/hrtim/
    trait.HRTimerPin.html
```
