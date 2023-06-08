# Manifest

Manifest is a flexible and dynamic Python library designed for managing application manifests including configurations in Python projects. By using the `pydantic` library for data validation, it allows you to define your own models, support dynamic configurations via expressions, and even instantiate Python objects directly from the configuration.

## Features

- Load manifests and configurations from various sources including files and environment variables.
- Define manifests as Pydantic models.
- Supports dynamic configurations through the use of expressions.
- Instantiate Python objects directly from the configuration using Instantiable model.
- Supports YAML, JSON, and TOML files out of the box.
- Built on top of `asyncio`.
- Support for multiple file systems using `fsspec`.

## Getting Started

Install the library using pip:

```bash
pip install manifest
```

## Usage

### Manifest Object

The Manifest class allows you to load and process manifests and configurations from various sources. It is designed to be subclassed, allowing you to define your own configuration models.

```python
class MyConfiguration(Manifest):
    my_value: str
```

### Building the Manifest

Manifest instances can be created just like any other Pydantic model. You can create one from keyword arguments, from a dictionary, etc.

```python
config = MyConfiguration(my_value="Hello, World!")
config = MyConfiguration.parse_obj({"my_value": "Hello, World!"})
```

It supports a variety of ways to build the Manifest using methods like `from_files`, `from_env`, `from_key_values`, and more. They make it easy
to load and validate configurations from various sources, but often times you'll want to use a combination of them. This can be accomplished using the `build` method:

```python
config = await MyConfiguration.build(
    files=["path/to/config.yaml"],
    dotenv_files=["path/to/.env"],
    key_values=["key=value"],
    env_prefix="MY_CONFIGURATION",
    pre_process_hooks=[do_something_with_raw_text_func],
    post_process_hooks=[do_something_with_deserialized_text_func],
)
```

Most cases will only require a subset of these arguments, but they are all available for you to use. The `build` method will automatically decide which serializer to use based on the file extension. You will most often just use `build` when working with Manifests, but you can use the other methods if you need more control.

Files can be loaded from various sources including local files, remote files, and even compressed files. The `fsspec` library is used to support multiple file systems.

```python
config = await MyConfiguration.from_files(
    files=["s3://path/to/config.yaml"],
)
```

### Saving the Manifest

While a Manifest can be built from many different files, you can only persist a Manifest to a single file. To save it use the `to_file` method. It will automatically decide the serializer based on the file extension.

```python
await config.to_file("s3://path/to/config.yaml")
```

### Expressions

Manifest supports dynamic configurations through the use of expressions, providing a way to inject dynamic values into your configuration.

```yaml
my_value: $reverse{sometext}
```

### Instantiable Class

Instantiable is a generic model that can be used to instantiate objects from a model. It allows for direct instantiation of Python objects from the configuration, working in tandem with the Manifest.

```python
class MyObj:
    def __init__(self, n: int):
        self.n = n

class MyConfiguration(Manifest):
    my_obj: Instantiable[MyObj]

config = MyConfiguration(my_obj={"target": "my_module.MyObj", "n": 7})
obj = config.my_obj.instantiate()

print(obj.n)  # Output: 7
```

Instantiable objects can be instantiated from a dictionary or a Manifest. The `target` key is required and must be a string representing the path to the class. Any additional fields are treated as keyword arguments to the class constructor.


## Contributing
Merge requests are always welcome! Feel free to open a new issue if you have any questions or suggestions.