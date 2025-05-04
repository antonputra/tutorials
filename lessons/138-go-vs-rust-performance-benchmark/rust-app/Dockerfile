FROM amd64/rust:1.65.0-bullseye as build

WORKDIR /app

COPY . .

RUN cargo build --release

FROM debian:11.5-slim

COPY --from=build /app/target/release/rust-app /rust-app

CMD ["/rust-app"]
