import platform
import sys


def main():
    print("=" * 60)
    print("HW3 Environment Check")
    print("=" * 60)

    print(f"Operating system : {platform.platform()}")
    print(f"Python executable: {sys.executable}")
    print(f"Python version   : {sys.version.split()[0]}")

    try:
        import torch
        import torchvision
        import numpy as np
        import matplotlib
    except Exception as exc:
        print("\n[FAIL] A required package could not be imported.")
        print(f"Reason: {exc}")
        raise SystemExit(1)

    print(f"PyTorch version  : {torch.__version__}")
    print(f"Torchvision      : {torchvision.__version__}")
    print(f"NumPy            : {np.__version__}")
    print(f"Matplotlib       : {matplotlib.__version__}")

    cuda_available = torch.cuda.is_available()
    xpu_available = bool(
        hasattr(torch, "xpu") and torch.xpu.is_available()
    )
    mps_available = bool(
        hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
    )

    accelerator_name = "ROCm" if getattr(torch.version, "hip", None) else "CUDA"
    print(f"{accelerator_name + ' available':<17}: {cuda_available}")
    print(f"XPU available    : {xpu_available}")
    print(f"MPS available    : {mps_available}")

    if cuda_available:
        device = torch.device("cuda")
        print(f"GPU device count : {torch.cuda.device_count()}")
        print(f"Selected GPU     : {torch.cuda.get_device_name(0)}")
        if accelerator_name == "ROCm":
            print(f"ROCm/HIP runtime : {torch.version.hip}")
        else:
            print(f"CUDA runtime     : {torch.version.cuda}")
    elif xpu_available:
        device = torch.device("xpu")
        print(f"XPU device count : {torch.xpu.device_count()}")
        print(f"Selected GPU     : {torch.xpu.get_device_name(0)}")
    elif mps_available:
        device = torch.device("mps")
        print("Selected device  : Apple MPS")
    else:
        device = torch.device("cpu")
        print("Selected device  : CPU")

    try:
        x = torch.randn(512, 512, device=device)
        y = torch.randn(512, 512, device=device)
        z = x @ y

        # Force completion before reporting success where synchronization is supported.
        if device.type == "cuda":
            torch.cuda.synchronize()
        elif device.type == "xpu":
            torch.xpu.synchronize()
        elif device.type == "mps" and hasattr(torch, "mps"):
            torch.mps.synchronize()

        value = z.mean().item()
        print(f"Tensor test      : PASS (mean={value:.6f})")
    except Exception as exc:
        print("\n[FAIL] PyTorch was imported, but the tensor test failed.")
        print(f"Device: {device}")
        print(f"Reason: {exc}")
        raise SystemExit(1)

    print("\nEnvironment check passed.")
    print("You can now open homework_resnet18_cifar10.ipynb and run the experiments.")


if __name__ == "__main__":
    main()
