#!/usr/bin/env bash
set -euo pipefail
shopt -s inherit_errexit

readonly API_URL="https://api.github.com/repos/pulsepm/pulse/releases"
readonly BINARY_NAME="pulse"
readonly INSTALL_DIR="${HOME}/.local/bin"
readonly BINARY_PATH="${INSTALL_DIR}/${BINARY_NAME}"

# Paths used for removing Pulse
readonly CONFIG_PATH="${XDG_CONFIG_HOME:-${HOME}/.config}/pulsepm"
readonly DATA_PATH="${XDG_DATA_HOME:-${HOME}/.local/share}/pulsepm"
readonly STATE_PATH="${XDG_STATE_HOME:-${HOME}/.local/state}/pulsepm"

get_latest_version() {
    wget -qO- "${API_URL}" | grep -m1 -Po '"tag_name": "\K.*?(?=")'
}

get_download_url() {
    wget -qO- "${API_URL}" | grep -m1 -Po '"browser_download_url": "\K.*pulse(?=")'
}

check_and_update() {
    local current_version
    local latest_version
    current_version=$(pulse -v 2>/dev/null | awk '{print $2}')
    
    if [[ -z "${current_version}" ]]; then
        echo "Could not determine the current version of pulse. Assuming update is needed."
        return 0
    else
        latest_version=$(set -e; get_latest_version)
        if [[ "${current_version}" != "${latest_version}" ]]; then
            echo "Updating pulse from ${current_version} to ${latest_version}"
            return 0
        else
            echo "Pulse is already up to date (version ${current_version})."
            return 1
        fi
    fi
}

download_and_install() {
    local download_url
    download_url=$(get_download_url)
    echo "Downloading pulse binary from ${download_url}"
    
    if ! wget -q -O "${BINARY_PATH}" "${download_url}"; then
        echo "Download failed. Please check your internet connection and try again." >&2
        exit 1
    fi
    
    chmod u+x "${BINARY_PATH}"
}

update_path() {
    local config_file
    case "${SHELL}" in
        */bash)
            config_file="${HOME}/.bashrc"
            ;;
        */zsh)
            config_file="${HOME}/.zshrc"
            ;;
        *)
            config_file="${HOME}/.profile"
            ;;
    esac
    
    if [[ ":${PATH}:" != *":${INSTALL_DIR}:"* ]]; then
        echo "Adding ${INSTALL_DIR} to PATH in ${config_file}"
        echo "export PATH=\$PATH:${INSTALL_DIR}" >> "${config_file}"
    fi
}

list_dependencies() {
    echo "This script requires the following dependencies:"
    echo "- wget: for downloading files and interacting with the GitHub API"
    echo "- grep: for parsing command output"
    echo "- awk: for text processing"
    echo "Please ensure these are installed on your system."
}

install_or_update() {
    local is_fresh_install=true

    if command -v pulse &> /dev/null; then
        is_fresh_install=false
        echo "Existing pulse installation found. Checking for updates..."
        if ! check_and_update; then
            exit 0
        fi
    fi

    # Create the ~/.local/bin directory and add to $PATH if it's not there
    mkdir -p "${INSTALL_DIR}"
    
    if ${is_fresh_install}; then
        update_path
    fi
    
    if ! download_and_install; then
        echo "Installation failed. Please check your permissions and try again." >&2
        list_dependencies
        exit 1
    fi
    
    if command -v pulse &> /dev/null; then
        if ${is_fresh_install}; then
            echo "Pulse has been successfully installed and added to your PATH."
            echo "You may need to restart your shell or source your shell configuration file for PATH changes to take effect."
        else
            echo "Pulse has been successfully updated."
        fi
    else
        echo "Installation failed. Please check your permissions and try again." >&2
        list_dependencies
        exit 1
    fi
}

uninstall() {
    local remove_all=false

    if [[ "${1:-}" == "--remove-all" ]]; then
        remove_all=true
    fi

    rm -f "${BINARY_PATH}" || { echo "Failed to remove ${BINARY_PATH}. Remove it manually to uninstall Pulse completely." >&2; }

    if ${remove_all}; then
        echo "Removing all associated directories..."
        rm -rf "${CONFIG_PATH}" || { echo "Failed to remove ${CONFIG_PATH}. Remove it manually to uninstall Pulse completely." >&2; }
        rm -rf "${DATA_PATH}" || { echo "Failed to remove ${DATA_PATH}. Remove it manually to uninstall Pulse completely." >&2; }
        rm -rf "${STATE_PATH}" || { echo "Failed to remove ${STATE_PATH}. Remove it manually to uninstall Pulse completely." >&2; }
    fi

    echo "Pulse has been removed."
}

print_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help       Display this help message"
    echo "  -r, --remove     Remove Pulse (removes only the binary)"
    echo "  --remove-all     Remove Pulse and remove all associated directories"
    echo ""
    echo "If no options are provided, the script will install or update Pulse."
}

main() {
    if [[ $# -eq 0 ]]; then
        install_or_update
        exit 0
    fi

    case "$1" in
        -h|--help)
        print_usage
        exit 0
        ;;
        -r|--remove)
        uninstall
        exit 0
        ;;
        --remove-all)
        uninstall --remove-all
        exit 0
        ;;
        *)
        echo "Unknown option: $1" >&2
        print_usage
        exit 22
        ;;
    esac
}

main "$@"
