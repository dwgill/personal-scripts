set positional-arguments

export PYTHONPATH := justfile_directory()
export ENV_FILE_PATH := justfile_directory() / '.env'

SECRET_KEY_PATH := env_var_or_default('SECRET_KEY_PATH', justfile_directory() / '..' / 'secret.key')

_help:
    just --list

setup:
    poetry install

obsidian *args='':
    PYTHONPATH="$$PWD" poetry run python -m obsidian "$@"

obsidian-add-tag dir_path tag:
    just obsidian tag apply --directory='{{dir_path}}' --tag='{{tag}}'

decrypt-env ENCRYPTED_ENV_FILE='./env.enc' PLAINTEXT_ENV_FILE=ENV_FILE_PATH:
    just crypt 'decrypt' '{{ENCRYPTED_ENV_FILE}}' '{{PLAINTEXT_ENV_FILE}}' '{{SECRET_KEY_PATH}}'

encrypt-env ENCRYPTED_ENV_FILE='./env.enc' PLAINTEXT_ENV_FILE=ENV_FILE_PATH:
    just crypt 'encrypt' '{{PLAINTEXT_ENV_FILE}}' '{{ENCRYPTED_ENV_FILE}}' '{{SECRET_KEY_PATH}}'

new-env-encryption-key KEY_PATH:
    just crypt 'new-key' '{{KEY_PATH}}'

crypt *ARGS:
    poetry run python -m util.crypt "$@"
