FROM rust:1.66.1-bullseye as build

WORKDIR /app

RUN apt update && apt install -y protobuf-compiler libprotobuf-dev

COPY . .

RUN cargo build --release

FROM debian:11.6-slim

COPY --from=build /app/target/release/hardware-server /hardware-server

CMD ["/hardware-server"]
