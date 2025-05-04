# Rust vs C++ Performance

You can find tutorial [here](https://youtu.be/WnMin9cf78g).

## Commands

```bash
# C++

git clone --depth 1 --branch v1.9.9 https://github.com/drogonframework/drogon
cd drogon
git submodule update --init
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make && sudo make install

cd /tmp/drogon-app/build
cmake -DCMAKE_BUILD_TYPE=Release ..
make

## Rust
curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh -s -- -y
cd /tmp/rust-app
source $HOME/.cargo/env && cargo build --release
```
