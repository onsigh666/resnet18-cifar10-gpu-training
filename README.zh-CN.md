# HW4 ：ResNet-18 在 CIFAR-10 上的优化



## 1. 作业目标

本次作业将研究深度神经网络训练过程中的优化。目标是在 **CIFAR-10 训练集上训练 ResNet-18 模型**，并**尽可能快地使训练准确率超过 99%**。本次作业的重点是**优化与训练效率**，而非泛化能力。因此，**本次作业不评估测试集性能**。 我们提供了一份初始 Jupyter Notebook， 要求你在**该 Notebook** 中完成所有实验，并保留完整输出，供助教检查。

## 2. 本次作业的文件

```text
HW3/
├── README.md
├── homework_resnet18_cifar10.ipynb
├── requirements.txt
├── setup/
│   ├── setup_linux.sh
│   ├── setup_windows.ps1
│   └── setup_macos.sh
└── scripts/
    ├── install_dependencies.py
    └── check_environment.py
```

- `README.md`：作业说明与要求。
- `homework_resnet18_cifar10.ipynb`：包含初始代码，也是**唯一允许编写和运行实验的文件**。
- `requirements.txt`：与硬件无关的 Python 依赖包列表。PyTorch 会单独安装，以确保安装的构建版本与可用的加速设备匹配。
- `setup/`：适用于 Linux、Windows 和 macOS 的一键环境配置脚本。
- `scripts/install_dependencies.py`：检测可用的加速设备，安装匹配的 PyTorch 构建版本，并在必要时回退到 CPU。
- `scripts/check_environment.py`：检查 Python、PyTorch 及可用的计算设备是否正常工作。

## 3. 优化目标

你的训练流程应同时满足以下两个目标：

1. 使**训练准确率超过 99%**。
2. **尽可能快地**达到这一目标。

基线实验采用以下设置：

- SGD（随机梯度下降）；
- 固定学习率；
- 与其他实验使用相同的机器和计算设备。

主要比较指标是**相对于你自己的 SGD 基线的实际耗时（wall-clock time）**。由于同学们可能使用不同的 NVIDIA GPU、Apple Silicon 设备或 CPU，因此不应直接比较不同同学的绝对训练时间。

## 4. 代码要求

**所有实验都必须在 `homework_resnet18_cifar10.ipynb` 中编写并运行。**

提交前，请完成以下事项：

1. 运行 Notebook，并保留相关输出，使其可见。
2. **不要**清除输出。
3. 确保重要的训练日志、曲线和最终结果都已保存在 Notebook 中。
4. 确保 Notebook 可以从上到下顺畅阅读，且主要实验设置清晰易辨。

保留输出非常重要，因为助教会直接检查 Notebook。

## 5. 环境配置

请选择与你的操作系统对应的配置脚本。

每个配置脚本都会按照以下优先顺序，自动安装最合适且可用的 PyTorch 构建版本：

- NVIDIA GPU：CUDA；
- Linux 上配有可正常工作的 ROCm 运行时的 AMD GPU：ROCm；
- 受支持的 Intel Arc GPU 或数据中心 GPU：XPU；
- macOS 上的 Apple GPU：MPS；
- 没有受支持的加速设备，或加速设备相关安装失败、设备测试失败时：CPU。

### Linux

在 `HW3` 目录下运行：

```bash
bash setup/setup_linux.sh
```

然后激活环境：

```bash
source .venv/bin/activate
```

### Windows

在 `HW3` 目录下打开 PowerShell，并运行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup\setup_windows.ps1
```

然后激活环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

### macOS

在 `HW3` 目录下运行：

```bash
bash setup/setup_macos.sh
```

然后激活环境：

```bash
source .venv/bin/activate
```

### 检查环境

激活环境后，运行：

```bash
python scripts/check_environment.py
```

脚本将报告以下信息：

- Python 版本；
- PyTorch 版本；
- Torchvision 版本；
- CUDA 是否可用；
- AMD ROCm 或 Intel XPU 是否可用；
- Apple MPS 是否可用；
- 所选的计算设备；
- 是否能在该设备上成功执行简单的张量运算。

如果脚本运行结束时显示 `Environment check passed`（环境检查通过），则说明基本环境已准备就绪。

## 6. AI 编程助手的使用

欢迎并鼓励你使用 Claude Code、Codex 或 Cursor 等 AI 工具辅助完成作业。不过，应将 AI 视为**编程与讨论助手**，而不能用它代替自己的验证和推理。

运行 AI 生成的代码之前，应仔细检查。尤其要确认：

- 使用的数据集是否正确；
- 训练准确率的计算是否正确；
- 优化器和超参数是否符合预定的实验设置；
- 计时方式是否一致；
- 不同方法是否在具有可比性的条件下进行比较；
- 报告中的结果是否确实来自实际运行的实验。

不要将仅由 AI 系统预测或生成的结果作为实验结果报告。

## 7. 实验报告

请提交一份简短报告，说明你的实验与结论。 报告简洁完整即可，应包含以下内容：

### 实验设置

- 硬件／计算设备；
- 基线优化器及其超参数；
- 你测试过的其他优化方法。

### 实验结果

请列出主要测量结果，例如：

- 达到 99% 训练准确率所需的时间；
- 相对于你自己的 SGD 基线的加速比；
- 最终训练准确率；
- 有代表性的训练曲线。

与尝试大量配置相比，**推理和实验验证的质量**更重要。

## 8. 提交要求

请提交一份zip压缩包，包括以下两项：

1. **`homework_resnet18_cifar10.ipynb`**
   - 包含最终代码；
   - 包含完整的相关输出；
   - 包含训练曲线和报告中列出的实验结果。

2. **一份简短的实验报告**，格式为 .pdf。

**不需要**提交虚拟环境、数据集文件、安装脚本或额外生成的代码。
