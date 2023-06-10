import os


def substitute_env_vars(text: bytes, env_vars: dict[str, str] = dict(os.environ)) -> bytes:
    """
    Replace environment variables in a string with their values.

    The string variables are formatted as $VAR or ${VAR}.

    :param text: The string to substitute environment variables in.
    :return: The string with environment variables substituted.
    """
    from string import Template

    template = Template(text.decode("utf-8"))
    substituted = template.safe_substitute(env_vars)

    return substituted.encode("utf-8")
