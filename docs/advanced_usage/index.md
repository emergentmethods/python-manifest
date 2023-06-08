# Advanced Usage

Welcome to the Advanced Usage section of the Manifest documentation. This is your launching pad into understanding and utilizing the more complex and powerful features that the Manifest library offers.

In this section, we'll introduce several advanced features and provide links to more detailed pages for each. Here are the topics we will cover:

## Dynamic Configurations with Expressions

The Manifest library supports dynamic configurations via special string patterns known as expressions. This feature allows you to inject computed or environment-derived values directly into your configuration data.

Learn More about [Expressions](/advanced_usage/expressions.md)

## Instantiable Objects

Manifest can instantiate Python objects directly from your configuration, a powerful feature that enables more flexible and dynamic application setups. This is made possible with the `Instantiable` model.

Learn More about [Instantiable Objects](/advanced_usage/instantiable.md)

## Hooks for Pre-processing and Post-processing

The library provides a mechanism for applying your own functions to the configuration data before (pre-processing) and after (post-processing) it is serialized/deserialized when reading or writing to files. This can be helpful for performing custom transformations or validations on your configuration data.

Learn More about [Pre-processing and Post-processing Hooks](/advanced_usage/hooks.md)

## Working with Multiple File Systems

Thanks to the use of fsspec library, Manifest supports multiple file systems, enabling you to load configuration files from various sources including local files, remote files, and even compressed files.

Learn More about Working with Multiple [File Systems](/advanced_usage/file_systems.md)

Remember, these advanced features offer you greater control and flexibility in how you define and use your configurations. However, with this increased power comes the responsibility of using these features wisely to maintain the integrity and stability of your application.