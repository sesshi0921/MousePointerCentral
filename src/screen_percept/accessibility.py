"""Accessibility-tree shortcut (§5.1).

If the OS exposes an accessibility tree for the target window we can
skip the entire CV pipeline and get accurate element coordinates
(including state information).  Returns ``None`` when inaccessible.
"""

from __future__ import annotations

import platform
from typing import Any, Optional

from .coords import CoordSpace


def get_accessibility_tree(
    pid: int | None = None,
    window_title: str | None = None,
) -> Optional[list[dict[str, Any]]]:
    """Return the accessibility tree for the given window.

    Each element is a dict compatible with the Candidate schema, with
    ``coord_space:"screen"`` and accurate ``click_target``.

    Returns ``None`` when the tree cannot be obtained (missing
    permissions, unsupported OS, etc.).
    """
    system = platform.system()

    if system == "Darwin":
        return _get_tree_macos(pid, window_title)
    if system == "Windows":
        return _get_tree_windows(pid, window_title)

    # Linux / other – not yet implemented
    return None


# ------------------------------------------------------------------
# macOS (pyobjc)
# ------------------------------------------------------------------

def _get_tree_macos(
    pid: int | None,
    window_title: str | None,
) -> Optional[list[dict[str, Any]]]:
    try:
        from AppKit import NSWorkspace  # type: ignore[import-untyped]
        import Quartz  # type: ignore[import-untyped]

        if pid is None:
            app = NSWorkspace.sharedWorkspace().frontmostApplication()
            pid = app.processIdentifier()

        app_ref = Quartz.AXUIElementCreateApplication(pid)
        err, windows = Quartz.AXUIElementCopyAttributeValue(app_ref, "AXWindows", None)
        if err or not windows:
            return None

        target = windows[0]
        if window_title:
            for w in windows:
                _, title = Quartz.AXUIElementCopyAttributeValue(w, "AXTitle", None)
                if title and window_title.lower() in str(title).lower():
                    target = w
                    break

        elements: list[dict[str, Any]] = []
        _walk_ax(target, elements, idx_counter=[0])
        return elements if elements else None
    except Exception:
        return None


def _walk_ax(element: Any, out: list[dict[str, Any]], idx_counter: list[int]) -> None:
    """Recursively walk the AX element tree."""
    try:
        import Quartz  # type: ignore[import-untyped]

        _, role = Quartz.AXUIElementCopyAttributeValue(element, "AXRole", None)
        _, title = Quartz.AXUIElementCopyAttributeValue(element, "AXTitle", None)
        _, position = Quartz.AXUIElementCopyAttributeValue(element, "AXPosition", None)
        _, size = Quartz.AXUIElementCopyAttributeValue(element, "AXSize", None)

        if position and size:
            import Quartz.CoreGraphics as CG  # type: ignore[import-untyped]

            pos = CG.CGPointMake(0, 0)
            Quartz.AXValueGetValue(position, Quartz.kAXValueCGPointType, pos)
            sz = CG.CGSizeMake(0, 0)
            Quartz.AXValueGetValue(size, Quartz.kAXValueCGSizeType, sz)

            x, y = int(pos.x), int(pos.y)
            w, h = int(sz.width), int(sz.height)
            cx, cy = x + w // 2, y + h // 2

            ctype = _ax_role_to_type(str(role) if role else "")
            idx = idx_counter[0]
            idx_counter[0] += 1
            out.append({
                "id": f"ax_{idx:03d}",
                "type": ctype,
                "click_target": [cx, cy],
                "anchors": [[x, y, x + w, y + h]],
                "text": [str(title)] if title else [],
                "conf": 1.0,
                "sources": ["accessibility"],
                "to_vision": False,
                "coord_space": CoordSpace.SCREEN,
            })

        _, children = Quartz.AXUIElementCopyAttributeValue(element, "AXChildren", None)
        if children:
            for child in children:
                _walk_ax(child, out, idx_counter)
    except Exception:
        pass


# ------------------------------------------------------------------
# Windows (uiautomation)
# ------------------------------------------------------------------

def _get_tree_windows(
    pid: int | None,
    window_title: str | None,
) -> Optional[list[dict[str, Any]]]:
    try:
        import uiautomation as auto  # type: ignore[import-untyped]

        if window_title:
            win = auto.WindowControl(searchDepth=1, Name=window_title)
        else:
            win = auto.GetForegroundControl()
        if win is None:
            return None

        elements: list[dict[str, Any]] = []
        _walk_uia(win, elements, [0])
        return elements if elements else None
    except Exception:
        return None


def _walk_uia(control: Any, out: list[dict[str, Any]], idx_counter: list[int]) -> None:
    try:
        import uiautomation as auto  # type: ignore[import-untyped]

        rect = control.BoundingRectangle
        if rect.width() > 0 and rect.height() > 0:
            x, y = int(rect.left), int(rect.top)
            w, h = int(rect.width()), int(rect.height())
            cx, cy = x + w // 2, y + h // 2
            name = control.Name or ""
            ctype = _uia_type(control.ControlTypeName or "")
            idx = idx_counter[0]
            idx_counter[0] += 1
            out.append({
                "id": f"uia_{idx:03d}",
                "type": ctype,
                "click_target": [cx, cy],
                "anchors": [[x, y, x + w, y + h]],
                "text": [name] if name else [],
                "conf": 1.0,
                "sources": ["accessibility"],
                "to_vision": False,
                "coord_space": CoordSpace.SCREEN,
            })

        for child in control.GetChildren():
            _walk_uia(child, out, idx_counter)
    except Exception:
        pass


# ------------------------------------------------------------------
# Role → type mapping
# ------------------------------------------------------------------

def _ax_role_to_type(role: str) -> str:
    mapping = {
        "AXButton": "button",
        "AXTextField": "field",
        "AXTextArea": "field",
        "AXCheckBox": "toggle",
        "AXRadioButton": "toggle",
        "AXImage": "icon",
        "AXStaticText": "text_button",
    }
    return mapping.get(role, "unknown")


def _uia_type(control_type: str) -> str:
    mapping = {
        "ButtonControl": "button",
        "EditControl": "field",
        "TextControl": "text_button",
        "CheckBoxControl": "toggle",
        "RadioButtonControl": "toggle",
        "ImageControl": "icon",
    }
    return mapping.get(control_type, "unknown")
