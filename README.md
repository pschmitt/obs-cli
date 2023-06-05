# obs-cli

Yes, this is yet another obs-cli implementation.

This one:

- is written in Python 3, powered by [rich](https://github.com/Textualize/rich) 
and [obswd-python](https://pypi.org/project/obsws-python/)
- 😮 Supports the *new websocket* API only

## Installation

```shell
pipx install obs-cli
```

## Usage

```
obs-cli --help
usage: obs_cli.py [-h] [-D] [-q] [-H HOST] [-P PORT] [-p PASSWORD] [-j]
                  {scene,item,input,filter,hotkey} ...

positional arguments:
  {scene,item,input,filter,hotkey}

options:
  -h, --help            show this help message and exit
  -D, --debug
  -q, --quiet
  -H HOST, --host HOST  host name
  -P PORT, --port PORT  port number
  -p PASSWORD, --password PASSWORD
                        password ($OBS_API_PASSWORD)
  -j, --json
```
