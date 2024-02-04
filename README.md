# 🎬🎥 OBS CLI

`obs-cli` is a command-line interface for OBS Studio.

It allows you to control OBS Studio from the command line, making it easier to
automate scene switching, source toggling, and more.

This implementation of `obs-cli` is:

- written in Python 3
- powered by [rich](https://github.com/Textualize/rich) and
[obsws-python](https://pypi.org/project/obsws-python/).

⚠️ Only the new OBS WebSocket API (v5) is supported!

## 💻 Installation

You can install `obs-cli` using pip(x):

```shell
# pipx
pipx install obs-cli

# pip
pip install --user obs-cli
```

## 🛠️ Usage

Here's the general usage of `obs-cli`:

```shell
obs-cli --help
```

This will show you the available commands and options.

## 🌟 Features

### 🎞️ Scene Management

You can manage scenes using the `scene` command:

```shell
obs-cli scene --help
```

For example, to switch to a scene named "Scene2":

```shell
obs-cli scene switch "Scene2"
```

To list all scenes:

```shell
obs-cli scene list
```

### 📦 Item Management

You can manage scene items using the `item` command:

```shell
obs-cli item --help
```

For example, to hide an item named "Item1" in a scene named "Scene2":

```shell
obs-cli item hide --scene "Scene2" "Item1"
```

And to show it:

```shell
obs-cli item show --scene "Scene2" "Item1"
```

To list all items in a scene:

```shell
obs-cli item list --scene "Scene2"
```

### 🎤 Input Management

You can manage inputs using the `input` command:

```shell
obs-cli input --help
```

For example, to get the settings of an input named "Mic/Aux":

```shell
obs-cli input get "Mic/Aux"
```

To set the device_id of a webcam input named "Webcam":

```shell
obs-cli input set "Webcam" device_id /dev/v4l/by-id/usb-Elgato_Elgato_Facecam_FW52K1A04919-video-index0
```

To list all inputs:

```shell
obs-cli input list
```

Mute/unmute or toggle the mute state of an input:

```shell
obs-cli input mute "Mic/Aux"
obs-cli input unmute "Mic/Aux"
obs-cli input toggle-mute "Mic/Aux"
```

### 🎨 Filter Management

You can manage filters using the `filter` command:

```shell
obs-cli filter --help
```

For example, to enable a filter named "Filter1" on an input named "Mic/Aux":

```shell
obs-cli filter enable "Mic/Aux" "Filter1"
```

And to disable it:

```shell
obs-cli filter disable "Mic/Aux" "Filter1"
```

To list all filters on an input:

```shell
obs-cli filter list "Mic/Aux"
```

### ⌨️ Hotkey Management

You can manage hotkeys using the `hotkey` command:

```shell
obs-cli hotkey --help
```

For example, to trigger a hotkey named "Hotkey1":

```shell
obs-cli hotkey trigger "Hotkey1"
```

To list all hotkeys:

```shell
obs-cli hotkey list
```

### 🎥 Virtual Camera Management

You can manage the virtual camera using the `virtualcam` command:

```shell
obs-cli virtualcam --help
```

For example, to start the virtual camera:

```shell
obs-cli virtualcam start
```

To stop the virtual camera:

```shell
obs-cli virtualcam stop
```

To toggle the virtual camera:

```shell
obs-cli virtualcam toggle
```

To get the status of the virtual camera:

```shell
obs-cli virtualcam status
```

### 📡 Stream Management

You can manage the stream using the `stream` command:

```shell
obs-cli stream --help
```

For example, to start streaming:

```shell
obs-cli stream start
```

To stop streaming:

```shell
obs-cli stream stop
```

To toggle streaming:

```shell
obs-cli stream toggle
```

To get the status of the stream:

```shell
obs-cli stream status
```

### 🎥 Record Management

You can manage recording using the `record` command:

```shell
obs-cli record --help
```

For example, to start recording:

```shell
obs-cli record start
```

To stop recording:

```shell
obs-cli record stop
```

To toggle recording:

```shell
obs-cli record toggle
```

To get the status of the recording:

```shell
obs-cli record status
```

## 📄 License

This project is licensed under the GPL-3.0 License.

See [LICENSE](LICENSE) for more information.
