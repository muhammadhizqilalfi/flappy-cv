#!/bin/bash
read -ra raw_name <<< "$(ls ./*.py 2>/dev/null)"

conf_path="project.conf"
file_name="${raw_name[*]}"
file_name="${file_name:2}"

config() {
    local key=$1
    local value=$2
    local config=$3

    if grep -q "^$key=" "$config"; then
        sed -i "s/^$key=.*/$key=$value/" "$config"
    else
        echo "$key=$value" >> "$config"
    fi
}

help() {
    echo -e "Using: ./run.sh [COMMAND]\n"

    echo "Commands:"
    echo "  start   : Run the information retrieval system program [Ex: ./run.sh start]"
    echo "  help    : Show help message [Ex: ./run.sh help]"
    echo "  version : Show version [Ex: ./run.sh version]"
}

command -v poetry >/dev/null 2>&1
is_poetry_exists=$?

command -v python >/dev/null 2>&1
is_python_exists=$?

# shellcheck source=/dev/null
source "$conf_path"

if [[ "$1" == "start" ]]; then
    if [[ is_poetry_exists -eq 0 && is_python_exists -eq 0 ]]; then
        if [[ $file_name != "" ]]; then
            if [[ $POETRY_DEP_INSTALLED == false ]]; then
                poetry install --no-root
                poetry run python "$file_name"
                config "POETRY_DEP_INSTALLED" true "$conf_path"
            else
                poetry run python "$file_name"
            fi
        else
            echo "Error: No such file or directory"
            exit 1
        fi

        exit 0
    elif [[ is_poetry_exists -eq 1 && is_python_exists -eq 0 ]]; then
        echo "Warning: 'poetry' command is not recognized"

        if [[ $file_name != "" ]]; then
            python "$file_name"
        else
            echo "Error: No such file or directory"
            exit 1
        fi

        exit 0
    else
        echo "Error: 'python' command is not recognized"
        exit 127
    fi
elif [[ "$1" == "help" ]]; then
    help
elif [[ "$1" == "version" ]]; then
    echo "$PROGRAM_NAME $PROGRAM_VERSION"
else
    help
fi