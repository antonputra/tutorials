FROM rust:1.80.1-bookworm AS build

WORKDIR /app

COPY . .

RUN cargo build --release

FROM debian:12.6-slim

RUN apt-get update && apt-get install -y ca-certificates

COPY --from=build /app/target/release/rust-app-v2 /rust-app-v2

CMD ["/rust-app-v2"]
