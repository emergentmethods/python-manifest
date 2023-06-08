# Instantiable Objects

The `Instantiable` object in Manifest allows for direct instantiation of Python objects from the configuration data. This is especially useful when you want to define and create Python objects directly within your Manifests, making your configuration more dynamic and flexible.

An `Instantiable` is described in your Manifest with a `target` field, which references the import path for the object to be instantiated. The `Instantiable` can also take additional parameters, which are treated as keyword arguments for the object's constructor.

Here's an example of how to use an `Instantiable`:

```python
from manifest import Manifest, Instantiable

class MyObj:
    def __init__(self, n: int):
        self.n = n

class MyConfiguration(Manifest):
    my_obj: Instantiable[MyObj]

config = MyConfiguration(my_obj={"target": "my_module.MyObj", "n": 7})
obj = config.my_obj.instantiate()

print(obj.n)  # Output: 7
```

In this example, we define a `MyObj` class with an `__init__` method that takes one parameter, `n`. In the `MyConfiguration` Manifest, we define `my_obj` as an `Instantiable` of `MyObj`. When creating a `MyConfiguration` instance, we pass a dictionary to `my_obj`, with `"my_module.MyObj"` as the `target` and `7` as the additional parameter `n`. The target must be a string representing the import path to the class.

When we call `config.my_obj.instantiate()`, it creates a new instance of `MyObj`, passing `n=7` to its constructor.

This provides a powerful way to create Python objects directly from your configuration data. You can define multiple Instantiable objects within a single Manifest, providing a versatile way to manage complex configurations. Everything works with static type checkers as well, since we defined `my_obj` as an `Instantiable` of `MyObj`. This tells type checkers like mypy that the `my_obj` field will be an instance of `Instantiable`, and the return value on the `instantiate` method will be an instance of `MyObj`.