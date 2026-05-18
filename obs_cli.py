#!/usr/bin/env python
# coding: utf-8

import argparse
import base64
import json
import logging
import os
import re
import sys
from importlib import metadata

import obsws_python as obs
from rich import print, print_json
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich_argparse import RichHelpFormatter


def get_version():
    pyproject = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "pyproject.toml",
    )

    try:
        with open(pyproject, encoding="utf-8") as f:
            match = re.search(
                r'^version = "([^"]+)"$',
                f.read(),
                re.MULTILINE,
            )
        if match:
            return match.group(1)
    except FileNotFoundError:
        pass

    try:
        return metadata.version("obs-cli")
    except metadata.PackageNotFoundError as exc:
        raise RuntimeError("Could not determine obs-cli version") from exc


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=RichHelpFormatter)
    parser.add_argument("-D", "--debug", action="store_true", default=False)
    parser.add_argument("-q", "--quiet", action="store_true", default=False)
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=get_version(),
    )
    parser.add_argument(
        "-H",
        "--host",
        default=os.environ.get("OBS_API_HOST", "localhost"),
        help="host name default: localhost ($OBS_API_HOST)",
    )
    parser.add_argument(
        "-P",
        "--port",
        type=int,
        default=os.environ.get("OBS_API_PORT", 4455),
        help="port number default: 4455 ($OBS_API_PORT)",
    )
    parser.add_argument(
        "-p",
        "--password",
        required=False,
        default=os.environ.get("OBS_API_PASSWORD"),
        help="password ($OBS_API_PASSWORD)",
    )
    parser.add_argument("-j", "--json", action="store_true", default=False)

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Shared parent so subcommands also accept -j/--json after their name.
    # argument_default=SUPPRESS means the subparser never writes a default
    # for --json, preserving the main parser's value when the flag comes first.
    _common = argparse.ArgumentParser(
        add_help=False, argument_default=argparse.SUPPRESS
    )
    _common.add_argument("-j", "--json", action="store_true")

    scene_parser = subparsers.add_parser(
        "scene",
        aliases=["scenes"],
        parents=[_common],
        formatter_class=RichHelpFormatter,
    )
    scene_parser.add_argument(
        "-e", "--exact", action="store_true", default=False, help="Exact match"
    )
    scene_parser.add_argument(
        "-i",
        "--ignorecase",
        action="store_true",
        default=False,
        help="Exact match",
    )
    scene_parser.add_argument(
        "action",
        choices=["list", "switch", "current", "screenshot"],
        default="list",
        nargs="?",
        help="list/switch/current/screenshot",
    )
    scene_parser.add_argument("SCENE", nargs="?", help="Scene name")
    scene_parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output file (required without --raw/--json)",
    )
    scene_parser.add_argument(
        "--raw",
        action="store_true",
        default=False,
        help="Write raw screenshot bytes to stdout",
    )
    scene_parser.add_argument(
        "-f",
        "--format",
        default=None,
        help="Image format: png, jpg, bmp (default: from filename ext or png)",
    )
    scene_parser.add_argument(
        "--width", type=int, default=None, help="Screenshot width"
    )
    scene_parser.add_argument(
        "--height", type=int, default=None, help="Screenshot height"
    )
    scene_parser.add_argument(
        "--compression-quality",
        type=int,
        default=-1,
        help="Compression quality -1 to 100 (-1 = OBS default)",
    )

    group_parser = subparsers.add_parser(
        "group",
        aliases=["groups"],
        parents=[_common],
        formatter_class=RichHelpFormatter,
    )
    group_parser.add_argument(
        "-s", "--scene", required=False, help="Scene name (default: current)"
    )
    group_parser.add_argument(
        "action",
        choices=["list", "show", "hide", "toggle"],
        default="list",
        nargs="?",
        help="list/show/hide/toggle",
    )
    group_parser.add_argument(
        "group", nargs="?", help="group to interact with"
    )

    item_parser = subparsers.add_parser(
        "item",
        aliases=["items"],
        parents=[_common],
        formatter_class=RichHelpFormatter,
    )
    item_parser.add_argument(
        "-s", "--scene", required=False, help="Scene name (default: current)"
    )
    item_parser.add_argument(
        "action",
        choices=["list", "show", "hide", "toggle", "screenshot"],
        default="list",
        nargs="?",
        help="list/show/hide/toggle/screenshot",
    )
    item_parser.add_argument("ITEM", nargs="?", help="Item to interact with")
    item_parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output file (required without --raw/--json)",
    )
    item_parser.add_argument(
        "--raw",
        action="store_true",
        default=False,
        help="Write raw screenshot bytes to stdout",
    )
    item_parser.add_argument(
        "-f",
        "--format",
        default=None,
        help="Image format: png, jpg, bmp (default: from filename ext or png)",
    )
    item_parser.add_argument(
        "--width", type=int, default=None, help="Screenshot width"
    )
    item_parser.add_argument(
        "--height", type=int, default=None, help="Screenshot height"
    )
    item_parser.add_argument(
        "--compression-quality",
        type=int,
        default=-1,
        help="Compression quality -1 to 100 (-1 = OBS default)",
    )

    input_parser = subparsers.add_parser(
        "input",
        aliases=["inputs"],
        parents=[_common],
        formatter_class=RichHelpFormatter,
    )
    input_parser.add_argument(
        "action",
        choices=[
            "list",
            "show",
            "get",
            "set",
            "mute",
            "unmute",
            "toggle-mute",
            "is-muted",
        ],
        default="list",
        nargs="?",
        help="list/show/get/set/mute/unmute/toggle-mute/is-muted",
    )
    input_parser.add_argument("INPUT", nargs="?", help="Input name")
    input_parser.add_argument("PROPERTY", nargs="?", help="Property name")
    input_parser.add_argument("VALUE", nargs="?", help="Property value")

    filter_parser = subparsers.add_parser(
        "filter",
        aliases=["filters"],
        parents=[_common],
        formatter_class=RichHelpFormatter,
    )
    filter_parser.add_argument(
        "action",
        choices=["list", "toggle", "enable", "disable", "status"],
        default="list",
        nargs="?",
        help="list/toggle/enable/disable/status",
    )
    filter_parser.add_argument("INPUT", nargs="?", help="Input name")
    filter_parser.add_argument("FILTER", nargs="?", help="Filter name")

    hotkey_parser = subparsers.add_parser(
        "hotkey",
        aliases=["hotkeys"],
        parents=[_common],
        formatter_class=RichHelpFormatter,
    )
    hotkey_parser.add_argument(
        "action",
        choices=["list", "trigger"],
        default="list",
        nargs="?",
        help="list/trigger",
    )
    hotkey_parser.add_argument("HOTKEY", nargs="?", help="Hotkey name")

    source_parser = subparsers.add_parser(
        "source",
        aliases=["sources"],
        parents=[_common],
        formatter_class=RichHelpFormatter,
    )
    source_parser.add_argument(
        "action",
        choices=["list", "screenshot", "active"],
        default="list",
        nargs="?",
        help="list/screenshot/active",
    )
    source_parser.add_argument("SOURCE", nargs="?", help="Source name")
    source_parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output file (required without --raw/--json)",
    )
    source_parser.add_argument(
        "--raw",
        action="store_true",
        default=False,
        help="Write raw screenshot bytes to stdout",
    )
    source_parser.add_argument(
        "-f",
        "--format",
        default=None,
        help="Image format: png, jpg, bmp (default: from filename ext or png)",
    )
    source_parser.add_argument(
        "--width", type=int, default=None, help="Screenshot width"
    )
    source_parser.add_argument(
        "--height", type=int, default=None, help="Screenshot height"
    )
    source_parser.add_argument(
        "--compression-quality",
        type=int,
        default=-1,
        help="Compression quality -1 to 100 (-1 = OBS default)",
    )

    virtualcam_parser = subparsers.add_parser(
        "virtualcam", parents=[_common], formatter_class=RichHelpFormatter
    )
    virtualcam_parser.add_argument(
        "action",
        choices=["status", "start", "stop", "toggle"],
        default="status",
        nargs="?",
        help="status/start/stop/toggle",
    )

    stream_parser = subparsers.add_parser(
        "stream", parents=[_common], formatter_class=RichHelpFormatter
    )
    stream_parser.add_argument(
        "action",
        choices=["status", "start", "stop", "toggle"],
        default="status",
        nargs="?",
        help="status/start/stop/toggle",
    )

    record_parser = subparsers.add_parser(
        "record", parents=[_common], formatter_class=RichHelpFormatter
    )
    record_parser.add_argument(
        "action",
        choices=["status", "start", "stop", "toggle"],
        default="status",
        nargs="?",
        help="status/start/stop/toggle",
    )

    replay_parser = subparsers.add_parser(
        "replay", parents=[_common], formatter_class=RichHelpFormatter
    )
    replay_parser.add_argument(
        "action",
        choices=["status", "start", "stop", "toggle", "save"],
        default="status",
        nargs="?",
        help="status/start/stop/toggle",
    )

    return parser.parse_args()


class ObsItemNotFoundException(ValueError):
    pass


class ObsSceneNotFoundException(ValueError):
    pass


def get_scene_names(cl):
    return sorted(
        (scene.get("sceneName") for scene in cl.get_scene_list().scenes)
    )


def switch_to_scene(cl, scene, exact=False, ignorecase=True):
    if not scene:
        raise ValueError("Missing scene name")

    regex = re.compile(
        (
            f"^{re.escape(scene)}$"
            if exact
            else re.escape(scene)
        ),
        re.IGNORECASE if ignorecase else re.NOFLAG,
    )
    scene_names = get_scene_names(cl)
    for scene_name in scene_names:
        if re.search(regex, scene_name):
            cl.set_current_program_scene(scene_name)
            return True

    available_scenes = "\n".join(
        f"  - '{name}'" for name in scene_names
    )
    raise ObsSceneNotFoundException(
        f"Scene not found: '{scene}'\nAvailable scenes:\n{available_scenes}"
    )


def get_items(
    cl, scene=None, names_only=False, recurse=True, include_groups=False
):
    scene = scene or get_current_scene_name(cl)
    items = cl.get_scene_item_list(scene).scene_items
    if recurse:
        all_items = []
        for it in items:
            if it.get("isGroup"):
                if include_groups:
                    all_items.append(it)
                for grp_it in cl.get_group_scene_item_list(
                    it.get("sourceName")
                ).scene_items:
                    # Inject parent group attribute
                    grp_it["parentGroup"] = it
                    all_items.append(grp_it)
            else:
                all_items.append(it)
        items = all_items

    items = sorted(
        items,
        key=lambda x: (
            x.get("parentGroup") is None,  # Items with parentGroup come first
            (
                x.get("parentGroup", {}).get("sourceName")
                if x.get("parentGroup")
                else None
            ),  # Then sort by parentGroup.sourceName
            x.get("sourceName"),  # Finally, sort by sourceName
        ),
    )

    return [x.get("sourceName") for x in items] if names_only else items


def get_groups(cl, scene=None, names_only=False):
    scene = scene or get_current_scene_name(cl)
    groups = sorted(
        [
            x
            for x in cl.get_scene_item_list(scene).scene_items
            if x.get("isGroup", False)
        ],
        key=lambda x: x.get("sourceName"),
    )

    return [x.get("sourceName") for x in groups] if names_only else groups


def get_item_by_name(
    cl, item, ignorecase=True, exact=False, scene=None, is_group=False
):
    items = get_items(cl, scene) if not is_group else get_groups(cl, scene)
    regex = re.compile(
        item if not exact else f"^{item}$",
        re.IGNORECASE if ignorecase else re.NOFLAG,
    )
    for it in items:
        if re.search(regex, it.get("sourceName")):
            return it

    raise ObsItemNotFoundException(
        f"Item not found: '{item}' (Scene: '{scene}')"
    )


def get_item_id(cl, item, scene=None, is_group=False):
    data = get_item_by_name(cl, item, scene=scene, is_group=is_group)
    return data.get("sceneItemId", -1)


def get_item_parent(cl, item, scene=None):
    data = get_item_by_name(cl, item, scene=scene)
    parent_group = data.get("parentGroup")
    return parent_group.get("sourceName") if parent_group else scene


def is_item_enabled(cl, item, scene=None, is_group=False):
    data = get_item_by_name(cl, item=item, is_group=is_group, scene=scene)
    return data.get("sceneItemEnabled")


def show_item(cl, item, scene=None, is_group=False):
    scene = scene or get_current_scene_name(cl)
    item_id = get_item_id(cl, item=item, scene=scene, is_group=is_group)
    parent = scene if is_group else get_item_parent(cl, item, scene)
    return cl.set_scene_item_enabled(parent, item_id, True)


def hide_item(cl, item, scene=None, is_group=False):
    scene = scene or get_current_scene_name(cl)
    item_id = get_item_id(cl, item=item, scene=scene, is_group=is_group)
    parent = scene if is_group else get_item_parent(cl, item, scene)
    return cl.set_scene_item_enabled(parent, item_id, False)


def toggle_item(cl, item, scene=None, is_group=False):
    scene = scene or get_current_scene_name(cl)
    item_id = get_item_id(cl, item=item, scene=scene, is_group=is_group)
    parent = scene if is_group else get_item_parent(cl, item, scene)
    enabled = not is_item_enabled(
        cl, item=item, scene=scene, is_group=is_group
    )
    return cl.set_scene_item_enabled(parent, item_id, enabled)


def get_current_scene_name(cl):
    return cl.get_current_program_scene().current_program_scene_name


def get_inputs(cl):
    return sorted(cl.get_input_list().inputs, key=lambda x: x.get("inputName"))


def get_input_settings(cl, input):
    return cl.get_input_settings(input).input_settings


def set_input_setting(cl, input, key, value):
    try:
        value = json.loads(value)
    except (ValueError, TypeError):
        pass
    LOGGER.debug(f"Setting {key} to {value} ({type(value)})")
    return cl.set_input_settings(input, {key: value}, overlay=True)


def get_mute_state(cl, input):
    return cl.get_input_mute(input).input_muted


def mute_input(cl, input):
    cl.set_input_mute(input, True)


def unmute_input(cl, input):
    cl.set_input_mute(input, False)


def toggle_mute_input(cl, input):
    cl.toggle_input_mute(input)


def get_filters(cl, input):
    return cl.get_source_filter_list(input).filters


def is_filter_enabled(cl, source, filter):
    return cl.get_source_filter(source, filter).filter_enabled


def enable_filter(cl, source, filter):
    return cl.set_source_filter_enabled(source, filter, True)


def disable_filter(cl, source, filter):
    return cl.set_source_filter_enabled(source, filter, False)


def toggle_filter(cl, source, filter):
    enabled = is_filter_enabled(cl, source, filter)
    return cl.set_source_filter_enabled(source, filter, not enabled)


def get_hotkeys(cl):
    return cl.get_hot_key_list().hotkeys


def trigger_hotkey(cl, hotkey):
    return cl.trigger_hot_key_by_name(hotkey)


def virtual_camera_status(cl):
    return cl.get_virtual_cam_status().output_active


def virtual_camera_start(cl):
    return cl.start_virtual_cam()


def virtual_camera_stop(cl):
    return cl.stop_virtual_cam()


def virtual_camera_toggle(cl):
    return cl.toggle_virtual_cam()


def stream_status(cl):
    return cl.get_stream_status().output_active


def stream_start(cl):
    return cl.start_stream()


def stream_stop(cl):
    return cl.stop_stream()


def stream_toggle(cl):
    return cl.toggle_stream()


def replay_start(cl):
    return cl.start_replay_buffer()


def replay_stop(cl):
    return cl.stop_replay_buffer()


def replay_save(cl):
    return cl.save_replay_buffer()


def replay_toggle(cl):
    return cl.toggle_replay_buffer()


def replay_status(cl):
    return cl.get_replay_buffer_status().output_active


def record_status(cl):
    return cl.get_record_status().output_active


def record_start(cl):
    return cl.start_record()


def record_stop(cl):
    return cl.stop_record()


def record_toggle(cl):
    return cl.toggle_record()


def source_active(cl, source):
    res = cl.send("GetSourceActive", {"sourceName": source}, raw=True)
    return res.get("videoActive", False), res.get("videoShowing", False)


def take_screenshot(
    cl,
    source,
    image_format="png",
    width=None,
    height=None,
    compression_quality=-1,
):
    payload = {
        "sourceName": source,
        "imageFormat": image_format,
        "imageCompressionQuality": compression_quality,
    }
    if width:
        payload["imageWidth"] = width
    if height:
        payload["imageHeight"] = height
    res = cl.send("GetSourceScreenshot", payload)
    image_data = res.image_data
    # Strip data URI prefix (e.g. "data:image/png;base64,")
    if "," in image_data:
        image_data = image_data.split(",", 1)[1]
    return base64.b64decode(image_data)


_NA = Text("N/A", style="bright_black italic")


_COLUMN_STYLES = (
    "cyan",
    "green",
    "magenta",
    "white",
    "yellow",
    "blue",
    "bright_black",
    "red",
)


def make_table(*headers):
    table = Table(
        box=None,
        show_edge=False,
        pad_edge=False,
        padding=(0, 2, 0, 0),
        header_style="bold",
    )
    for i, header in enumerate(headers):
        table.add_column(
            header.upper(), style=_COLUMN_STYLES[i % len(_COLUMN_STYLES)]
        )
    return table


def print_error(console, message):
    console.print(f"[bold red]ERROR:[/bold red] {message}")


def main():
    console = Console()
    error_console = Console(stderr=True)
    logging.basicConfig()

    args = parse_args()
    LOGGER.setLevel(logging.DEBUG if args.debug else logging.INFO)
    LOGGER.debug(args)

    try:
        cl = obs.ReqClient(
            host=args.host,
            port=args.port,
            password=args.password,
        )

        _aliases = {
            "scenes": "scene",
            "groups": "group",
            "items": "item",
            "inputs": "input",
            "filters": "filter",
            "hotkeys": "hotkey",
            "sources": "source",
        }
        cmd = _aliases.get(args.command, args.command)
        if cmd == "scene":
            if args.action == "current":
                print(get_current_scene_name(cl))
            elif args.action == "list":
                res = cl.get_scene_list()
                LOGGER.debug(res)
                if args.json:
                    print_json(data=res.scenes)
                    return
                current = res.current_program_scene_name
                table = make_table("index", "name", "current")
                for sc in sorted(
                    res.scenes, key=lambda x: x.get("sceneIndex")
                ):
                    is_current = sc.get("sceneName") == current
                    table.add_row(
                        str(sc.get("sceneIndex")),
                        sc.get("sceneName"),
                        (
                            Text("true", style="bold green")
                            if is_current
                            else Text("false", style="bright_black")
                        ),
                    )
                console.print(table)
            elif args.action == "switch":
                if not args.SCENE:
                    print_error(error_console, "missing scene name")
                    return 2
                res = switch_to_scene(cl, args.SCENE, exact=False)
                LOGGER.debug(res)
            elif args.action == "screenshot":
                if not args.raw and not args.json and not args.output:
                    print(
                        "ERROR: --output required without --raw/--json",
                        file=sys.stderr,
                    )
                    return 2
                scene = args.SCENE or get_current_scene_name(cl)
                fmt = args.format
                if not fmt and args.output and not args.json:
                    ext = os.path.splitext(args.output)[1].lstrip(".")
                    if ext:
                        fmt = ext.lower()
                fmt = fmt or "png"
                data = take_screenshot(
                    cl,
                    scene,
                    image_format=fmt,
                    width=args.width,
                    height=args.height,
                    compression_quality=args.compression_quality,
                )
                if args.json:
                    json_out = json.dumps(
                        {
                            "format": fmt,
                            "data": base64.b64encode(data).decode(),
                        }
                    )
                    if args.output:
                        with open(args.output, "w") as f:
                            f.write(json_out)
                    else:
                        print_json(json_out)
                elif args.raw:
                    sys.stdout.buffer.write(data)
                else:
                    with open(args.output, "wb") as f:
                        f.write(data)

        elif cmd == "group":
            scene = args.scene or get_current_scene_name(cl)
            if args.action == "list":
                data = get_groups(cl, scene)
                if args.json:
                    print_json(data=data)
                    return

                table = make_table("id", "name", "enabled")
                for group in data:
                    table.add_row(
                        str(group.get("sceneItemId")),
                        group.get("sourceName"),
                        str(group.get("sceneItemEnabled")).lower(),
                    )
                console.print(table)
            elif args.action == "toggle":
                res = toggle_item(cl, args.group, scene=scene, is_group=True)
                LOGGER.debug(res)
            elif args.action == "show":
                res = show_item(cl, args.group, scene=scene, is_group=True)
                LOGGER.debug(res)
            elif args.action == "hide":
                res = hide_item(cl, args.group, scene=scene, is_group=True)
                LOGGER.debug(res)

        elif cmd == "item":
            scene = args.scene or get_current_scene_name(cl)
            if args.action == "list":
                data = get_items(cl, args.scene)
                if args.json:
                    print_json(data=data)
                    return

                table = make_table("id", "group", "name", "enabled")
                for item in data:
                    group = (item.get("parentGroup") or {}).get("sourceName")
                    table.add_row(
                        str(item.get("sceneItemId")),
                        group or _NA,
                        item.get("sourceName"),
                        str(item.get("sceneItemEnabled")).lower(),
                    )
                console.print(table)
            elif args.action == "toggle":
                res = toggle_item(cl, item=args.ITEM, scene=scene)
                LOGGER.debug(res)
            elif args.action == "show":
                res = show_item(cl, item=args.ITEM, scene=scene)
                LOGGER.debug(res)
            elif args.action == "hide":
                res = hide_item(cl, item=args.ITEM, scene=scene)
                LOGGER.debug(res)
            elif args.action == "screenshot":
                if not args.raw and not args.json and not args.output:
                    print(
                        "ERROR: --output required without --raw/--json",
                        file=sys.stderr,
                    )
                    return 2
                fmt = args.format
                if not fmt and args.output and not args.json:
                    ext = os.path.splitext(args.output)[1].lstrip(".")
                    if ext:
                        fmt = ext.lower()
                fmt = fmt or "png"
                data = take_screenshot(
                    cl,
                    args.ITEM,
                    image_format=fmt,
                    width=args.width,
                    height=args.height,
                    compression_quality=args.compression_quality,
                )
                if args.json:
                    json_out = json.dumps(
                        {
                            "format": fmt,
                            "data": base64.b64encode(data).decode(),
                        }
                    )
                    if args.output:
                        with open(args.output, "w") as f:
                            f.write(json_out)
                    else:
                        print_json(json_out)
                elif args.raw:
                    sys.stdout.buffer.write(data)
                else:
                    with open(args.output, "wb") as f:
                        f.write(data)

        elif cmd == "input":
            if args.action == "list":
                data = get_inputs(cl)
                if args.json:
                    print_json(data=data)
                    return

                table = make_table("kind", "name", "muted")
                for input in data:
                    kind = input.get("inputKind")
                    name = input.get("inputName")
                    # FIXME The inputKind whitelist here is probably incomplete
                    if kind in ["ffmpeg_source"] or "capture" in kind:
                        muted = str(get_mute_state(cl, name)).lower()
                    else:
                        muted = _NA
                    table.add_row(kind, name, muted)
                console.print(table)
            elif args.action == "show" or args.action == "get":
                data = get_input_settings(cl, args.INPUT)
                if args.PROPERTY:
                    print(data.get(args.PROPERTY))
                else:
                    # TODO Implement rich table output
                    print_json(data=data)
            elif args.action == "set":
                if not args.INPUT or not args.PROPERTY or not args.VALUE:
                    raise ValueError("Missing input name, property or value")
                res = set_input_setting(
                    cl, args.INPUT, args.PROPERTY, args.VALUE
                )
                LOGGER.debug(res)

            elif args.action == "mute":
                res = mute_input(cl, args.INPUT)
                LOGGER.debug(res)

            elif args.action == "unmute":
                res = unmute_input(cl, args.INPUT)
                LOGGER.debug(res)

            elif args.action == "toggle-mute":
                res = toggle_mute_input(cl, args.INPUT)
                LOGGER.debug(res)

            elif args.action == "is-muted":
                res = get_mute_state(cl, args.INPUT)
                print("enabled" if res else "disabled")

        elif cmd == "filter":
            if args.action == "list":
                data = get_filters(cl, args.INPUT)
                if args.json:
                    print_json(data=data)
                    return
                table = make_table("kind", "name", "enabled")
                for f in data:
                    table.add_row(
                        f.get("filterKind"),
                        f.get("filterName"),
                        str(f.get("filterEnabled")).lower(),
                    )
                console.print(table)
            elif args.action == "toggle":
                res = toggle_filter(cl, args.INPUT, args.FILTER)
                LOGGER.debug(res)
            elif args.action == "enable":
                res = enable_filter(cl, args.INPUT, args.FILTER)
                LOGGER.debug(res)
            elif args.action == "disable":
                res = disable_filter(cl, args.INPUT, args.FILTER)
                LOGGER.debug(res)
            elif args.action == "status":
                res = is_filter_enabled(cl, args.INPUT, args.FILTER)
                LOGGER.debug(res)
                if args.quiet:
                    sys.exit(0 if res else 1)
                print("enabled" if res else "disabled")
        elif cmd == "hotkey":
            if args.action == "list":
                data = get_hotkeys(cl)
                if args.json:
                    print_json(data=data)
                    return
                table = make_table("name")
                for hk in data:
                    table.add_row(hk)
                console.print(table)
            elif args.action == "trigger":
                res = trigger_hotkey(cl, args.HOTKEY)
                LOGGER.debug(res)

        elif cmd == "source":
            if args.action == "list":
                data = get_inputs(cl)
                if args.json:
                    print_json(data=data)
                    return
                table = make_table("kind", "name")
                for src in data:
                    table.add_row(
                        src.get("inputKind"),
                        src.get("inputName"),
                    )
                console.print(table)
            elif args.action == "screenshot":
                if not args.raw and not args.json and not args.output:
                    print(
                        "ERROR: --output required without --raw/--json",
                        file=sys.stderr,
                    )
                    return 2
                fmt = args.format
                if not fmt and args.output and not args.json:
                    ext = os.path.splitext(args.output)[1].lstrip(".")
                    if ext:
                        fmt = ext.lower()
                fmt = fmt or "png"
                data = take_screenshot(
                    cl,
                    args.SOURCE,
                    image_format=fmt,
                    width=args.width,
                    height=args.height,
                    compression_quality=args.compression_quality,
                )
                if args.json:
                    json_out = json.dumps(
                        {
                            "format": fmt,
                            "data": base64.b64encode(data).decode(),
                        }
                    )
                    if args.output:
                        with open(args.output, "w") as f:
                            f.write(json_out)
                    else:
                        print_json(json_out)
                elif args.raw:
                    sys.stdout.buffer.write(data)
                else:
                    with open(args.output, "wb") as f:
                        f.write(data)
            elif args.action == "active":
                active, showing = source_active(cl, args.SOURCE)
                if args.json:
                    print_json(
                        data={"active": active, "showing": showing}
                    )
                    return
                if args.quiet:
                    sys.exit(0 if active else 1)
                table = make_table("source", "active", "showing")
                table.add_row(
                    args.SOURCE,
                    Text("true", style="bold green")
                    if active
                    else Text("false", style="bright_black"),
                    Text("true", style="bold green")
                    if showing
                    else Text("false", style="bright_black"),
                )
                console.print(table)

        elif cmd == "virtualcam":
            if args.action == "status":
                res = virtual_camera_status(cl)
                LOGGER.debug(res)
                if args.quiet:
                    sys.exit(0 if res else 1)
                print("started" if res else "stopped")
            elif args.action == "start":
                res = virtual_camera_start(cl)
                LOGGER.debug(res)
            elif args.action == "stop":
                res = virtual_camera_stop(cl)
                LOGGER.debug(res)
            elif args.action == "toggle":
                res = virtual_camera_toggle(cl)
                LOGGER.debug(res)

        elif cmd == "stream":
            if args.action == "status":
                res = stream_status(cl)
                LOGGER.debug(res)
                if args.quiet:
                    sys.exit(0 if res else 1)
                print("started" if res else "stopped")
            elif args.action == "start":
                res = stream_start(cl)
                LOGGER.debug(res)
            elif args.action == "stop":
                res = stream_stop(cl)
                LOGGER.debug(res)
            elif args.action == "toggle":
                res = stream_toggle(cl)
                LOGGER.debug(res)

        elif cmd == "record":
            if args.action == "status":
                res = record_status(cl)
                LOGGER.debug(res)
                if args.quiet:
                    sys.exit(0 if res else 1)
                print("started" if res else "stopped")
            elif args.action == "start":
                res = record_start(cl)
                LOGGER.debug(res)
            elif args.action == "stop":
                res = record_stop(cl)
                LOGGER.debug(res)
            elif args.action == "toggle":
                res = record_toggle(cl)
                LOGGER.debug(res)

        elif cmd == "replay":
            if args.action == "status":
                res = replay_status(cl)
                LOGGER.debug(res)
                if args.quiet:
                    sys.exit(0 if res else 1)
                print("started" if res else "stopped")
            elif args.action == "start":
                res = replay_start(cl)
                LOGGER.debug(res)
            elif args.action == "stop":
                res = replay_stop(cl)
                LOGGER.debug(res)
            elif args.action == "toggle":
                res = replay_toggle(cl)
                LOGGER.debug(res)
            elif args.action == "save":
                res = replay_save(cl)
                LOGGER.debug(res)

        return 0
    except ObsItemNotFoundException as ecp:
        print_error(error_console, str(ecp))
        return 1
    except ObsSceneNotFoundException as ecp:
        print_error(error_console, str(ecp))
        return 1
    except Exception:
        console.print_exception(show_locals=True)
        return 1


LOGGER = logging.getLogger(__name__)

if __name__ == "__main__":
    sys.exit(main())
