# 🎬🎥 OBS CLI

`obs-cli` is a command-line interface for OBS Studio. It allows you to control OBS Studio from the command line, making it easier to automate scene switching, source toggling, and more.

This implementation of `obs-cli` is written in Python 3 and powered by [rich](https://github.com/Textualize/rich) and [obsws-python](https://pypi.org/project/obsws-python/). It supports the new OBS WebSocket API only.

## 💻 Installation

You can install `obs-cli` using pip:

```shell
pipx install obs-cli
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
obs-cli scene switch --scene "Scene2"
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
obs-cli item hide --scene "Scene2" --item "Item1"
```

And to show it:

```shell
obs-cli item show --scene "Scene2" --item "Item1"
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
obs-cli input get --input "Mic/Aux"
```

To list all inputs:

```shell
obs-cli input list
```

### 🎨 Filter Management

You can manage filters using the `filter` command:

```shell
obs-cli filter --help
```

For example, to enable a filter named "Filter1" on an input named "Mic/Aux":

```shell
obs-cli filter enable --input "Mic/Aux" --filter "Filter1"
```

And to disable it:

```shell
obs-cli filter disable --input "Mic/Aux" --filter "Filter1"
```

To list all filters on an input:

```shell
obs-cli filter list --input "Mic/Aux"
```

### ⌨️ Hotkey Management

You can manage hotkeys using the `hotkey` command:

```shell
obs-cli hotkey --help
```

For example, to trigger a hotkey named "Hotkey1":

```shell
obs-cli hotkey trigger --hotkey "Hotkey1"
```

To list all hotkeys:

```shell
obs-cli hotkey list
```

## 📄 License

This project is licensed under the GPL-3.0 License. See [LICENSE](LICENSE) for more information.

