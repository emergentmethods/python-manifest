from typing import Any
from pydantic.version import VERSION
from pydantic import BaseModel, Field, validator, ConfigDict


__all__ = (
    "IS_V1",
    "BaseModel",
    "Field",
    "validator",
    "ConfigDict",
    "GenericModel",
    "model_dump",
    "model_copy",
    "get_model_extras",
)

IS_V1 = VERSION.startswith("1.")


if IS_V1:
    from pydantic.generics import GenericModel
else:
    GenericModel = BaseModel


def model_dump(
    model: BaseModel,
    *,
    include: set[str] | set[int] | dict[int, Any] | dict[str, Any] | None = None,
    exclude: set[str] | set[int] | dict[int, Any] | dict[str, Any] | None = None,
    by_alias: bool = True,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
    warnings: bool = False,
) -> Any:
    if IS_V1:
        return model.dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
    else:
        return model.model_dump(
            mode="python",
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            warnings=warnings
        )


def model_copy(
    model: BaseModel,
    *,
    update: dict[str, Any] | None = None,
    deep: bool = False,
) -> BaseModel:
    if IS_V1:
        return model.copy(update=update, deep=deep)
    else:
        return model.model_copy(update=update, deep=deep)


def get_model_extras(model: BaseModel) -> dict[str, Any]:
    if IS_V1:
        return {
            k: v
            for k, v in model.__dict__.items()
            if k not in type(model).__fields__.keys()  # type: ignore
        }
    else:
        return model.__pydantic_extra__ or {}


def get_set_fields(model: BaseModel) -> set[str]:
    if IS_V1:
        return model.__fields_set__
    else:
        return model.model_fields_set


def get_fields(model: BaseModel) -> dict[str, Any]:
    if IS_V1:
        return model.__fields__
    else:
        return model.model_fields
