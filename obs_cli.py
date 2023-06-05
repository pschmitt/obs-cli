#!/usr/bin/env python
# coding: utf-8

import argparse
import logging
import re
import sys

import obsws_python as obs
from rich import print, print_json
from rich.console import Console
from rich.table import Table


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-D", "--debug", action="store_true", default=False)
    parser.add_argument("-H", "--host", help="host name", default="localhost")
    parser.add_argument(
        "-P", "--port", help="port number", type=int, default=4455
    )
    parser.add_argument("-p", "--password", help="password")
    parser.add_argument("-j", "--json", action="store_true", default=False)

    subparsers = parser.add_subparsers(dest="command")

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
        choices=["list", "show", "set"],
        default="show",
        help="list/show",
    )
    input_parser.add_argument("INPUT", nargs="?", help="Input name")
    input_parser.add_argument("PROPERTY", nargs="?", help="Property name")
    input_parser.add_argument("VALUE", nargs="?", help="Property value")

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
    return cl.set_input_settings(input, {key: value}, overlay=True)


def main():
    console = Console()
    logging.basicConfig()

    args = parse_args()
    LOGGER.setLevel(logging.DEBUG if args.debug else logging.INFO)
    LOGGER.debug(args)

    try:
        cl = obs.ReqClient(
            host=args.host, port=args.port, password=args.password
        )

        cmd = args.command
        if cmd == "scene":
            if args.action == "current":
                print(get_current_scene_name(cl))
            elif args.action == "list":
                res = cl.get_scene_list()
                print(
                    *sorted([x.get("sceneName") for x in res.scenes]), sep="\n"
                )
            elif args.action == "switch":
                switch_to_scene(cl, args.SCENE, exact=False)
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
                toggle_item(cl, args.ITEM, args.scene)
            elif args.action == "show":
                show_item(cl, args.ITEM, args.scene)
            elif args.action == "hide":
                hide_item(cl, args.ITEM, args.scene)
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
            elif args.action == "show":
                data = get_input_settings(cl, args.INPUT)
                if args.PROPERTY:
                    print(data.get(args.PROPERTY))
                else:
                    # TODO Implement rich table output
                    print_json(data=data)
            elif args.action == "set":
                if not args.INPUT or not args.PROPERTY or not args.VALUE:
                    raise ValueError("Missing input name, property or value")
                set_input_setting(cl, args.INPUT, args.PROPERTY, args.VALUE)

        return 0
    except Exception:
        console.print_exception(show_locals=True)
        return 1


LOGGER = logging.getLogger(__name__)

if __name__ == "__main__":
    sys.exit(main())
