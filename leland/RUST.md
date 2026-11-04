# Rust for Swift developers (the short version)

Written 2026-11-04 for me (Leland): I know Swift well. Rust is the language the duck's software is
written in, and it's now installed on the laptop and the Studio.

## The short version

- **Rust is Swift's stricter cousin.** It's compiled, fast, type-safe, with `enum`s that carry data,
  `Option` and `Result`, and traits that work like protocols. Most Swift ideas carry straight over.
- **The one new idea is ownership.** Swift counts references at runtime (ARC). Rust works out
  *at compile time* who owns each value and when it's freed. There's no garbage collector, no ARC,
  and no pauses. That's why it's used on a robot that must hit 50 control ticks a second.
- **The compiler is strict, and that's the point.** If a program compiles, whole kinds of bugs are
  ruled out: use-after-free, data races between threads, and forgotten error cases.
- **Cargo is SwiftPM, but nicer.** It builds, tests, fetches libraries ("crates"), and runs the linter.
- **You don't need to write Rust to use the duck.** You drive it with `duck-sim`, `robotctl` and the
  apps. Rust matters if you want to read *how* the duck works or change it.

## What the duck uses Rust for

This repo is a Cargo **workspace**: one folder per program or library, about 147,000 lines in all.
The ones worth knowing:

| Crate | What it is |
|---|---|
| `robotd` | The brain stem. It runs the trained policy (the `.onnx` file) 50 times a second and drives the motors. |
| `mediad` | Camera and WebRTC video. |
| `btd` | Bluetooth, for phone pairing and control. |
| `robotctl`, `duckctl` | Command-line tools you type at. |
| `updater` | Installs new releases on the robot. |
| `kinematics`, `odometry` | Leg geometry, and working out where the duck has walked. |

The *training* (Python, MuJoCo, PPO) is not Rust. Rust is what runs on the robot. Python is what
teaches the brain that Rust then runs.

## Swift → Rust phrasebook

| Swift | Rust | Notes |
|---|---|---|
| `let x = 5` | `let x = 5;` | Constant by default, like Swift. Semicolons matter. |
| `var x = 5` | `let mut x = 5;` | "mut" = mutable. |
| `func add(a: Int, b: Int) -> Int` | `fn add(a: i64, b: i64) -> i64` | Sized number types: `i32`, `u8`, `f32`… |
| `struct` | `struct` | Methods go in a separate `impl` block. |
| `enum` with associated values | `enum` | Same idea, used everywhere. |
| `switch` | `match` | Must cover every case, like Swift. |
| `Optional<T>`, `nil` | `Option<T>`: `Some(x)` / `None` | No `?.` chaining sugar for nil, but `?` works (below). |
| `throws` / `try` | `Result<T, E>`: `Ok(x)` / `Err(e)` | Errors are ordinary return values, not exceptions. |
| `try foo()` | `foo()?` | `?` means "if this failed, return the error now". |
| `protocol` | `trait` | `impl Display for Duck` ≈ `extension Duck: CustomStringConvertible`. |
| generics `<T: Equatable>` | `<T: PartialEq>` | Very close. |
| `[Int]`, `[String: Int]` | `Vec<i64>`, `HashMap<String, i64>` | |
| `String` | `String` (owned) and `&str` (borrowed) | Two string types: see ownership. |
| `print("hi \(x)")` | `println!("hi {x}");` | The `!` means it's a *macro*, code that writes code. |
| `.map { $0 * 2 }` | `.map(\|x\| x * 2)` | Closures use `\|args\|`. |
| SwiftPM, `Package.swift` | Cargo, `Cargo.toml` | |
| XCTest | `#[test]` + `cargo test` | Tests often sit in the same file. |

## A real function from the duck

From [`robotd/src/control.rs`](../robotd/src/control.rs). Someone asks the duck to pick something up off the ground:

```rust
pub fn start_ground_pick(&mut self) -> Result<(), &'static str> {
    if !self.policy.has_ground_pick() {
        return Err("no ground-pick policy loaded");
    }
    if let Some(reason) = self.move_blocked() {
        return Err(reason);
    }
    self.ground_pick = Some(0.0);
    Ok(())
}
```

In Swift you'd read it as:

- `pub fn` = `public func`. `&mut self` = a `mutating func`: it's allowed to change the controller.
- `-> Result<(), &'static str>` = "returns nothing on success, or an error message". Roughly
  `throws`, but the error is a value the caller *must* deal with. The compiler warns if they ignore it.
- `if let Some(reason) = …` is exactly Swift's `if let reason = …`.
- `self.ground_pick = Some(0.0)` sets an Optional. It means "a pick has started, 0 seconds in".
- `Ok(())` at the end, with no `return` and no semicolon: the last expression is the return value.

## Ownership in five minutes (the part that's actually new)

Three rules:

1. **Every value has exactly one owner** (a variable). When the owner goes out of scope, the value is
   freed, right then. Like Swift's `deinit`, but certain and free.
2. **Assigning or passing a value *moves* it.** `let b = a;` and now `a` can't be used. The compiler
   stops you. (Small simple types like numbers are copied instead.) This is like Swift's new
   `consuming` / non-copyable types, but it's the default for everything.
3. **You can *borrow* instead of moving:** `&x` lends it read-only, `&mut x` lends it for changing.
   You can have **many readers OR one writer, never both at once.** This is Swift's "exclusive
   access" rule, enforced fully at compile time.

The "borrow checker" is the part of the compiler that enforces rule 3. Newcomers spend their first
weeks arguing with it. It's almost always pointing at a real problem, usually two parts of the
program changing the same thing at once.

**Why the two strings?** `String` is a string you own (you can grow it). `&str` is a borrowed view
of someone else's text. `&'static str` (in the example above) is text baked into the program that
lives forever, so it's safe to hand out anywhere.

**When you really need shared ownership** (like Swift classes), Rust has opt-in versions:
`Rc<T>` / `Arc<T>` are reference counting, which is ARC by hand. `Mutex<T>` gives safe shared
changes across threads.

## Cargo commands you'll actually type

Run these in `~/microduck`, after `. "$HOME/.cargo/env"` if the shell can't find `cargo`.

| Command | What it does |
|---|---|
| `cargo build` | Compile everything (debug). Output in `target/`. |
| `cargo build --release` | Optimised build, slower to compile and faster to run. |
| `cargo run -p robotctl -- --help` | Build and run one program; args after `--` go to it. |
| `cargo test -p kinematics` | Run one crate's tests. |
| `cargo clippy` | The linter, which is very good at teaching Rust style. |
| `cargo fmt` | Auto-format, like swift-format. |
| `cargo doc --open` | Build HTML docs for the code and every library, and open them. |
| `cargo clean` | Delete `target/` (frees ~2 GB; the next build re-creates it). |

`scripts/duck-sim` runs `cargo build` for you, which is why it "just worked".

## Habits that make Rust easier

- **Read compiler errors in full.** Rust's are famously helpful, and often end with "help: try this".
- **Use `.clone()` freely while learning.** It copies a value to dodge the borrow checker. Slightly
  slower and almost always fine. Tidy up later.
- **`unwrap()` is Swift's `!`.** "I'm sure this isn't `None` or `Err`, crash if I'm wrong." Fine in
  experiments; the duck's code avoids it on the robot.
- **VS Code:** install the **rust-analyzer** extension. It's the equivalent of Xcode's live errors,
  jump-to-definition and autocomplete.

## Where to learn more

- **"The Rust Programming Language"** ("the Book"), free, and also on your machine: `rustup doc --book`.
  Chapters 4 (ownership) and 6 (enums and match) are the ones a Swift developer needs most.
- **Rustlings**: small exercises you fix until they compile. Good for an evening.
- **Rust by Example**: `rustup doc --rust-by-example`.
- In this repo: [`CONTRIBUTING.md`](../CONTRIBUTING.md) (how Pollen builds and tests) and
  [`docs/design/architecture.md`](../docs/design/architecture.md) (which daemon does what).

## Summary

Rust ≈ Swift with no ARC. The compiler tracks who owns each value, which makes it fast and safe
enough to run a walking robot. The Swift ideas (`enum`, `match`, `Option`, `Result`, traits ≈
protocols, generics) carry straight over. The new part is ownership and borrowing: one owner, and
many readers *or* one writer. Cargo does all the building. You only need it if you want to read or
change how the duck works.
