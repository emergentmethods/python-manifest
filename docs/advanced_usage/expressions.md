# Expressions

Expressions in Manifest are special string patterns that allow for dynamic configurations. They allow you to inject computed or environment-derived values directly into your configuration data. This feature is useful when you need your configuration to adapt based on certain conditions or computations at runtime.

Expressions follow a specific pattern: `$operation{arguments}`.

- **operation** represents the operation to perform.
- **arguments** is the argument for the operation, which can be a comma-separated list of values.

## Built-in Operations

Manifest provides a variety of built-in operations that can be used with expressions:

| Operation 	| Description                   	| Example           	|
|-----------	|-------------------------------	|-------------------	|
| `reverse` 	| Reverse a string              	| `$reverse{hello}` 	|
| `upper`   	| Convert a string to uppercase 	| `$upper{hello}`   	|
| `lower`   	| Convert a string to lowercase 	| `$lower{HELLO}`   	|

The above operations are used in expressions as follows:

```yaml
name_value: $reverse{olleH}
upper_value: $upper{hello}
lower_value: $lower{HELLO}
```

## Custom Operations

In addition to the built-in operations, you can define your own custom operations using the `add_operation` method from the `manifest.expressions.operations` module.

This function takes two parameters:

- **operation_name**: A string representing the name of the operation.
- **func**: A callable to call when the operation is resolved. This callable must accept two parameters:
    - **args**: list[str]: The arguments provided to the operation.
    - **context**: dict: A context dictionary. Depending on the specifics of your operation, you may or may not need to use this parameter.

Here is an example of creating a custom operation:

```python
from manifest.expressions.operations import register_operation

def multiply(args: list[str], context: dict) -> int:
    # This function ignores the context and simply multiplies the arguments.
    return int(args[0]) * int(args[1])

register_operation("multiply", multiply)
```

Now we can use our new operation in our configuration:

```yaml
result: $multiply{5,10}
```

In this example, the multiply operation would resolve to 50.

It's worth noting that operation functions can be synchronous or asynchronous, and the Manifest library handles both types automatically. This adds another layer of flexibility to how you can define your custom operations.