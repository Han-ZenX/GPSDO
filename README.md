# 🛰️ GPSDO - GPS disciplined Oscillator (GPS  disciplining frequency standard)

<div align="center">

**A highly integrated, portable and high-precision GPSDO**  
一款高度集成、便携式、高精度的 GPS discipling frequency standard

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Build](https://github.com/Han-ZenX/GPSDO/actions/workflows/build.yml/badge.svg)](ci/workflows/build.yml)
[![CMake](https://img.shields.io/badge/build-CMake-lightgrey)](https://cmake.org/)
[![STM32](https://img.shields.io/badge/MCU-STM32F407-yellow)](https://www.st.com/en/microcontrollers-microprocessors/stm32f407.html)

</div>

---

## 📖 概述 (Overview)

GPSDO (GPS Disciplined Oscillator) 是一种利用 GPS 卫星信号来校准高精度晶振频率的设备。本项目采用模块化设计，支持长期持续迭代，具备：

- ✨ **高稳定性**：PPB 级频率精度
- 🔧 **便携设计**：低功耗、一体化结构
- 🚀 **易于扩展**：分层架构，支持功能升级
- 💻 **开放源码**：完整固件 + 硬件设计开源

---

## 🎯 主要特性

| 特性 | 说明 |
|------|------|
| **精度** | PPB（十亿分之一）级别的频率稳定度 |
| **温度补偿** | 内置高精度温度传感器，实时补偿 |
| **数据记录**：支持 SD 卡存储历史数据 |
| **通信接口**：UART/SPI/I2C 多种通信方式 |
| **显示模块**：可扩展 OLED/LCD 显示屏 |
| **电源管理**：宽电压输入，锂电池供电 |
| **外壳设计**：可 3D 打印或 CNC 加工 |

---

## 🏗️ 系统架构

项目采用 **Monorepo + 四层分层架构**，各层级职责清晰：

```
GPSDO/
├── firmware/          # 嵌入式固件 (STM32G431)
│   ├── src/
│   │   ├── app/       # 应用层：业务逻辑、算法、UI
│   │   ├── hal/       # 硬件抽象层：GPIO、时钟、中断
│   │   ├── drivers/   # 驱动层：SPI、I2C、UART 等外设
│   │   └── services/  # 服务层：通信协议、数据存储
│   └── boards/        # 板级配置 (不同硬件版本)
│
├── hardware/          # KiCad 硬件设计
│   ├── schematic/v1.0/# 原理图
│   ├── pcb/v1.0/      # PCB 布局
│   ├── bom/           # BOM 物料清单
│   └── pinout/        # 引脚分配表
│
├── docs/              # 项目文档
│   ├── architecture/  # 系统架构说明
│   ├── user-guide/    # 用户使用手册
│   └── api/           # API 接口文档
│
├── software/          # 配套软件（开发中）
│   ├── desktop/       # PC 桌面应用
│   └── mobile/        # 移动端 App
│
├── tests/             # 测试套件
├── tools/             # 构建脚本与工具
└── ci/                # CI/CD 流水线配置
```

### 分层架构优势

| 层级 | 职责 | 独立性 |
|------|------|--------|
| **Application** | 业务逻辑、状态机 | 更换 MCU 零修改 |
| **HAL** | GPIO、时钟、中断 | 换 MCU 时整体替换 |
| **Drivers** | SPI/I2C/UART 通信 | 随外设更换更新 |
| **Services** | 通信、存储、OTA | 可独立升级 |

👉 **核心原则**：业务逻辑不直接访问寄存器，确保代码可移植性。

---

## 🛠️ 硬件规格 (Hardware Specs)

### 主控芯片
- **MCU**: STM32F407ZGT6 (Cortex-M4F, 168MHz)
- **Flash**: 1MB
- **RAM**: 112KB

### GPS 模块
- **芯片**: u-blox NEO-M8N / F10
- **通道数**: 72 通道
- **定位精度**: 水平 < 2.5m CEP

### ADC 采样
- **芯片**: ADS1115 / ADS1258
- **分辨率**: 16/24-bit
- **采样率**: 上行至 8SPS

### 辅助传感器
- **温度传感器**: TMP117 (-40~+125°C, ±0.1°C)
- **RTC**: PCF8563 (带电池备份)

### 接口
- UART: 调试串口 / 通信接口
- SPI: ADC / 显示屏
- I2C: 传感器 / EEPROM
- GPIO: LED / 按键 / 扩展

---

## 📦 构建指南 (Build Instructions)

### 环境要求

- CMake ≥ 3.16
- ARM GCC Toolchain (`arm-none-eabi-gcc`)
- Python 3.8+ (用于自动化脚本)

### 快速开始

#### Windows (PowerShell)
```powershell
# Debug 构建 (默认板级)
cd firmware
cmake -B build -DBOARD=default
cmake --build build

# Release 构建
cmake -B build -DBOARD=default -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

#### Linux/macOS
```bash
# 使用自动化脚本 (推荐)
python tools/scripts/build.py --board=default

# 或使用 CMake 命令
cmake -B build -DBOARD=default && cmake --build build
```

### 多板级支持

添加新的硬件版本：
```bash
# 复制默认板级配置
cp -r firmware/boards/default firmware/boards/v2.0

# 编辑引脚映射
nano firmware/boards/v2.0/board_config.h

# 编译新版本
cmake -B build -DBOARD=v2.0
```

---

## 🧪 测试运行

### 单元测试 (Host-based)
```bash
# 在 PC 上运行纯软件测试
python tools/scripts/build.py --test unit
```

### 集成测试
```bash
# 模块间交互测试
python tools/scripts/build.py --test integration
```

### HWT (Hardware-in-the-Loop)
```bash
# 硬件在环测试
python tools/scripts/build.py --test hwt
```

---

## 📂 目录结构详解

### `firmware/src/`
| 目录 | 说明 |
|------|------|
| `app/` | 应用层：GPS 数据处理、频偏计算、状态机 |
| `hal/` | HAL 层：STM32 寄存器操作封装 |
| `drivers/` | 驱动层：ADS1258、u-blox、TMP117 等 |
| `services/` | 服务层：NMEA 解析、Flash 日志、UART 协议 |

### `hardware/schematic/v1.0/`
KiCad 原理图工程文件：
- `GPSDO.kicad_sch` - 原理图
- `GPSDO.kicad_pcb` - PCB 布局
- `fp-lib-table` - 封装库

---

## 🔌 通信协议 (Communication Protocol)

### UART 协议格式
```
波特率：115200
数据位：8
停止位：1
校验位：无
流控：无
```

### 指令集示例
```text
AT+GPS?       → 查询 GPS 状态
AT+TEMP?      → 读取温度值
AT+ALIGN      → 手动校准
AT+LOG START  → 开始记录数据
AT+LOG STOP   → 停止记录
```

详细协议文档：`docs/api/communication.md`

---

## 🚀 开发路线图

| 阶段 | 计划 | 状态 |
|------|------|------|
| **v1.0** | 基础版 - 核心功能实现 | ✅ 完成 |
| **v1.1** | 优化算法 - 提升精度 | 🔄 进行中 |
| **v1.2** | 增加 LCD 显示 | 📋 规划中 |
| **v2.0** | 蓝牙/Wi-Fi 远程监控 | 📋 未来计划 |
| **v3.0** | 云端数据同步 | 📋 概念验证 |

---

## 📄 许可证

本项目采用 **[MIT License](LICENSE)** 开源协议

允许：
- ✅ 自由商用
- ✅ 修改代码
- ✅ 分发源码
- ✅ 私有修改

要求：
- ⚠️ 保留版权声明
- ⚠️ 注明原始作者

---

## 👥 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发流程
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

### 编码规范
- C 代码遵循 [Google C Style Guide](https://google.github.io/styleguide/cguide.html)
- 函数注释使用 Doxygen 格式
- 提交信息符合 [Conventional Commits](https://www.conventionalcommits.org/)

---

## 📞 联系方式

- **作者**: Han-ZenX
- **项目主页**: https://github.com/Han-ZenX/GPSDO
- **问题反馈**: [GitHub Issues](https://github.com/Han-ZenX/GPSDO/issues)

---

## 🙏 致谢

本项目参考了以下优秀开源项目：

- **ESP-IDF** - 组件化架构设计
- **Zephyr RTOS** - 板级抽象层模式
- **FreeRTOS** - 任务调度机制
- **RIOT-OS** - 驱动分层设计

---

## 📊 统计信息

```
语言分布:
├── C         54.8%
├── CMake     21.6%
└── Python    23.6%
```

---

<div align="center">

**Made with ❤️ for Precision Timing**

⭐ Star 本仓库以支持项目开发！

</div>
