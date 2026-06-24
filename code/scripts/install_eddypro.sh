#!/usr/bin/env bash

set -euo pipefail

# Disable git pager and prompts for scripted use
export GIT_TERMINAL_PROMPT=0
export GIT_PAGER=cat

# Parse command line arguments
INSTALL_DIR="software/eddypro-engine"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --install-dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

mkdir -p "${INSTALL_DIR}"
INSTALL_DIR="$(realpath "${INSTALL_DIR}")"

REPO_DIR="${INSTALL_DIR}"
REPO_URL="https://github.com/LI-COR-Environmental/eddypro-engine.git"

echo "=== EddyPro Engine Installer ==="

OS="$(uname -s)"

# Map OS to the build output subdirectory name
case "${OS}" in
    Linux)  SYSTEM="linux" ;;
    Darwin) SYSTEM="mac"   ;;
    *)
        echo "Unsupported operating system: ${OS}"
        exit 1
        ;;
esac


# ── resolve_gfortran ───────────────────────────────────────────────────────────
# Sets FC/F77/F90/F95 to the versioned gfortran binary from Homebrew.
# Called unconditionally on macOS so re-runs (where brew install is skipped)
# still get a valid compiler.
resolve_gfortran() {
    local gcc_prefix
    gcc_prefix="$(brew --prefix gcc)"

    # Sort numerically by version so gfortran-14 beats gfortran-9
    FC="$(ls "${gcc_prefix}/bin/gfortran-"* 2>/dev/null | sort -V | tail -1)"

    if [[ -z "${FC}" ]]; then
        echo "Error: no versioned gfortran found under ${gcc_prefix}/bin/"
        exit 1
    fi

    export FC F77="${FC}" F90="${FC}" F95="${FC}"

    echo "Using Fortran compiler: ${FC}"
    "${FC}" --version
}


install_linux_dependencies() {
    echo "Installing Linux dependencies..."

    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y \
            git \
            make \
            build-essential \
            gfortran

    elif command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y \
            git \
            make \
            gcc \
            gcc-c++ \
            gcc-gfortran

    elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y \
            git \
            make \
            gcc \
            gcc-c++ \
            gcc-gfortran

    elif command -v pacman >/dev/null 2>&1; then
        sudo pacman -Sy --needed \
            git \
            make \
            base-devel \
            gcc-fortran

    else
        echo "Unsupported Linux distribution."
        exit 1
    fi
}


install_macos_dependencies() {
    echo "Installing macOS dependencies..."

    # Xcode command line tools open a GUI dialog — they can't be
    # installed non-interactively. Fail early in CI/SSH sessions.
    if ! xcode-select -p >/dev/null 2>&1; then
        if [[ -n "${CI:-}" || ! -t 0 ]]; then
            echo "Error: Xcode command line tools are not installed."
            echo "Run 'xcode-select --install' in an interactive terminal first."
            exit 1
        fi

        echo "Installing Xcode command line tools..."
        xcode-select --install || true

        echo "Waiting for Xcode tools installation..."
        until xcode-select -p >/dev/null 2>&1; do
            sleep 10
        done
    fi

    if ! command -v brew >/dev/null 2>&1; then
        echo "Installing Homebrew..."
        /bin/bash -c \
            "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

        eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || true)"
        eval "$(/usr/local/bin/brew shellenv  2>/dev/null || true)"
    fi

    # 'git' and 'make' are already provided by Xcode tools; 'gcc' brings gfortran.
    # Redirect stdin so Homebrew's tty? check returns false, suppressing the
    # "do you want to proceed?" prompt for dependency upgrades.
    brew install gcc </dev/null

    resolve_gfortran
}


patch_macos_makefiles() {
    echo "Patching macOS linker issues..."

    cd "${REPO_DIR}/prj"

    # Replace deprecated -macosx_version_min with -macos_version_min
    grep -rl -- "-macosx_version_min" . \
        | xargs sed -i '' \
        's/-macosx_version_min/-macos_version_min/g' \
        || true

    # Add -Wl,-ld_classic for modern macOS linker compatibility.
    # Guard with a negative grep so re-runs don't double-add the flag.
    grep -rl -- "-lSystem" . \
        | xargs grep -L "ld_classic" \
        | xargs sed -i '' \
        's/-lSystem/-Wl,-ld_classic -lSystem/g' \
        || true

    # Override the Fortran compiler in any Makefile that sets FC.
    # Use | as the sed delimiter to avoid conflicts with path slashes.
    find . -type f -name "Makefile*" -exec \
        sed -i '' \
        "s|^FC *=.*|FC=${FC}|" {} \; \
        || true
}


clone_repository() {
    # Check for .git specifically — INSTALL_DIR may already exist as an
    # empty directory from a previous failed run, which would fool a
    # plain 'test -d' check and make 'git pull' fail.
    if [[ -d "${REPO_DIR}/.git" ]]; then
        echo "EddyPro engine already exists. Updating repository..."
        cd "${REPO_DIR}"
        git pull origin HEAD
    else
        echo "Cloning EddyPro engine..."
        # --depth 1 is sufficient for a build-only install
        git clone --depth 1 "${REPO_URL}" "${REPO_DIR}"
    fi
}


build_eddypro() {
    cd "${REPO_DIR}/prj"

    echo "Building RP..."
    # 'make clean' may legitimately fail on a fresh tree
    make clean || true
    make rp

    echo "Building FCC..."
    make fcc

    echo
    echo "EddyPro build complete."
}


# ── pre-flight ─────────────────────────────────────────────────────────────────
command -v git >/dev/null 2>&1 || {
    echo "Error: git is not installed or not on PATH."
    exit 1
}


# ── install dependencies ───────────────────────────────────────────────────────
case "${OS}" in
    Linux)
        install_linux_dependencies
        ;;
    Darwin)
        install_macos_dependencies
        ;;
esac


# ── on re-runs on macOS, FC may not have been set yet ─────────────────────────
if [[ "${OS}" = "Darwin" ]] && [[ -z "${FC:-}" ]]; then
    resolve_gfortran
fi


# ── clone / update ─────────────────────────────────────────────────────────────
clone_repository


# ── macOS-specific Makefile patches ───────────────────────────────────────────
if [[ "${OS}" = "Darwin" ]]; then
    patch_macos_makefiles
fi


# ── build ──────────────────────────────────────────────────────────────────────
build_eddypro


# ── verify ─────────────────────────────────────────────────────────────────────
test -x "${INSTALL_DIR}/bin/${SYSTEM}/eddypro_rp"  \
    || { echo "Error: eddypro_rp binary not found or not executable."; exit 1; }
test -x "${INSTALL_DIR}/bin/${SYSTEM}/eddypro_fcc" \
    || { echo "Error: eddypro_fcc binary not found or not executable."; exit 1; }

echo
echo "Installation finished."
echo "Source directory: ${REPO_DIR}"
echo "Binaries:         ${INSTALL_DIR}/bin/${SYSTEM}/"