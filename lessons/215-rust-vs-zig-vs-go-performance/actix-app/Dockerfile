FROM rust:1.81.0-bookworm AS build

WORKDIR /app

COPY . .

ENV RUSTFLAGS="-Ctarget-cpu=native"

RUN cargo build --release

FROM debian:12.7-slim

RUN apt-get update && apt-get install -y ca-certificates

COPY --from=build /app/target/release/actix-app /server

CMD ["/server"]
