from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter, ValidationError


class ActionBase(BaseModel):
    type: str


class MoveAction(ActionBase):
    type: Literal["move"]
    to: tuple[int, int]
    duration: float = 0.3


class WaitAction(ActionBase):
    type: Literal["wait"]
    seconds: float = Field(gt=0)


class ClickAction(ActionBase):
    type: Literal["click"]
    at: tuple[int, int] | None = None
    button: Literal["left", "middle", "right"] = "left"
    clicks: int = Field(default=1, ge=1)


class DragAction(ActionBase):
    type: Literal["drag"]
    from_: Annotated[tuple[int, int], Field(alias="from")]
    to: tuple[int, int]
    duration: float = 0.4
    button: Literal["left", "middle", "right"] = "left"

    model_config = {"populate_by_name": True}


class TypeAction(ActionBase):
    type: Literal["type"]
    text: str
    interval: float = Field(default=0.02, ge=0)


class KeyAction(ActionBase):
    type: Literal["key"]
    keys: list[str] = Field(min_length=1)


class ScrollAction(ActionBase):
    type: Literal["scroll"]
    amount: int
    at: tuple[int, int] | None = None


ActionModel = MoveAction | WaitAction | ClickAction | DragAction | TypeAction | KeyAction | ScrollAction
ACTION_ADAPTER = TypeAdapter(ActionModel)


def _validate_bounds(point: tuple[int, int], width: int, height: int) -> None:
    x, y = point
    if x < 0 or y < 0 or x >= width or y >= height:
        raise ValueError(f"point out of bounds: {point}")


def validate_action(raw: dict, width: int, height: int) -> dict:
    action = ACTION_ADAPTER.validate_python(raw)
    payload = action.model_dump(by_alias=True)
    if payload["type"] in {"move", "drag"}:
        _validate_bounds(payload["to"], width, height)
    if payload["type"] == "drag":
        _validate_bounds(payload["from"], width, height)
    if payload.get("at") is not None:
        _validate_bounds(payload["at"], width, height)
    return payload


def validate_actions(raw_actions: list[dict], width: int, height: int) -> tuple[list[dict], list[dict]]:
    accepted: list[dict] = []
    rejected: list[dict] = []
    for idx, raw in enumerate(raw_actions):
        try:
            accepted.append(validate_action(raw, width, height))
        except (ValidationError, ValueError) as exc:
            rejected.append({"index": idx, "action": raw, "reason": str(exc)})
    return accepted, rejected
