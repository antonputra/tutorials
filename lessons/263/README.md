# Rust vs C++ Performance: Can Rust Actually Be Faster?

You can find tutorial [here](https://youtu.be/J6YVX7E5QPE).

## Commands

```bash
## C++
cmake --preset default -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS_RELEASE="-O3 -ffast-math"
cmake --build build && ./build/app

## Rust
cargo build --release
```
