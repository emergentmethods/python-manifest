from manifest.hooks.builtin import substitute_env_vars


def test_substitute_env_vars():
    # Define the environment variables
    env_vars = {
        "VAR1": "value1",
        "VAR2": "value2"
    }

    # Define the input text
    input_text = b"Text with $VAR1 and ${VAR2}"

    # Call substitute_env_vars with the input text and environment variables
    result = substitute_env_vars(input_text, env_vars)

    # Assert the result is as expected
    expected_output = b"Text with value1 and value2"
    assert result == expected_output