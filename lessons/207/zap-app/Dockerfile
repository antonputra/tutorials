FROM debian:12.7 AS build

ARG ZIG_VER=0.14.0-dev.1511+54b668f8a

RUN apt-get update && apt-get install -y curl xz-utils

RUN curl https://ziglang.org/builds/zig-linux-$(uname -m)-${ZIG_VER}.tar.xz -o zig-linux.tar.xz && \
    tar xf zig-linux.tar.xz && \
    mv zig-linux-$(uname -m)-${ZIG_VER}/ /opt/zig

WORKDIR /app

COPY . .

RUN /opt/zig/zig build -Doptimize=ReleaseFast -Dcpu=baseline

FROM debian:12.6-slim

RUN apt-get update && apt-get install -y ca-certificates

COPY --from=build /app/zig-out/bin/zap-app /server

CMD ["/server"]
