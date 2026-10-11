#!/bin/sh
# Rebuild the patched MicroPython for the GT Trackball (Pico 2 W).
#
#   ./build.sh [workdir]
#
# Needs git, make, cmake and the Arm GNU toolchain (arm-none-eabi-gcc)
# on PATH, e.g. from developer.arm.com (tested: 15.2.rel1). Result:
#   <workdir>/micropython/ports/rp2/build-RPI_PICO2_W/firmware.uf2
set -e

HERE=$(cd "$(dirname "$0")" && pwd)
WORK=${1:-$HERE/build}
TAG=v1.29.0

mkdir -p "$WORK"
cd "$WORK"
if [ ! -d micropython ]; then
    git clone --depth 1 --branch "$TAG" https://github.com/micropython/micropython.git
fi
cd micropython
git checkout -- .                       # start from the pristine tag
git apply "$HERE/gt-trackball-micropython-$TAG.patch"
make -C mpy-cross -j8
make -C ports/rp2 BOARD=RPI_PICO2_W submodules
make -C ports/rp2 BOARD=RPI_PICO2_W -j8
ls -l ports/rp2/build-RPI_PICO2_W/firmware.uf2
