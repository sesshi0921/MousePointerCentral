"""Tunable parameters for screen-perception pipeline (§5.6).

All values are *provisional* – adjust after fixture-based evaluation (§10).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class ScreenPerceptConfig:
    # -- Preprocessing (§5.2) ------------------------------------------------
    upscale_factor: float = 2.0               # 暫定・要 fixture 調整
    sharpen: bool = False                     # 既定 OFF – フラグ化
    bilateral_d: int = 9                      # 暫定・要 fixture 調整
    bilateral_sigma_color: float = 75.0       # 暫定・要 fixture 調整
    bilateral_sigma_space: float = 75.0       # 暫定・要 fixture 調整

    # -- Contour detection ---------------------------------------------------
    contour_min_area: int = 200               # 暫定・要 fixture 調整
    contour_max_area: int = 500_000           # 暫定・要 fixture 調整
    contour_approx_epsilon: float = 0.02      # 暫定・要 fixture 調整

    # -- MSER detection ------------------------------------------------------
    mser_delta: int = 5                       # 暫定・要 fixture 調整
    mser_min_area: int = 60                   # 暫定・要 fixture 調整
    mser_max_area: int = 14_400               # 暫定・要 fixture 調整

    # -- Color segmentation --------------------------------------------------
    colorseg_k: int = 8                       # k-means clusters, 暫定
    colorseg_min_area: int = 300              # 暫定・要 fixture 調整

    # -- OCR -----------------------------------------------------------------
    ocr_backend: str = "tesseract"            # tesseract | easyocr | paddleocr
    ocr_lang: str = "eng+jpn"                 # 暫定
    ocr_conf_threshold: float = 0.4           # 暫定・要 fixture 調整

    # -- Ensemble (§5.4.1) ---------------------------------------------------
    ensemble_iou_threshold: float = 0.5       # 暫定・要 fixture 調整
    ensemble_min_votes: int = 1               # 暫定・要 fixture 調整
    classify_min_conf: float = 0.6            # 暫定・要 fixture 調整

    # -- Refine (§5.5) -------------------------------------------------------
    refine_snap_radius: int = 8               # 暫定・要 fixture 調整


PERCEPT_CONFIG = ScreenPerceptConfig()
