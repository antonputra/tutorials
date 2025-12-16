FROM ubuntu:24.04 AS build

# Set working directory
WORKDIR /app

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    curl \
    zip \
    unzip \
    tar \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install vcpkg
RUN git clone https://github.com/microsoft/vcpkg.git /opt/vcpkg \
    && /opt/vcpkg/bootstrap-vcpkg.sh \
    && ln -s /opt/vcpkg/vcpkg /usr/local/bin/vcpkg

# Copy project files
COPY . /app

# # Create build directory
RUN rm -rf build && mkdir -p build

# Configure project with CMake using vcpkg toolchain
WORKDIR /app/build

RUN cmake .. -DCMAKE_TOOLCHAIN_FILE=/opt/vcpkg/scripts/buildsystems/vcpkg.cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS_RELEASE="-O3 -ffast-math"

# Build the project
RUN cmake --build . --parallel 10 --config Release

FROM ubuntu:24.04

COPY --from=build /app/build/protobuf /protobuf
COPY --from=build /app/build/json /json
