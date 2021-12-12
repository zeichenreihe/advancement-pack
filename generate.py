import yaml

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

with open("config.yaml") as file:
    try:
        data = yaml.safe_load(file)
        file.close()
    except:
        print("yaml.safe_load crashed!!!!")
        file.close()
        exit(1)

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

def nbt_helper(obj):
    nbt = ""
    if "nbt" in obj:
        nbt = str(obj["nbt"]).replace("'","\\\"")
    if "nbt_str" in obj:
        nbt = obj["nbt_str"]
    return nbt

def task_helper(obj):
    return obj["task"]

def feature_helper(obj):
    return obj["features"]

def combine(name :str, identifier :str, desc :str, task :str, features, icon :str, nbt :str = "", parent :str = "", background :str = ""):
    global default_out
    if parent != "":
        parent = '"parent": "{}",'.format(parent)

    if background != "":
        background = '"background": "{}",'.format(background)

    if nbt != "":
        nbt = '"nbt": "{}",'.format(nbt)

    frame = "task"
    if "display" in features:
        frame = features["display"]
    show_toast = "true"
    if "pop_up" in features:
        toast = str(features["pop_up"]).lower()
    chat = "true"
    if "chat" in features:
        chat = str(features["chat"]).lower()
    hidden = "false"
    if "hidden" in features:
        hidden = str(features["hidden"]).lower()

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

entries = []

for category in data:
    entries.append(combine(
        category["category"],
        category["id"] + "/root",
        category["description"],
        task_helper(category),
        feature_helper(category),
        category["icon"],
        nbt = nbt_helper(category),
        background = category["background"]
    ))

    for child in category["children"]:
        entries.append(combine(
            child["name"],
            child["id"],
            child["description"],
            task_helper(child),
            feature_helper(child),
            child["icon"],
            nbt = nbt_helper(child),
            parent = child["parent"]
        ))

print(entries)

