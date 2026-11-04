# Rust for a JavaScript (and old Objective-C) developer

Written 2026-11-04 for me (Leland). These days I mostly write JavaScript, and years ago I wrote
Objective-C. Rust is the language the duck's software is written in, and it's now installed on the
laptop and the Studio.

## The short version

- **Rust is like TypeScript taken all the way.** Every value has a type, the compiler checks them
  all, and it compiles to a fast native program with no runtime or engine underneath. There's no
  Node, no V8, no `any` escape hatch.
- **No garbage collector.** JavaScript cleans up memory for you while the program runs, with
  occasional pauses. Objective-C made *you* do it (`retain` / `release`), and forgetting meant
  crashes or leaks. **Rust has the compiler do it.** It works out when each value is no longer
  needed and frees it right there. Nothing pauses, nothing leaks, and there's no bookkeeping by hand.
- **The rules that make that possible are called ownership.** They're the only truly new idea, and
  the thing everyone finds hard for a few weeks. They're explained below.
- **No `null` or `undefined`, and no exceptions.** A value that might be missing is an `Option`.
  An operation that might fail returns a `Result`. The compiler makes you handle both.
- **Cargo is npm.** It builds, tests, downloads libraries ("crates", like npm packages) and runs
  the linter. `Cargo.toml` is `package.json`.
- **You don't need to write Rust to use the duck.** You drive it with `duck-sim`, `robotctl` and
  the apps. Rust matters if you want to read *how* the duck works or change it.

## What the duck uses Rust for

This repo is a Cargo **workspace**: one folder per program or library, like an npm monorepo with
workspaces. It's about 147,000 lines in all. The parts worth knowing:

| Crate | What it is |
|---|---|
| `robotd` | The brain stem. It runs the trained policy (the `.onnx` file) 50 times a second and drives the motors. |
| `mediad` | Camera and WebRTC video. |
| `btd` | Bluetooth, for phone pairing and control. |
| `robotctl`, `duckctl` | Command-line tools you type at. |
| `updater` | Installs new releases on the robot. |
| `kinematics`, `odometry` | Leg geometry, and working out where the duck has walked. |

**Why Rust and not JavaScript on the robot?** The motors need a new command every 20 ms, every
time. A garbage-collector pause at the wrong moment and the duck stumbles. Rust has no such pauses
and runs at C speed, on a small board.

The *training* (Python, MuJoCo, PPO) is not Rust. Python teaches the brain; Rust runs it.

## JavaScript → Rust phrasebook

| JavaScript | Rust | Notes |
|---|---|---|
| `const x = 5` | `let x = 5;` | Can't be changed, and that's the default. Semicolons matter. |
| `let x = 5` | `let mut x = 5;` | "mut" = mutable: you must ask to change a variable. |
| `function add(a, b) { return a + b }` | `fn add(a: i64, b: i64) -> i64 { a + b }` | Types are required on functions. The last line with no `;` is the return value. |
| `number` | `i32`, `i64`, `u8`, `f32`, `f64`… | Whole numbers and decimals are different types; `u` = no negatives. |
| `{ name: "Duck", legs: 2 }` | `struct Duck { name: String, legs: u8 }` | Like a TypeScript `interface`, but it's the real object. |
| class methods | `impl Duck { fn walk(&self) { … } }` | Data and methods are declared separately. No classes, no inheritance. |
| `"sit" \| "stand" \| "walk"` (TS union) | `enum Pose { Sit, Stand, Walk }` | Rust enums can also carry data: `Walk { speed: f32 }`. |
| `switch` | `match` | Must cover every case, or it won't compile. |
| `null` / `undefined` | `Option<T>`: `Some(x)` or `None` | You can't use the value without checking first. |
| `throw` / `try…catch` | `Result<T, E>`: `Ok(x)` or `Err(e)` | Errors are ordinary return values. |
| `await foo()` that may reject | `foo()?` | `?` means "if this failed, return the error now". It reads like `await` does. |
| TS `interface` that a class implements | `trait` | Shared behaviour: `impl Display for Duck` lets a duck be printed. |
| `[1, 2, 3]` | `vec![1, 2, 3]` (a `Vec`) | All items are the same type. |
| `new Map()` | `HashMap::new()` | |
| `` `hi ${x}` `` | `format!("hi {x}")` | The `!` means it's a *macro*, code that writes code. |
| `console.log(...)` | `println!(...)` | |
| `arr.map(x => x * 2)` | `v.iter().map(\|x\| x * 2)` | Arrow functions are written `\|x\| …`. |
| `npm install`, `package.json` | `cargo build`, `Cargo.toml` | Cargo downloads dependencies on first build. |
| Jest / Mocha | `#[test]` + `cargo test` | Tests often sit in the same file as the code. |
| ESLint / Prettier | `cargo clippy` / `cargo fmt` | |

## A real function from the duck

From [`robotd/src/control.rs`](../robotd/src/control.rs). It runs when someone asks the duck to
pick something up off the ground:

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

Read as JavaScript:

```js
startGroundPick() {
  if (!this.policy.hasGroundPick()) {
    throw new Error("no ground-pick policy loaded");
  }
  const reason = this.moveBlocked();
  if (reason !== null) throw new Error(reason);
  this.groundPick = 0.0;
}
```

Line by line:

- `pub fn` = an exported function. `&mut self` = it's a method (`self` is `this`), and it's allowed
  to change the object.
- `-> Result<(), &'static str>` = "returns nothing on success, or an error message". `()` means
  "nothing", like `void`. Unlike `throw`, the error is a value the caller must deal with. The
  compiler warns if they ignore it.
- `if let Some(reason) = …` = "if this gives back a value, call it `reason` and run the block".
  It's the null check and the variable in one line.
- `self.ground_pick = Some(0.0)` = "a pick has started, 0 seconds in". `None` would mean "no pick".
- `Ok(())` at the end, with no `return` and no semicolon, is the return value: "it worked".

## Ownership in five minutes (the part that's actually new)

**Where it comes from.** In Objective-C (before ARC), you `retain`ed an object to keep it alive and
`release`d it when done. Forget a release: leak. Release twice: crash. JavaScript fixed that with a
garbage collector, which costs speed and pauses. Rust fixes it with three rules the compiler checks:

1. **Every value has exactly one owner** (a variable). When the owner's `{ }` block ends, the value
   is freed, automatically and right then. Rust writes the `release` for you, in exactly the right
   place.
2. **Assigning or passing a value *moves* it.** After `let b = a;`, `a` is empty and the compiler
   won't let you touch it. This is the big surprise coming from JavaScript, where `b = a` just
   makes two names for the same object. (Small simple things like numbers are copied instead.)
3. **You can *borrow* instead of moving.** `&x` lends it read-only and `&mut x` lends it for
   changing. The borrower gives it back when done. The rule: **many readers OR one writer, never
   both at once.**

Rule 3 is what the "borrow checker" enforces, and it's what newcomers argue with. It stops a whole
family of bugs JavaScript lets through. One example is changing an array while another part of the
code is looping over it. With threads it's worse: two threads changing the same thing at once.
In Rust that won't compile.

**Why there are two kinds of string.** `String` is text you own (you can add to it). `&str` is a
borrowed, read-only view of someone else's text. `&'static str` in the example above is text baked
into the program itself, so it lives forever and is safe to hand out anywhere.

**When you really need shared objects**, as in JavaScript where many things point at one object,
Rust has opt-in versions. `Rc<T>` / `Arc<T>` are reference counting, which is Objective-C's
retain/release done for you. `Mutex<T>` gives safe changes from several threads.

## Cargo commands you'll actually type

Run these in `~/microduck`, after `. "$HOME/.cargo/env"` if the shell can't find `cargo`.

| Command | npm feel | What it does |
|---|---|---|
| `cargo build` | `npm run build` | Compile everything (debug). Output goes in `target/`, like `dist/`. |
| `cargo build --release` | production build | Optimised: slower to compile, much faster to run. |
| `cargo run -p robotctl -- --help` | `npm run … -- --help` | Build and run one program. Args after `--` go to it. |
| `cargo test -p kinematics` | `npm test` | Run one crate's tests. |
| `cargo clippy` | ESLint | The linter. Very good at teaching Rust style. |
| `cargo fmt` | Prettier | Auto-format. |
| `cargo doc --open` | | Build HTML docs for the code and every library, and open them. |
| `cargo clean` | `rm -rf dist node_modules` | Delete `target/` (frees ~2 GB; the next build re-creates it). |

`scripts/duck-sim` runs `cargo build` for you, which is why it "just worked".

## Habits that make Rust easier

- **Read compiler errors in full.** Rust's are famously helpful, and often end with "help: try this".
  Expect to spend more time getting code to compile, and much less time debugging it once it does.
- **Use `.clone()` freely while learning.** It makes a copy, so you dodge the ownership rules.
  Slightly slower, almost always fine. Tidy up later.
- **`unwrap()` means "I'm sure, crash if I'm wrong".** It takes the value out of an `Option` or
  `Result` without checking. Fine in experiments; the duck's code avoids it on the robot.
- **VS Code:** install the **rust-analyzer** extension. You get red squiggles, types on hover,
  jump-to-definition and autocomplete, like TypeScript in VS Code.

## Where to learn more

- **"The Rust Programming Language"** ("the Book"), free, and already on your Mac:
  `rustup doc --book`. Chapter 4 (ownership) is the one that matters. Chapter 6 (enums and
  `match`) is the second.
- **Rustlings**: small broken exercises you fix until they compile. Good for an evening.
- **Rust by Example**: `rustup doc --rust-by-example`. Short runnable snippets.
- In this repo: [`CONTRIBUTING.md`](../CONTRIBUTING.md) (how Pollen builds and tests) and
  [`docs/design/architecture.md`](../docs/design/architecture.md) (which program does what).

## Summary

Rust is like strict TypeScript that compiles to a fast native program. It has no garbage collector:
the compiler works out when to free memory, the job you once did by hand with `retain` / `release`
in Objective-C. That makes it fast and steady enough to run a walking robot. The new idea is
ownership: one owner, assignment *moves*, and you can borrow with many readers *or* one writer.
There's no `null` and no exceptions; `Option` and `Result` take their place. Cargo is npm.
You only need Rust to read or change how the duck works, not to use it.
