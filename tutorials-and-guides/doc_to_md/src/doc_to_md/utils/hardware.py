"""Helpers for detecting local accelerator capabilities and configuring engines."""
from __future__ import annotations

import os
from functools import lru_cache


@lru_cache(maxsize=1)
def detect_torch_device() -> str:
    """Return 'cuda:0', 'mps', or 'cpu' based on availability."""
    torch = _safe_import_torch()
    if torch is None:
        return "cpu"
    try:  # pragma: no cover - hardware specific
        if torch.cuda.is_available():
            idx = torch.cuda.current_device()
            return f"cuda:{idx}"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
    except Exception:  # noqa: BLE001 - default to cpu
        return "cpu"
    return "cpu"


@lru_cache(maxsize=1)
def has_cuda_support() -> bool:
    """Return True if CUDA is usable via torch (preferred) or paddle fallback."""
    if detect_torch_device().startswith("cuda"):
        return True
    return paddle_supports_cuda()


@lru_cache(maxsize=1)
def paddle_supports_cuda() -> bool:
    """Return True if PaddlePaddle was compiled with CUDA."""
    try:
        import paddle  # type: ignore

        return bool(paddle.device.is_compiled_with_cuda())
    except Exception:  # noqa: BLE001
        return False


def ensure_docling_accelerator_env() -> None:
    """Set Docling accelerator env vars based on detected hardware."""
    device = detect_torch_device()
    if device == "cpu":
        return
    os.environ.setdefault("DOCLING_ACCELERATOR_DEVICE", device)


def ensure_marker_accelerator_env() -> None:
    """Set Marker env vars so Surya/torch leverage accelerators."""
    device = detect_torch_device()
    if device == "cpu":
        return
    # Marker expects generic device identifiers (cuda/mps)
    norm_device = "cuda" if device.startswith("cuda") else device
    os.environ.setdefault("TORCH_DEVICE", norm_device)


def ensure_mineru_accelerator_env() -> None:
    """Configure MinerU device mode and VRAM budget."""
    device = detect_torch_device()
    if device.startswith("cuda"):
        env_device = "cuda"
    elif device == "mps":
        env_device = "mps"
    else:
        env_device = "cpu"
    os.environ.setdefault("MINERU_DEVICE_MODE", env_device)
    if env_device == "cuda":
        vram = _estimate_cuda_vram_gb()
        if vram:
            os.environ.setdefault("MINERU_VIRTUAL_VRAM_SIZE", str(vram))


def _estimate_cuda_vram_gb() -> int | None:
    torch = _safe_import_torch()
    if not torch:
        return None
    try:  # pragma: no cover - hardware specific
        props = torch.cuda.get_device_properties(torch.cuda.current_device())
        return max(1, round(props.total_memory / (1024**3)))
    except Exception:  # noqa: BLE001
        return None


def _safe_import_torch():
    try:
        import torch  # type: ignore

        return torch
    except Exception:  # noqa: BLE001
        return None
