from typing import TypeVar, Any, Generic

from manifest.pydantic import (
    BaseModel,
    Field,
    validator,
    model_copy,
    get_set_fields,
    get_fields,
    ConfigDict,
    GenericModel,
    IS_V1,
)
from manifest.utils import import_from_string

T = TypeVar("T")


class Instantiable(GenericModel, Generic[T]):
    """
    Instantiable is a generic model that can be used to instantiate objects from a model. It
    requires that the model specify a `target` attribute, which is used to import the class, and the
    model's fields are used as keyword arguments to the class constructor.
    """
    if IS_V1:  # pragma: no cover
        class Config:
            extra = "allow"
            arbitrary_types_allowed = True
            allow_population_by_field_name = True
    else:
        model_config = ConfigDict(
            {"extra": "allow", "arbitrary_types_allowed": True, "populate_by_name": True}
        )

    target: str = Field(alias="__target__")

    @validator("target", pre=True)
    def validate_target(cls, v: str) -> str:
        if not v:
            raise ValueError("target must be a non-empty string")
        return v

    def instantiate(self, **kwargs) -> T:
        return instantiate_from_model(self, extra=kwargs)


def instantiate_from_model(model: BaseModel, extra: dict = {}, skip: bool = False) -> Any:
    """
    Instantiate an object from a model.

    :param model: The model to instantiate from.
    :type model: BaseModel
    :param extra: Extra keyword arguments to pass to the object constructor.
    :type extra: dict
    :param skip: Whether to skip the target check.
    :type skip: bool
    :return: The instantiated object.
    """
    object_info = model_copy(model)

    if not hasattr(object_info, "target") or not object_info.target:
        if skip:
            return object_info
        raise ValueError("`model` must specify a `target` attribute")

    target = import_from_string(object_info.target)

    field_names = set(get_fields(object_info).keys())
    set_fields = get_set_fields(object_info)
    fields_to_copy = (set_fields | field_names) - {"target"}
    kwargs = {}

    for field in fields_to_copy:
        value = getattr(object_info, field)

        if isinstance(value, BaseModel):
            value = instantiate_from_model(value, skip=True)

        kwargs[field] = value

    return target(**{**kwargs, **extra})
