FROM ubuntu:24.04 AS build

RUN apt-get update && apt-get -y install cmake git curl zip unzip tar ninja-build build-essential libuv1-dev pkg-config

RUN git clone https://github.com/microsoft/vcpkg.git

RUN /vcpkg/bootstrap-vcpkg.sh

ENV VCPKG_ROOT=/vcpkg

ENV CMAKE_TOOLCHAIN_FILE=/vcpkg/scripts/buildsystems/vcpkg.cmake

COPY vcpkg.json .

RUN /vcpkg/vcpkg install

WORKDIR /app

COPY . .

RUN cmake --preset default \
-DCMAKE_TOOLCHAIN_FILE=/vcpkg/scripts/buildsystems/vcpkg.cmake \
-DCMAKE_BUILD_TYPE=Release \
-DCMAKE_CXX_FLAGS_RELEASE="-Ofast"

RUN cmake --build build
