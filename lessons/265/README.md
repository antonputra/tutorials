# Rust vs C++ Performance: Can Rust Actually Be Faster? (Pt. 2)

You can find tutorial [here](https://youtu.be/5-sDEDBJPlY).

## Commands

```bash
## C++
cmake --preset default -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS_RELEASE="-O3 -ffast-math"
cmake --build build && ./build/app

## Rust
cargo build --release
```
