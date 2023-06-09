# Getting Started

Welcome to the Manifest library, a flexible and dynamic tool for managing application manifests, including configurations in Python projects. This guide will walk you through the steps to install the Manifest library and prepare for its use.

## Prerequisites

To use Manifest, you need to have Python 3.10 or newer installed on your system.

Manifest also depends on several Python libraries such as `pyyaml`, `python-rapidjson`, `pydantic`, `python-dotenv`, `fsspec`, and `toml`. Ensure your Python environment can support these dependencies. If you're using pip, these dependencies will be installed automatically when you install Manifest.

## Installation

To get started with Manifest, you need to install it first. You can install the Manifest library using pip:

```bash
pip install python-manifest
```

For development, you can install the library from source:

```bash
git clone https://github.com/emergentmethods/python-manifest.git
cd python-manifest
pip install poetry # If not already installed
poetry install
# The pre-commit hooks are only needed if you plan to contribute to the project
pre-commit install --hook-type commit-msg
pre-commit install
```

Now you are ready to start using Manifest! For a guide on how to use Manifest, head over to the [Basic Usage](basic_usage.md) page. For a deep dive into more specific topics, check out the rest of our [Advanced Usage](advanced_usage/index.md) guide.

If you encounter any problems, don't hesitate to raise an issue.