# 🎬🎥 OBS CLI

`obs-cli` is a command-line interface for OBS Studio.

It allows you to control OBS Studio from the command line, making it easier to
automate scene switching, source toggling, and more.

This implementation of `obs-cli` is:

- written in Python 3
- powered by [rich](https://github.com/Textualize/rich),
  [rich-argparse](https://github.com/hamdanal/rich-argparse), and
  [obsws-python](https://pypi.org/project/obsws-python/).

⚠️ Only the new OBS WebSocket API (v5) is supported!

## 💻 Installation

```shell
# uv (recommended)
uv tool install obs-cli

# pip
pip install --user obs-cli
```

## 🛠️ Usage

```shell
obs-cli --help
```

Global flags (`-H`, `-P`, `-p`, `-j`, `-q`, `-D`) can be placed before or
after the subcommand name. Subcommands also accept plural forms (`scenes`,
`items`, `groups`, etc.) and default to `list` (or `status` for stateful
commands) when no action is given.

```shell
obs-cli scenes               # same as: obs-cli scene list
obs-cli items --json         # JSON output
obs-cli --json scene list    # equivalent
```

## 🌟 Features

### 🎞️ Scene Management

```shell
obs-cli scene --help
```

```shell
# List all scenes (INDEX / NAME / CURRENT columns)
obs-cli scene list
obs-cli scenes               # plural alias

# Switch to a scene
obs-cli scene switch "Scene2"

# Print the current scene name
obs-cli scene current

# Screenshot — current scene or a named one
obs-cli scene screenshot -o scene.png
obs-cli scene screenshot "Scene2" -o scene2.png
obs-cli scene screenshot --raw > scene.png   # raw bytes to stdout
obs-cli scene screenshot --json              # base64-encoded JSON
```

### 📦 Item Management

```shell
obs-cli item --help
```

```shell
# List all items in the current (or a named) scene
obs-cli item list
obs-cli item list --scene "Scene2"
obs-cli items                # plural alias

# Show / hide / toggle a source
obs-cli item show --scene "Scene2" "Item1"
obs-cli item hide --scene "Scene2" "Item1"
obs-cli item toggle "Item1"

# Screenshot a source
obs-cli item screenshot "Webcam" -o webcam.png
obs-cli item screenshot "Webcam" --raw > webcam.png
obs-cli item screenshot "Webcam" --json
obs-cli item screenshot "Webcam" -f jpg -o webcam.jpg
```

### 📂 Group Management

```shell
obs-cli group --help
```

```shell
# List all groups in a scene
obs-cli group list
obs-cli group list --scene "Scene2"
obs-cli groups               # plural alias

# Show / hide / toggle a group
obs-cli group show --scene "Scene2" "group1"
obs-cli group hide --scene "Scene2" "group1"
obs-cli group toggle "group1"
```

### 🎤 Input Management

```shell
obs-cli input --help
```

```shell
# List all inputs
obs-cli input list
obs-cli inputs               # plural alias

# Show all settings for an input
obs-cli input get "Mic/Aux"

# Get a single property
obs-cli input get "Webcam" device_id

# Set a property
obs-cli input set "Webcam" device_id /dev/v4l/by-id/usb-Elgato_Elgato_Facecam_FW52K1A04919-video-index0

# Mute / unmute / toggle
obs-cli input mute "Mic/Aux"
obs-cli input unmute "Mic/Aux"
obs-cli input toggle-mute "Mic/Aux"
obs-cli input is-muted "Mic/Aux"
```

### 🎨 Filter Management

```shell
obs-cli filter --help
```

```shell
# List filters on a source
obs-cli filter list "Mic/Aux"
obs-cli filters              # plural alias (current scene)

# Enable / disable / toggle
obs-cli filter enable  "Mic/Aux" "Filter1"
obs-cli filter disable "Mic/Aux" "Filter1"
obs-cli filter toggle  "Mic/Aux" "Filter1"

# Check status (exits 0 if enabled, 1 if disabled)
obs-cli filter status "Mic/Aux" "Filter1"
obs-cli -q filter status "Mic/Aux" "Filter1"
```

### ⌨️ Hotkey Management

```shell
obs-cli hotkey --help
```

```shell
# List all hotkeys
obs-cli hotkey list
obs-cli hotkeys              # plural alias

# Trigger a hotkey
obs-cli hotkey trigger "OBSBasic.StartStreaming"
```

### 🎥 Virtual Camera

```shell
obs-cli virtualcam status
obs-cli virtualcam start
obs-cli virtualcam stop
obs-cli virtualcam toggle
```

### 📡 Stream Management

```shell
obs-cli stream status
obs-cli stream start
obs-cli stream stop
obs-cli stream toggle
```

### 📹 Recording

```shell
obs-cli record status
obs-cli record start
obs-cli record stop
obs-cli record toggle
```

### 🔁 Replay Buffer

```shell
obs-cli replay status
obs-cli replay start
obs-cli replay stop
obs-cli replay toggle
obs-cli replay save
```

## 📄 License

This project is licensed under the GPL-3.0 License.

See [LICENSE](LICENSE) for more information.
