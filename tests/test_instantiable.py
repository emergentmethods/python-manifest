import pytest
from pydantic import BaseModel

from manifest.utils import import_from_string
from manifest.instantiable import instantiate_from_model, Instantiable
from tests.mydummyobject import MyDummyObject


def test_instantiate_from_model() -> None:
    class MyModel(BaseModel):
        target: str
        x: int = 5
        y: int = 10

    model = MyModel(target="tests.mydummyobject.MyDummyObject")
    obj = instantiate_from_model(model)

    assert type(obj.__class__) == MyDummyObject.__class__
    assert obj.x == 5
    assert obj.y == 10

    with pytest.raises(ValueError):
        instantiate_from_model(MyModel(target=""))

    instantiate_from_model(MyModel(target="", x=10, y=20), skip=True)

    class NestedMyModel(BaseModel):
        target: str
        x: int = 5
        y: int = 10
        nested: MyModel

    nested_model = NestedMyModel(
        target="tests.mydummyobject.MyDummyObject",
        nested=MyModel(target="tests.mydummyobject.MyDummyObject", x=10, y=20),
    )

    obj = instantiate_from_model(nested_model)

    assert type(obj.__class__) == MyDummyObject.__class__
    assert obj.x == 5
    assert obj.y == 10
    assert type(obj.nested.__class__) == MyDummyObject.__class__
    assert obj.nested.x == 10
    assert obj.nested.y == 20


def test_instantiable_instantiate():
    instantiable = Instantiable[MyDummyObject](
        target="tests.mydummyobject.MyDummyObject",
        x=5,
    )
    obj = instantiable.instantiate(y=10)

    assert type(obj.__class__) == MyDummyObject.__class__
    assert obj.x == 5
    assert obj.y == 10

    with pytest.raises(ValueError):
        Instantiable[MyDummyObject](target="")
