"""Install HW3 dependencies with the best available PyTorch accelerator build.

The installer deliberately keeps PyTorch out of requirements.txt because its
wheel index depends on the host hardware.  Set PYTORCH_ACCELERATOR to one of
auto, cuda, rocm, xpu, mps, or cpu to override detection.  Advanced users may
also set PYTORCH_INDEX_URL to an official/custom wheel index URL.
"""

from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
PYTORCH_PACKAGES = ("torch", "torchvision")
VALID_ACCELERATORS = {"auto", "cuda", "rocm", "xpu", "mps", "cpu"}


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print(f"+ {' '.join(command)}", flush=True)
    return subprocess.run(command, check=check, text=True)


def command_output(command: list[str]) -> str:
    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout if result.returncode == 0 else ""


def nvidia_cuda_version() -> tuple[bool, tuple[int, int] | None]:
    if not shutil.which("nvidia-smi"):
        return False, None

    output = command_output(["nvidia-smi"])
    if not output:
        return False, None

    # Newer Windows drivers label this field "CUDA UMD Version" while older
    # Windows/Linux drivers use "CUDA Version".
    match = re.search(r"CUDA(?: UMD)? Version:\s*(\d+)\.(\d+)", output)
    version = (int(match.group(1)), int(match.group(2))) if match else None
    return True, version


def has_rocm_runtime() -> bool:
    if platform.system() != "Linux":
        return False
    for tool in ("rocminfo", "rocm-smi"):
        executable = shutil.which(tool)
        if executable and command_output([executable]):
            return True
    return Path("/dev/kfd").exists()


def gpu_names() -> str:
    system = platform.system()
    if system == "Windows":
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if powershell:
            return command_output(
                [
                    powershell,
                    "-NoProfile",
                    "-Command",
                    "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name",
                ]
            )
    elif system == "Linux" and shutil.which("lspci"):
        return command_output(["lspci"])
    return ""


def has_supported_intel_gpu() -> bool:
    names = gpu_names()
    if not names:
        return False
    # Official XPU wheels currently target Arc, Core Ultra Arc, and Intel data
    # center GPUs. Avoid installing the much larger XPU build for older iGPUs.
    return bool(
        re.search(
            r"Intel.*(?:Arc|Data Center GPU|GPU Max|GPU Flex)",
            names,
            flags=re.IGNORECASE,
        )
    )


def detect_accelerator() -> tuple[str, tuple[int, int] | None]:
    requested = os.environ.get("PYTORCH_ACCELERATOR", "auto").strip().lower()
    if requested not in VALID_ACCELERATORS:
        choices = ", ".join(sorted(VALID_ACCELERATORS))
        raise SystemExit(f"PYTORCH_ACCELERATOR must be one of: {choices}")

    has_nvidia, cuda_version = nvidia_cuda_version()
    if requested != "auto":
        return requested, cuda_version

    if platform.system() == "Darwin":
        return "mps", None
    if has_nvidia:
        return "cuda", cuda_version
    if has_rocm_runtime():
        return "rocm", None
    if has_supported_intel_gpu():
        return "xpu", None
    return "cpu", None


def cuda_indexes(driver_cuda: tuple[int, int] | None) -> list[str]:
    # Try only runtimes that the NVIDIA driver advertises as compatible. Older
    # cu126/cu118 builds also preserve support for more legacy GPU generations.
    choices = [
        ((13, 2), "cu132"),
        ((12, 6), "cu126"),
        ((11, 8), "cu118"),
    ]
    if driver_cuda is None:
        tags = ["cu126", "cu118"]
    else:
        tags = [tag for minimum, tag in choices if driver_cuda >= minimum]
        if not tags:
            tags = ["cu118"]
    return [f"https://download.pytorch.org/whl/{tag}" for tag in tags]


def candidate_indexes(
    accelerator: str, driver_cuda: tuple[int, int] | None
) -> list[str | None]:
    override = os.environ.get("PYTORCH_INDEX_URL", "").strip()
    if override:
        return [override]
    if accelerator == "cuda":
        return cuda_indexes(driver_cuda)
    if accelerator == "rocm":
        return [
            "https://download.pytorch.org/whl/rocm7.14",
            "https://download.pytorch.org/whl/rocm7.2",
            "https://download.pytorch.org/whl/rocm6.3",
        ]
    if accelerator == "xpu":
        return ["https://download.pytorch.org/whl/xpu"]
    if accelerator == "cpu":
        return ["https://download.pytorch.org/whl/cpu"]
    # The standard macOS wheels contain both MPS and CPU support.
    return [None]


def install_pytorch(index_url: str | None) -> bool:
    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        "--force-reinstall",
        *PYTORCH_PACKAGES,
    ]
    if index_url:
        command.extend(["--index-url", index_url])
    return run(command, check=False).returncode == 0


def backend_test(accelerator: str) -> tuple[bool, str]:
    test_code = r"""
import sys
import torch

backend = sys.argv[1]
if backend == "cuda":
    available = torch.cuda.is_available() and torch.version.cuda is not None
    device = torch.device("cuda")
elif backend == "rocm":
    available = torch.cuda.is_available() and torch.version.hip is not None
    device = torch.device("cuda")
elif backend == "xpu":
    available = hasattr(torch, "xpu") and torch.xpu.is_available()
    device = torch.device("xpu")
elif backend == "mps":
    available = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
    device = torch.device("mps")
else:
    available = True
    device = torch.device("cpu")

if not available:
    raise SystemExit(2)

x = torch.randn(64, 64, device=device)
_ = (x @ x).mean().item()
print(f"PyTorch {torch.__version__}: {device.type} tensor test passed")
"""
    result = subprocess.run(
        [sys.executable, "-c", test_code, accelerator],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return result.returncode == 0, result.stdout.strip()


def install_base_requirements() -> None:
    run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            str(ROOT_DIR / "requirements.txt"),
        ]
    )


def main() -> None:
    accelerator, driver_cuda = detect_accelerator()
    print(f"Requested/detected PyTorch backend: {accelerator}")
    if driver_cuda:
        print(f"NVIDIA driver reports CUDA compatibility: {driver_cuda[0]}.{driver_cuda[1]}")

    selected = None
    passed, details = backend_test(accelerator)
    if passed:
        print(f"Existing installation is already usable: {details}")
        selected = accelerator

    if selected is None:
        for index_url in candidate_indexes(accelerator, driver_cuda):
            source = index_url or "the default PyPI index"
            print(f"\nTrying PyTorch for {accelerator} from {source}")
            if not install_pytorch(index_url):
                print(f"[WARN] Installation from {source} failed; trying the next option.")
                continue
            passed, details = backend_test(accelerator)
            if details:
                print(details)
            if passed:
                selected = accelerator
                break
            print(f"[WARN] The {accelerator} build installed, but its device test failed.")

    if selected is None and accelerator != "cpu":
        print("\nNo usable accelerator build was found. Falling back to CPU PyTorch.")
        # macOS uses one standard wheel for both MPS and CPU execution.
        cpu_index = (
            None
            if platform.system() == "Darwin"
            else "https://download.pytorch.org/whl/cpu"
        )
        if not install_pytorch(cpu_index):
            raise SystemExit("CPU PyTorch installation failed.")
        passed, details = backend_test("cpu")
        if details:
            print(details)
        if not passed:
            raise SystemExit("CPU PyTorch installed, but its tensor test failed.")
        selected = "cpu"

    if selected is None:
        raise SystemExit("No working PyTorch installation could be installed.")

    print("\nInstalling the remaining homework packages.")
    install_base_requirements()
    print(f"\nDependency installation complete. Selected backend: {selected}")


if __name__ == "__main__":
    main()
