"""Candidate ensemble – merge, de-duplicate, classify (§5.4.1).

Pipeline stages:
1. Collect candidates from all detectors.
2. Merge overlapping candidates (IoU threshold).
3. Vote on merged candidates (source count).
4. Classify – minimal rule-based, ambiguous → ``to_vision=true``.
5. Sort by confidence descending.
"""

from __future__ import annotations

from typing import Any

from .config import PERCEPT_CONFIG
from .coords import CoordSpace


# ------------------------------------------------------------------
# IoU helpers
# ------------------------------------------------------------------

def _iou(a: list[int], b: list[int]) -> float:
    """Intersection-over-Union for two [x1,y1,x2,y2] boxes."""
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area_a = max(0, a[2] - a[0]) * max(0, a[3] - a[1])
    area_b = max(0, b[2] - b[0]) * max(0, b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def _anchor_box(c: dict[str, Any]) -> list[int]:
    """Return the first anchor box (or synthesise from click_target)."""
    if c.get("anchors") and c["anchors"][0]:
        return c["anchors"][0]
    cx, cy = c["click_target"]
    return [cx - 10, cy - 10, cx + 10, cy + 10]


# ------------------------------------------------------------------
# Stage 1-2: Merge overlapping candidates
# ------------------------------------------------------------------

def _merge_candidates(candidates: list[dict[str, Any]], iou_thresh: float) -> list[dict[str, Any]]:
    """Greedily merge candidates that overlap above *iou_thresh*."""
    merged: list[dict[str, Any]] = []
    used = [False] * len(candidates)

    for i, c in enumerate(candidates):
        if used[i]:
            continue
        group = [c]
        used[i] = True
        box_i = _anchor_box(c)
        for j in range(i + 1, len(candidates)):
            if used[j]:
                continue
            box_j = _anchor_box(candidates[j])
            if _iou(box_i, box_j) >= iou_thresh:
                group.append(candidates[j])
                used[j] = True
        merged.append(_fuse_group(group))

    return merged


def _fuse_group(group: list[dict[str, Any]]) -> dict[str, Any]:
    """Fuse a list of overlapping candidates into one."""
    best = max(group, key=lambda c: c.get("conf", 0))
    sources: list[str] = []
    texts: list[str] = []
    for c in group:
        sources.extend(c.get("sources", []))
        texts.extend(c.get("text", []))
    sources = sorted(set(sources))
    texts = sorted(set(t for t in texts if t))

    return {
        "id": best["id"],
        "type": best.get("type", "unknown"),
        "click_target": best["click_target"],
        "anchors": best.get("anchors", []),
        "text": texts,
        "conf": best.get("conf", 0),
        "sources": sources,
        "to_vision": best.get("to_vision", False),
        "coord_space": best.get("coord_space", CoordSpace.CROP),
    }


# ------------------------------------------------------------------
# Stage 3: Vote
# ------------------------------------------------------------------

def _vote(candidates: list[dict[str, Any]], min_votes: int) -> list[dict[str, Any]]:
    """Keep only candidates supported by ≥ *min_votes* sources."""
    return [c for c in candidates if len(c.get("sources", [])) >= min_votes]


# ------------------------------------------------------------------
# Stage 4: Classify (minimal rules – ambiguous → to_vision)
# ------------------------------------------------------------------

def classify(candidate: dict[str, Any], *, min_conf: float | None = None) -> dict[str, Any]:
    """Assign a type to *candidate* using minimal heuristic rules.

    When ambiguous, sets ``to_vision=true`` so Claude can decide.
    """
    if min_conf is None:
        min_conf = PERCEPT_CONFIG.classify_min_conf

    texts = candidate.get("text", [])
    joined = " ".join(texts).lower()
    ctype = candidate.get("type", "unknown")

    if ctype != "unknown":
        # Already classified by a detector – keep
        pass
    elif texts:
        # Text-bearing candidates
        if any(kw in joined for kw in ("save", "cancel", "ok", "submit", "close", "delete", "open")):
            ctype = "text_button"
        elif any(kw in joined for kw in ("on", "off")):
            ctype = "toggle"
        else:
            ctype = "text_button"  # default for labelled items
    else:
        ctype = "unknown"

    # Low-confidence → defer to Vision
    if candidate.get("conf", 0) < min_conf:
        candidate["to_vision"] = True

    candidate["type"] = ctype
    return candidate


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def ensemble(all_candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Run the full ensemble pipeline and return sorted candidates."""
    cfg = PERCEPT_CONFIG
    merged = _merge_candidates(all_candidates, cfg.ensemble_iou_threshold)
    voted = _vote(merged, cfg.ensemble_min_votes)
    classified = [classify(c) for c in voted]
    classified.sort(key=lambda c: c.get("conf", 0), reverse=True)
    return classified
