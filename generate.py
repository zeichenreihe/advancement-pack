import yaml
import json

class Mcid():
    # namespace:name
    # namespace:folder/name
    # namespace:folder/folder/name
    def __init__(self, identifier :str):
        self.namespace, rest = identifier.split(":")
        self.location = rest.split("/")
        self.name = self.location.pop(-1)

    def getFilename(self, subfolder="", fileending=".json") -> str:
        output = "data/" + self.namespace + "/"
        if subfolder != "":
            output = output + subfolder + "/"
        
        for i in self.location:
            output = output + i + "/"

        output = output + self.name + fileending
        return output

class Remapper():
    remapping_category_to_child = {
        "category": "name",
        "id": "id",
        "description": "description",
        "task": "task",
        "features": "features",
        "icon": "icon",
        "nbt": "nbt",
        "nbt_str": "nbt_str",
        "background": "background"
    }
    def remap_category(category):
        out_obj = {}
        for i in Remapper.remapping_category_to_child.keys():
            if i in category:
                out_obj[Remapper.remapping_category_to_child[i]] = category[i]
        if "id" in out_obj:
           out_obj["id"] += "/root"
        return out_obj

    def remap_child_id(child, category):
        if "id" in child and "id" in category:
            child["id"] = category["id"] + "/" + child["id"]
        if "parent" in child and "id" in category:
            child["parent"] = category["id"] + "/" + child["parent"]
        return child

    remapping_features_to_child = {
        "display": "frame",
        "pop_up": "show_toast",
		"chat": "announce_to_chat",
        "hidden": "hidden"
    }
    def remap_features(obj):
        features = {} 
        if "features" in obj:
            features = obj.pop("features")
        for i in Remapper.remapping_features_to_child.keys():
            if i in features:
                obj[Remapper.remapping_features_to_child[i]] = features[i]
        return obj

    def remap_nbt(obj):
        if "nbt" in obj:
            obj["nbt"] = str(obj["nbt"]).replace("'", "\\\"")
        if "nbt_str" in obj:
            obj["nbt"] = obj.pop("nbt_str")
        return obj

    remapping_names = {
        "background": ["display", "background"],
        "icon": ["display", "icon", "item"],
        "nbt": ["display", "icon", "nbt"],
        "name": ["display", "title"],
        "description": ["display", "description"],
        "frame": ["display", "frame"],
        "show_toast": ["display", "show_toast"],
        "announce_to_chat": ["display", "announce_to_chat"],
        "hidden": ["display", "hidden"],
        "parent": ["parent"]
    }
    def remap_names(obj):
        def dict_gen(array :list, data, level :int = 0):
            if level < len(array):
                return {
                    array[level]: dict_gen(array, data, level + 1)
                }
            else:
                return data

        def deepupdate(a, b):
            for i in b.keys():
                if i not in a:
                    a[i] = b[i]
                elif isinstance(a[i], dict):
                    deepupdate(a[i], b[i]) 
            return a

        out_obj= {}
        for i in obj.keys():
            if i in Remapper.remapping_names:
                out_obj = deepupdate(
                        out_obj,
                        dict_gen(Remapper.remapping_names[i], obj[i])
                )
            else:
                out_obj[i] = obj[i]
        return out_obj
   
    def remap_task(obj):
        if "task" in obj:
            task = Task(obj.pop("task"))
            obj["criteria"] = task.get_criteria()
            obj["requirements"] = task.get_requirements()
        return obj

    def remap_id_to_file(obj):
        filename = ""
        if "id" in obj:
            filename = Mcid(obj.pop("id")).getFilename()
        return (filename, obj)

class Task():
    # basically AND grouping of OR groups
    # "criteria": {
    #   "foo": {
    #       "trigger": "
    def __init__(self, obj):
        self.obj = obj
    def get_criteria(self):
        return self.obj
    def get_requirements(self):
        return self.obj

with open("config.yaml") as file:
    try:
        data = yaml.safe_load(file)
    except:
        print("yaml.safe_load crashed!!!!")
    finally:
        file.close()

entries = []
for category in data:
    entries.append(
        Remapper.remap_category(category)
    )
    if "children" in category:
        for child in category["children"]:
            entries.append(Remapper.remap_child_id(child, category))

for i in range(len(entries)):
    entries[i] = Remapper.remap_features(entries[i])
    entries[i] = Remapper.remap_nbt(entries[i])
    entries[i] = Remapper.remap_names(entries[i])
    entries[i] = Remapper.remap_task(entries[i])
    entries[i] = Remapper.remap_id_to_file(entries[i])
print(json.dumps(entries, indent=4))
   
default_out = '''{
    {parent}
    "display": {
        {background}
		"icon": {
            {nbt}
			"item": "{item}"
        },
		"title": "{title}",
		"description": "{description}",
		"frame": "{frame}",
		"show_toast": {show_toast},
		"announce_to_chat": {announce_to_chat},
		"hidden": {hidden}
    },
	"criteria": {
		"get_stone": {
			"trigger": "minecraft:inventory_changed",
			"conditions": {
				"items": [
					{
						"item": "minecraft:stone"
					}
				]
			}
		},
		"cobblestone": {
			"trigger": "minecraft:inventory_changed",
			"conditions": {
				"items": [
					{
						"item": "minecraft:stone"
					}
				]
			}
		}

	},
	"requirements": [
		[
			"get_stone",
            "cobblestone"
		]
	]
}'''
