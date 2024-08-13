import os
import functools
from typing import Callable
from dotenv import dotenv_values
from pathlib import Path

env_file_values = dotenv_values(
    os.environ.get("ENV_FILE_PATH", str(Path.cwd() / ".env"))
)


def _get_env_var[
    T
](key: str, default: str | None = None, *, coerce: Callable[[str], T],) -> T:
    str_value = os.environ.get(key, None)
    if str_value is None:
        str_value = env_file_values.get(key, None)

    if str_value is None:
        if default is None:
            raise MissingEnvVarError(key)
        else:
            str_value = default

    try:
        return coerce(str_value)
    except (ValueError, TypeError) as e:
        raise InvalidEnvVarError(key, str_value) from e


def airtable_personal_access_token():
    return _get_env_var("AIRTABLE_PERSONAL_ACCESS_TOKEN", coerce=str)


def airtable_daniel_network_base_id():
    return _get_env_var("AIRTABLE_DANIEL_NETWORK_BASE_ID", coerce=str)


def airtable_daniel_network_people_table_id():
    return _get_env_var("AIRTABLE_DANIEL_NETWORK_PEOPLE_TABLE_ID", coerce=str)


def _surround_with_quotes(string: str) -> str:
    if "'" not in string:
        return f"'{string}'"

    if '"' not in string:
        return f'"{string}"'

    if "'''" not in string:
        return f"'''{string}'''"

    return f'"""{string}"""'


class MissingEnvVarError(ValueError):
    def __init__(self, env_var_name: str) -> None:
        self.env_var_name = env_var_name
        self.message = (
            f"Missing environment variable: {_surround_with_quotes(env_var_name)}"
        )

        super().__init__(self.message)


class InvalidEnvVarError(ValueError):
    def __init__(self, env_var_name: str, env_var_value: str) -> None:
        self.env_var_name = env_var_name
        self.env_var_value = env_var_value
        self.message = f"Invalid environment variable: {_surround_with_quotes(env_var_name)} = {_surround_with_quotes(env_var_value)}"

        super().__init__(self.message)
