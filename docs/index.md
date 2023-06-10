# Overview

![Gitlab code coverage (self-managed, specific job)](https://img.shields.io/gitlab/pipeline-coverage/wizrds/manifest?branch=main&gitlab_url=https%3A%2F%2Fgit.freqai.cloud&job_name=unit-tests&style=flat-square)
![GitLab Release (self-managed)](https://img.shields.io/gitlab/v/release/wizrds/manifest?gitlab_url=https%3A%2F%2Fgit.freqai.cloud&include_prereleases&style=flat-square)
![GitLab (self-managed)](https://img.shields.io/gitlab/license/wizrds/manifest?gitlab_url=https%3A%2F%2Fgit.freqai.cloud&style=flat-square)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/python-manifest?style=flat-square)

---

**Source code**: [https://github.com/emergentmethods/python-manifest](https://github.com/emergentmethods/python-manifest)

---

Welcome to the official documentation of Manifest, an advanced Python library designed to simplify the process of managing application manifests and configurations. Whether you are configuring a simple application or managing a complex system, Manifest provides a robust set of features that make the process easier, more efficient, and less error-prone.

With Manifest, you can:

- Define custom models to validate your configurations.
- Load configurations from a variety of sources, such as environment variables, JSON files, YAML files, or TOML files.
- Instantiate Python objects directly from your configurations.
- Leverage dynamic configurations through expressions.
- Easily serialize and deserialize Manifests based on file extensions.

Built with Python's [asyncio](https://docs.python.org/3/library/asyncio.html) for asynchronous operations and relying on [fsspec](https://filesystem-spec.readthedocs.io/en/latest/) for flexible file system support, Manifest is designed to be efficient and versatile. Moreover, it's built on top of [pydantic](https://docs.pydantic.dev/latest/), providing seamless data validation.

This documentation will guide you through the features of Manifest, from installation and basic usage to advanced features. If you have any issues, please [open an issue](https://github.com/emergentmethods/python-manifest/issues).