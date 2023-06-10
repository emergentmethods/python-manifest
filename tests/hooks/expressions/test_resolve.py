import pytest

from manifest.hooks.expressions.resolve import parse_expression, resolve_expression, resolve_expressions


async def test_parse_expression():
    result = parse_expression("$reverse{hello, world}")
    assert result == {"operation": "reverse", "args": "hello, world"}

    result = parse_expression("notanoperation")
    assert result is None


async def test_resolve_expression():
    result = await resolve_expression("$reverse{hello}", {})
    assert result == "olleh"

    result = await resolve_expression("notanoperation", {})
    assert result == "notanoperation"

    with pytest.raises(ValueError):
        await resolve_expression("$invalidoperation{hello}", {})


async def test_resolve_expressions():
    data = {
        "key1": "$reverse{hello}",
        "key2": "$sum{2,3}",
        "key3": {
            "key4": "$reverse{world}"
        },
        "key5": ["$reverse{hello}", "$sum{2,3}"]
    }

    result = await resolve_expressions(data)

    assert result == {
        "key1": "olleh",
        "key2": 5.0,
        "key3": {
            "key4": "dlrow"
        },
        "key5": ["olleh", 5.0]
    }