import yaml
import json

class Mcid():
    # minecraft:name
    # minecraft:folder/name
    # minecraft:folder/folder/name
    def __init__(self, identifier : str):
        namespace, rest = identifier.split(":")
        location = rest.split("/")
        name = location.pop(-1)

        self.namespace = namespace
        self.location = location
        self.name = name

    def getId(self) -> str:
        output = self.namespace + ":"

        for i in self.location:
            output = output + i + "/"

        if output[-1] != ":":
            output = output [:-1]

        output = output + self.name
        return output

    def getFolder(self, subfolder="", fileending=".json") -> str:
        output = "data/" + self.namespace + "/"
        if subfolder != "":
            output = output + subfolder + "/"
        
        for i in self.location:
            output = output + i + "/"

        output = output + self.name + fileending
        return output

criteria_requirements = '''
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
}
'''


default_out = '''{brackets_open}
    {parent}
    "display": {brackets_open}
        {background}
		"icon": {brackets_open}
            {nbt}
			"item": "{item}"
        {brackets_close},
		"title": "{title}",
		"description": "{description}",
		"frame": "{frame}",
		"show_toast": {show_toast},
		"announce_to_chat": {announce_to_chat},
		"hidden": {hidden}
    {brackets_close},
    {criteria_requirements}
{brackets_close}'''

def access_helper(obj, location):
    try:
        for i in location:
            if i in obj:
                obj = obj[i]
            else:
                print("Error!!!")
                print("While reading {} from {} in obj: {}".format(i, str(location), str(obj)))
                exit(2)
        return obj
    except:
        print("An Error Occoured!")
        exit(3)


def id_helper(parent_id :str, child_id :str) -> str:
    return parent_id + "/" + child_id

def task_helper(obj) -> str:
    return access_helper(obj, ["task"])

def combine(name :str, identifier :str, desc :str, task :str, features, icon :str, nbt :str = "", parent :str = "", background :str = ""):
    global default_out
    if parent != "":
        parent = '"parent": "{}",'.format(parent)

    if background != "":
        background = '"background": "{}",'.format(background)

    if nbt != "":
        nbt = '"nbt": "{}",'.format(nbt)

    [frame, toast, chat, hidden] = features
    print(task)
    criteria_requirements = ""

    return (
        Mcid(identifier).getFolder(),
        default_out.format(
            brackets_open = '{',
            brackets_close = '}',
            parent = parent,
            background = background,
            nbt = nbt,
            item = icon,
            title = name,
            description = desc,
            frame = frame,
            show_toast = toast,
            announce_to_chat = chat,
            hidden = hidden,
            criteria_requirements = criteria_requirements#XXX
        )
    )


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
        out_obj = {}
        def recursive_write(array :list, data, level :int = 0):
            if level < len(array):
                return {
                    array[level]: recursive_write(array, data, level + 1)
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

        for i in obj.keys():
            if i in Remapper.remapping_names:
                out_obj = deepupdate(
                        out_obj,
                        recursive_write(Remapper.remapping_names[i], obj[i])
                )
            else:
                out_obj[i] = obj[i]
        return out_obj
    
    def remap_id_to_file(obj):
        filename = ""
        if "id" in obj:
            filename = Mcid(obj.pop("id")).getFolder()
        return (filename, obj)

with open("config.yaml") as file:
    try:
        data = yaml.safe_load(file)
        file.close()
    except:
        print("yaml.safe_load crashed!!!!")
        file.close()
        exit(1)

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
    entries[i] = Remapper.remap_id_to_file(entries[i])
print(json.dumps(entries, indent=4))

   
default_out = '''{
    {parent}
    "display": {
		"show_toast": {show_toast},
		"announce_to_chat": {announce_to_chat},
		"hidden": {hidden}
    },
    {criteria_requirements}
}'''




'''
try:
    for category in data:
        entries.append(combine(
            access_helper(category, ["category"]),
            access_helper(category, ["id"]) + "/root",
            access_helper(category, ["description"]),
            task_helper(category),
            feature_helper(category),
            access_helper(category, ["icon"]),
            nbt = nbt_helper(category),
            background = access_helper(category, ["background"])
        ))

        for child in access_helper(category, ["children"]):
            entries.append(combine(
                access_helper(child, ["name"]),
                id_helper(access_helper(category, ["id"]), access_helper(child, ["id"])),
                access_helper(child, ["description"]),
                task_helper(child),
                feature_helper(child),
                access_helper(child, ["icon"]),
                nbt = nbt_helper(child),
                parent = id_helper(access_helper(category, ["id"]), access_helper(child, ["parent"]))
            ))
except Exception as e:
    print("something went wrong!!!")
    print(e)
'''
#print(json.dumps(entries, indent=4))
