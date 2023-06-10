# Hooks

In Manifest, hooks are a set of functions that are invoked during the reading and writing of files. There are two types of hooks you can use in the two operations:

- **pre_process_hooks**: These are called before the file is parsed, after it has been read when loading. When dumping, these are called before the file is written.
- **post_process_hooks**: These are called after the file has been parsed when loading. When dumping, these are called after the file has been written.

These hooks give you a powerful way to modify and manipulate your configuration data during its processing, providing you with the flexibility to customize how your configurations are handled.

## Built-in Hooks

By default, Manifest supports a set of built-in hooks for commonly used operations.

### Expressions
Expressions, which are a form of post-processing hooks, allow you to dynamically modify your configuration data after it's been loaded. They provide a way to inject dynamic values into your configuration. For more information see the [Expressions](/advanced_usage/expressions.md) page.

### Environment Variable Substitution

Another built-in hook is the `substitute_env_vars` hook, which provides support for specifying environment variables in your configuration files. This hook substitutes any environment variables in your configuration data with their corresponding values from the environment.

This feature is useful when you want to inject sensitive data into your configuration without having to hard-code it into your configuration files. For instance, you can store your database credentials as environment variables and reference them in your configuration file, and the `substitute_env_vars` hook will automatically replace them with the actual values during configuration processing.

## Defining Your Own Hooks

In addition to the built-in hooks, you can also define your own pre-process and post-process hooks to perform custom operations on your configuration data.

To define a hook, you need to create a function that takes a single parameter (the configuration data) and returns the processed configuration data. You can then pass this function to the `pre_process_hooks` or `post_process_hooks` parameters when building your Manifest, or using any file-based method such as `from_files`, `to_file`. Or if you'd like to register it globally to always be used you can call `register_hook`.

Here is an example of a custom pre-process hook:

```python
from manifest.hooks import register_hook

def replace_one_with_two(contents: bytes) -> bytes:
    string_contents = str(contents, "utf-8")
    string_contents.replace("one", "two")
    return bytes(string_contents, "utf-8")

# Pass it when you build your Manifest
config = await MyConfiguration.from_files(
    files=["path/to/config.yaml"],
    pre_process_hooks=[replace_one_with_two],
    post_process_hooks=[],
)

# Or register it globally
register_hook(replace_one_with_two, hook_type="pre", operation="load")
```

In this example, the `replace_one_with_two` function will be called after the file has been read but before it is parsed by the Serializer. The function takes the file contents as bytes and returns the modified bytes, which is then passed to the Serializer for parsing. If it were a post-process hook, it would be called after the Serializer has parsed the file, and the parameter type would be a dictionary instead of bytes.

When registering hooks the available hook types are `pre` and `post`, and the available operations are `load` and `dump`.

Hooks provide a powerful and flexible way to control how your configuration data is processed in Manifest, enabling you to customize your configuration processing to suit your specific needs.