# Basic Usage

This section provides a step-by-step guide on how to use Manifest. We'll go through the process of setting up a basic application configuration, though manifests are meant to describe any part of a system, not just configurations.

First, let's import the Manifest class:

```python
from manifest import Manifest
```

The core component of Manifest is a class that you will subclass to create your own model. These are just pydantic models, so any feature that pydantic provides you can apply here. For more information about pydantic, see the documentation [here](https://docs.pydantic.dev/latest/). Here's a simple example:

```python
class MyConfiguration(Manifest):
    database_url: str
```

Since model classes inherit from Pydantic's BaseModel, they can be instantiated with keyword arguments or parsed from a dictionary:

```python
config = MyConfiguration(database_url="sqlite:///database.db")
config = MyConfiguration.parse_obj({"database_url": "sqlite:///database.db"})
```

However, the real power of Manifest comes from its ability to build and manage configurations from various sources. For instance, you can build a Manifest from a list of files, environment variables, or key-value pairs:

```python
config = await MyConfiguration.build(
    files=["path/to/config.yaml"],
    dotenv_files=["path/to/.env"],
    key_values=["database_url=value"],
    env_prefix="MY_CONFIGURATION",
)
```

You can also load configurations directly from files:

```python
config = await MyConfiguration.from_files(["path/to/config.yaml"])
```

Or from environment variables:

```python
config = await MyConfiguration.from_env(["path/to/.env"], env_prefix="MY_CONFIGURATION")
```

Or even from simple key-value pairs:

```python
config = await MyConfiguration.from_key_values(["a.b.c=value"])
```

Finally, Manifest provides a simple way to save your configuration back to a file:

```python
await config.to_file("path/to/config.yaml")
```

Once you have a configuration, you can access its values as attributes:

```python
print(config.database_url)
```

You can also access nested values using dot delimited keys:

```python
print(config.get_by_key("a.b.c"))
```

And you can set and unset values using the same dot delimited keys:  

```python
config = config.set_by_key("a.b.c", "value")
config = config.unset_by_key("a.b.c")
```

???+ "Note"
    When working with your Manifest and using `set_by_key`, and `unset_by_key`, you should always assign the result back to the original Manifest. This is because these methods return a new Manifest with the updated values, rather than modifying the original Manifest.

There is even support for Manifests with custom root types:

```python
class MyList(Manifest):
    __root__: list[int]

config = await MyList.from_files(["path/to/list.json"])
print(config.__root__) # [1, 2, 3]

await config.to_file("path/to/list.json")

# path/to/list.json -> [1, 2, 3]
```

These features make Manifest a powerful tool for managing your application manifests and configurations. To learn more about the advanced features of Manifest, including expressions and the Instantiable class, head over to the [Advanced Usage guide](advanced_usage/index.md).
