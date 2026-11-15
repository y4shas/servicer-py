# servicer-py

A Python port of [servicer](https://github.com/servicer-labs/servicer/tree/master) — a dead-simple CLI for managing systemd services without touching `.service` files by hand.

## Install

Install with [pipx](https://pipx.pypa.io/), which keeps the application in an isolated environment:

```sh
sudo pipx install --global .
# Or install directly from GitHub
sudo pipx install --global --system-site-packages git+https://github.com/y4shas/servicer-py.git
```

The global install puts `ser` on the system path, so it is available to commands run with `sudo`.

## Usage

```sh
# Create a service (auto-detects python3/node from extension)
sudo ser create app.py --name my-app --start --enable

# Pass env vars or extra args
sudo ser create app.py --env-vars "PORT=3000 DEBUG=1"
sudo ser create app.py -- --port 3000

# Custom interpreter
sudo ser create app.ts --interpreter ts-node

# Control
sudo ser start my-app
sudo ser stop my-app
sudo ser restart my-app   # stop + start
sudo ser enable my-app
sudo ser disable my-app

# Info
sudo ser status           # table with PID, state, cpu%, memory
sudo ser logs my-app
sudo ser logs my-app --follow
sudo ser cat my-app       # print .service file
sudo ser which my-app     # print file paths

# Edit the .service file directly
sudo ser edit my-app --editor vim

# Rename (restarts if running)
sudo ser rename my-app better-name
sudo ser mv my-app better-name    # alias

# Delete
sudo ser delete my-app
sudo ser rm my-app        # alias
```

Services are stored as `/etc/systemd/system/<name>.ser.service`. You can write your own `.service` files and manage them with `ser` — just name them `*.ser.service`.

## Requirements

- Linux with systemd
- Python 3.10+
- Run with `sudo` for most commands (same as the original)

---

## vs. the original Rust version

| | [servicer (Rust)](https://github.com/servicer-labs/servicer) | servicer-py |
|---|---|---|
| Install | `cargo install` or download binary | `pip install` or `pipx` |
| Runtime | None (compiled binary) | Python 3.10+ |
| Async | tokio everywhere | Synchronous (simpler, no overhead for a CLI) |
| D-Bus | zbus | dasbus |
| Tables | cli_table | rich (colors, better formatting) |
| Byte sizes | bytesize crate | humanize |
| `ser logs` | Pipes stdout line-by-line through its own reader | `subprocess.run` inherits stdout directly — no buffering issues with `--follow` |
| Errors | `panic!()` | Friendly message + clean exit |
| Unknown extension | panic | Error message suggesting `--interpreter` |
