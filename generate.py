#!/usr/share/python

import json, yaml, re, os
from lib.dict_tools import DictRemapper

class TaskConverter:
    def in_inv(obj):
        if isinstance(obj["in_inv"], str):
            items = [obj.pop("in_inv")]
        else:
            items = obj.pop("in_inv")

        for i in range(len(items)):
            if isinstance(items[i], str):
                items[i] = {items[i]: 1}
            item = list(items[i].keys())[0]
            count = items[i].pop(item)
            items[i] = {"item": item}
            items[i].update({"count": count})

        return {
            "trigger": "minecraft:inventory_changed",
            "conditions": {
                "items": items
            }
        }

    def break_tool(obj):
        return {
			"trigger": "minecraft:item_durability_changed",
			"conditions": {
				"item": {
					"item": obj.pop("break_tool")
				},
				"durability": {
					"max": 1
				}
 			}
		}

    callback_table = {
        "in_inv": in_inv,
        "break_tool": break_tool
    }
    
    def convert(task, index = 0):
        for i in TaskConverter.callback_table:
            if i in task:
                return TaskConverter.callback_table[i](task)
        if (not "trigger" in task) or (not "conditions" in task):
            raise Exception("task not matched by TaskConverter.callback_table,\n" +
                " and no \"criteria\" and \"trigger\" in it: \n\n" + str(task))
        return task


class Default:
    root = {
        "frame": "task",
        "pop_up": False,
        "chat": False,
        "hidden": False
    }
    task = {
        "frame": "task",
        "pop_up": True,
        "chat": True,
        "hidden": False
    }

class Main:
    def pprint(obj):
        print(json.dumps(obj, indent = 4, sort_keys = True))

    def parser(data):
        def raise_not_in(obj, name, comment = ""):
            if comment != "":
                comment = " " + comment
            if name not in obj:
                raise Exception("no " + str(name) + " found" + comment + "\n\n" + str(obj))

        def id_to_filename(identifier):
            namespace, location = identifier.split(":")
            return "./data/" + namespace + "/advancements/" + location + ".json"
            
        advancements = []
        pack_mcmeta = 0
        for i in range(len(data)):
            if "pack" in data[i]:
                pack_mcmeta = i
        pack_mcmeta = data.pop(pack_mcmeta)

        for i in data:
            raise_not_in(i, "category")

            category = i["category"]
            category_root = ""
            for element in category:
                if "root" in element:
                    raise_not_in(element, "root")
                    raise_not_in(element, "id", "(in a root element)")

                    element["name"] = element.pop("root")
                    category_root = element["id"]
                    element["id"] = "root"

                    for name, value in Default.root.items():
                        if name not in element: element[name] = value
                else:
                    for name, value in Default.task.items():
                        if name not in element: element[name] = value

            for element in category:
                raise_not_in(element, "id")
                element["id"] = category_root + "/" + element["id"]

                if "parent" in element:
                    element["parent"] = category_root + "/" + element["parent"]


                advancements.append(element)

        del data, category_root

        remapper = DictRemapper({
            "name":        "display/title",
            "description": "display/description",
            "icon":        "display/icon/item",
            "nbt":         "display/icon/nbt",
            "frame":       "display/frame",
            "pop_up":      "display/show_toast",
            "chat":        "display/announce_to_chat",
            "hidden":      "display/hidden",
            "background":  "display/background"
        })

        for advancement in advancements:
            raise_not_in(advancement, "task")

            if not isinstance(advancement["task"], list):
                advancement["task"] = [advancement["task"]]
            if "icon" not in advancement:
                if "in_inv" in advancement["task"][0]:
                    advancement["icon"] = advancement["task"][0]["in_inv"]
                    if isinstance(advancement["icon"], list):
                        advancement["icon"] = list(advancement["icon"][0].keys())[0]

            ctr = 0
            if "criteria" not in advancement:
                advancement["criteria"] = {}
            if "requirements" not in advancement:
                advancement["requirements"] =[]
            for i in range(len(advancement["task"])):
                task = advancement["task"][i]
                advancement["requirements"].append([])
                if not isinstance(task, list):
                    task = [task]
                for j in task:
                    advancement["criteria"][str(ctr)] = TaskConverter.convert(j)
                    advancement["requirements"][i].append(str(ctr))
                    ctr += 1
            del ctr, advancement["task"]

            raise_not_in(advancement, "icon")


            if "nbt" in advancement and isinstance(advancement["nbt"], dict):
                advancement["nbt"] = str(advancement["nbt"]).replace("'", "\"")
            elif "nbt_str" in advancement:
                advancement["nbt"] = advancement.pop("nbt_str")
            elif "nbt" in advancement and isinstance(advancement["nbt"], str):
                pass

        for i in range(len(advancements)):
            advancements[i] = (
                id_to_filename(advancements[i].pop("id")),
                remapper.remap(advancements[i])
            )

        version = pack_mcmeta["pack"].pop("version")
        pack_mcmeta["pack"]["pack_format"] = {
            "1.16.5": 6
        }[version]
        advancements.append(["./pack.mcmeta", pack_mcmeta])
        del pack_mcmeta, remapper
        return advancements

    def write(files):
        def create_folder(file):
            folder = "/".join(re.split("/", file)[:-1])
            if not os.path.exists(folder):
                os.makedirs(folder)

        for name, data in files:
            create_folder(name)
            with open(name, 'w') as f:
                f.write(json.dumps(data, indent = 4))
                f.close()
                print(name)

    def main(filename):
        with open(filename) as f:
            try:
                data = yaml.safe_load(f)
            except Exception as e:
                print(e)
            finally:
                f.close()

            files = Main.parser(data)
            Main.write(files)

Main.main("config.yaml")
