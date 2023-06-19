#!/usr/bin/env python
# coding: utf-8

import argparse
import json
import logging
import os
import re
import sys

import obsws_python as obs
from rich import print, print_json
from rich.console import Console
from rich.table import Table


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-D", "--debug", action="store_true", default=False)
    parser.add_argument("-q", "--quiet", action="store_true", default=False)
    parser.add_argument("-H", "--host", help="host name", default="localhost")
    parser.add_argument(
        "-P", "--port", help="port number", type=int, default=4455
    )
    parser.add_argument(
        "-p", "--password", required=False, help="password ($OBS_API_PASSWORD)"
    )
    parser.add_argument("-j", "--json", action="store_true", default=False)

    subparsers = parser.add_subparsers(dest="command", required=True)

    scene_parser = subparsers.add_parser("scene")
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
        choices=["list", "switch", "current"],
        default="current",
        help="list/switch/current",
    )
    scene_parser.add_argument("SCENE", nargs="?", help="Scene name")

    item_parser = subparsers.add_parser("item")
    item_parser.add_argument(
        "-s", "--scene", required=False, help="Scene name (default: current)"
    )
    item_parser.add_argument(
        "action",
        choices=["list", "show", "hide", "toggle"],
        default="toggle",
        help="show/hide/toggle",
    )
    item_parser.add_argument("ITEM", nargs="?", help="Item to interact with")

    input_parser = subparsers.add_parser("input")
    input_parser.add_argument(
        "action",
        choices=["list", "show", "get", "set"],
        default="show",
        help="list/show/get/set",
    )
    input_parser.add_argument("INPUT", nargs="?", help="Input name")
    input_parser.add_argument("PROPERTY", nargs="?", help="Property name")
    input_parser.add_argument("VALUE", nargs="?", help="Property value")

    filter_parser = subparsers.add_parser("filter")
    filter_parser.add_argument(
        "action",
        choices=["list", "toggle", "enable", "disable", "status"],
        default="list",
        help="list/toggle/enable/disable/status",
    )
    filter_parser.add_argument("INPUT", nargs="?", help="Input name")
    filter_parser.add_argument("FILTER", nargs="?", help="Filter name")

    hotkey_parser = subparsers.add_parser("hotkey")
    hotkey_parser.add_argument(
        "action",
        choices=["list", "trigger"],
        default="list",
        help="list/trigger",
    )
    hotkey_parser.add_argument("HOTKEY", nargs="?", help="Hotkey name")

    virtualcam_parser = subparsers.add_parser("virtualcam")
    virtualcam_parser.add_argument(
        "action",
        choices=["status", "start", "stop", "toggle"],
        default="status",
        help="status/start/stop/toggle",
    )

    stream_parser = subparsers.add_parser("stream")
    stream_parser.add_argument(
        "action",
        choices=["status", "start", "stop", "toggle"],
        default="status",
        help="status/start/stop/toggle",
    )

    record_parser = subparsers.add_parser("record")
    record_parser.add_argument(
        "action",
        choices=["status", "start", "stop", "toggle"],
        default="status",
        help="status/start/stop/toggle",
    )

    return parser.parse_args()


def switch_to_scene(cl, scene, exact=False, ignorecase=True):
    regex = re.compile(
        f"^{scene}$" if exact else scene,
        re.IGNORECASE if ignorecase else re.NOFLAG,
    )
    for sc in sorted(
        cl.get_scene_list().scenes, key=lambda x: x.get("sceneName")
    ):
        print(f"Compare {scene} with {sc.get('sceneName')}")
        if re.search(regex, sc.get("sceneName")):
            cl.set_current_program_scene(sc.get("sceneName"))
            return True


def get_items(cl, scene=None, names_only=False):
    scene = scene or get_current_scene_name(cl)
    items = sorted(
        cl.get_scene_item_list(scene).scene_items,
        key=lambda x: x.get("sourceName"),
    )

    return [x.get("sourceName") for x in items] if names_only else items


def get_item_by_name(cl, item, ignorecase=True, exact=False, scene=None):
    items = get_items(cl, scene)
    regex = re.compile(
        item if not exact else f"^{item}$",
        re.IGNORECASE if ignorecase else re.NOFLAG,
    )
    for it in items:
        if re.search(regex, it.get("sourceName")):
            return it


def get_item_id(cl, item, scene=None):
    data = get_item_by_name(cl, item, scene=scene)
    if not data:
        LOGGER.warning(f"Item not found: {item} (in {scene})")
        return -1
    return data.get("sceneItemId", -1)


def is_item_enabled(cl, item, scene=None):
    data = get_item_by_name(cl, item, scene=scene)
    if not data:
        LOGGER.warning(f"Item not found: {item} (in {scene})")
        return -1
    return data.get("sceneItemEnabled", False)


def show_item(cl, item, scene=None):
    scene = scene or get_current_scene_name(cl)
    item_id = get_item_id(cl, item, scene)
    return cl.set_scene_item_enabled(scene, item_id, True)


def hide_item(cl, item, scene=None):
    scene = scene or get_current_scene_name(cl)
    item_id = get_item_id(cl, item, scene)
    return cl.set_scene_item_enabled(scene, item_id, False)


def toggle_item(cl, item, scene=None):
    scene = scene or get_current_scene_name(cl)
    item_id = get_item_id(cl, item, scene)
    enabled = is_item_enabled(cl, item, scene)
    return cl.set_scene_item_enabled(scene, item_id, not enabled)


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


def record_status(cl):
    return cl.get_record_status().output_active


def record_start(cl):
    return cl.start_record()


def record_stop(cl):
    return cl.stop_record()


def record_toggle(cl):
    return cl.toggle_record()


def main():
    console = Console()
    logging.basicConfig()

    args = parse_args()
    LOGGER.setLevel(logging.DEBUG if args.debug else logging.INFO)
    LOGGER.debug(args)

    password = args.password or os.environ.get("OBS_API_PASSWORD")

    try:
        cl = obs.ReqClient(host=args.host, port=args.port, password=password)

        cmd = args.command
        if cmd == "scene":
            if args.action == "current":
                print(get_current_scene_name(cl))
            elif args.action == "list":
                res = cl.get_scene_list()
                print(
                    *sorted([x.get("sceneName") for x in res.scenes]), sep="\n"
                )
                LOGGER.debug(res)
            elif args.action == "switch":
                res = switch_to_scene(cl, args.SCENE, exact=False)
                LOGGER.debug(res)
            else:
                print(get_current_scene_name(cl))

        elif cmd == "item":
            if args.action == "list":
                # print(*get_items(cl, args.scene), sep="\n")
                scene = args.scene or get_current_scene_name(cl)

                data = get_items(cl, args.scene)
                if args.json:
                    print_json(data=data)
                    return

                table = Table(title=f"Items in scene '{scene}'")
                table.add_column("ID")
                table.add_column("Name")
                table.add_column("Enabled", justify="center")
                for item in data:
                    item_id = str(item.get("sceneItemId"))
                    name = item.get("sourceName")
                    enabled = "✅" if item.get("sceneItemEnabled") else "❌"
                    table.add_row(item_id, name, enabled)
                console.print(table)
            elif args.action == "toggle":
                res = toggle_item(cl, args.ITEM, args.scene)
                LOGGER.debug(res)
            elif args.action == "show":
                res = show_item(cl, args.ITEM, args.scene)
                LOGGER.debug(res)
            elif args.action == "hide":
                res = hide_item(cl, args.ITEM, args.scene)
                LOGGER.debug(res)

        elif cmd == "input":
            if args.action == "list":
                data = get_inputs(cl)
                if args.json:
                    print_json(data=data)
                    return

                table = Table(title="Inputs")
                table.add_column("Kind")
                table.add_column("Name")
                for input in data:
                    kind = input.get("inputKind")
                    name = input.get("inputName")
                    table.add_row(kind, name)
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

        elif cmd == "filter":
            if args.action == "list":
                data = get_filters(cl, args.INPUT)
                if args.json:
                    print_json(data=data)
                    return
                table = Table(title=f"Filters for {args.INPUT}")
                table.add_column("Kind")
                table.add_column("Name")
                table.add_column("Enabled", justify="center")
                for filter in data:
                    kind = filter.get("filterKind")
                    name = filter.get("filterName")
                    enabled = "✅" if filter.get("filterEnabled") else "❌"
                    table.add_row(kind, name, enabled)
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
                table = Table(title="Hotkeys")
                table.add_column("Name")
                for hk in data:
                    table.add_row(hk)
                console.print(table)
            elif args.action == "trigger":
                res = trigger_hotkey(cl, args.HOTKEY)
                LOGGER.debug(res)

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

        return 0
    except Exception:
        console.print_exception(show_locals=True)
        return 1


LOGGER = logging.getLogger(__name__)

if __name__ == "__main__":
    sys.exit(main())
