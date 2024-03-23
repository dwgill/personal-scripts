set positional-arguments

default:
    @echo "Hello, World!"

setup:
    poetry install

obsidian *args='':
    PYTHONPATH="$$PWD" poetry run python -m obsidian "$@"

obsidian-add-tag dir_path tag:
    just obsidian tag apply --directory='{{dir_path}}' --tag='{{tag}}'
