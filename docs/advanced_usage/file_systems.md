# Working with Filesystems

Manifest leverages the `fsspec` library to provide flexible and versatile filesystem support. This allows Manifest to interact with a wide variety of filesystems and storage solutions, including local files, remote files (over HTTP, S3, etc.), and even compressed files.

## File-Based Methods

The Manifest object includes several file-based methods, such as `from_files`, `to_file`, and `build`. Each of these methods supports a parameter called `filesystem_options`, which is a dictionary of options passed to `fsspec` when reading from or writing to files.

This `filesystem_options` parameter can be used to pass additional information needed to access the filesystem. This could be authentication details, caching options, or other filesystem-specific settings.

Here's an example of using filesystem_options to provide credentials when reading a file from S3:

```python
config = await MyConfiguration.from_files(
    files=["s3://path/to/config.yaml"],
    filesystem_options={
        'key': '<your-access-key>',
        'secret': '<your-secret-key>'
    }
)
```

## Supported Protocols

Because Manifest is built on top of `fsspec`, it supports all the protocols that `fsspec` does. This includes, but is not limited to:

- Local files (Default) (file://)
- HTTP/HTTPS
- Amazon S3 (s3://)
- Google Cloud Storage (gs://)
- Azure Blob Storage (abfs://)
- Hadoop Distributed File System (HDFS)

You can check the [fsspec documentation](https://filesystem-spec.readthedocs.io/en/latest/) for a full list of supported protocols and their usage.

Remember that different filesystems may require different options to be passed via `filesystem_options`. Always refer to the `fsspec` documentation or the specific filesystem's documentation for details.

Using Manifest in conjunction with fsspec offers a powerful and flexible way to handle your application's configurations, no matter where they are stored.