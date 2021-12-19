#!/usr/share/python

import json

class DictTools:
    def deepdictgen(a, array :list, data):
        if len(array) == 0:
            return data
        name = array.pop(0)
        if name not in a:
            a[name] = {}
        if isinstance(a[name], dict):
            a[name] = DictTools.deepdictgen(a[name], array, data)
        return a
    
    def deepread(a, array :list):
        if len(array) == 0:
            return a
        name = array.pop(0)
        return DictTools.deepread(a[name], array)

class DictRemapper:
    def __init__(self, config, seperator :str = "/"):
        self.config = {}

        for i in config:
            DictTools.deepdictgen(
                self.config,
                i.split(seperator),
                config[i].split(seperator)
            )

    def remap(self, data):

        def recursion_remapper(in_data, config, out_data :dict = {}):
            for i in in_data:
                if i in config:
                    if isinstance(config[i], list):
                        DictTools.deepdictgen(out_data, config[i].copy(), in_data[i])
                    else:
                        recursion_remapper(in_data[i], config[i], out_data)
                else:
                    out_data[i] = in_data[i]
            return out_data


        return recursion_remapper(data, self.config)

    def example():
        remapper = DictRemapper({
            "foo/bar": "baz/java",
            "hello/world": "python/c",
            "list": "ilikepython",
            "setset/inner": "set"
        })

        in_data = {
            "foo": {
                "bar": 42
            },
            "hello": {
                "world": 23
            },
            "list": [
                42, 23, 44, 41, 43
            ],
            "setset": {
                "inner": ["bla", "blupp"]
            },
            "retro": 42
        }

        out_data = {
            "baz": {
                "java": 42
            },
            "python": {
                "c": 23
            },
            "ilikepython": [
                42, 23, 44, 41, 43
            ],
            "set": ["bla", "blupp"],
            "retro": 42
        }

        def log(obj):
            print(json.dumps(obj, indent=4, sort_keys=True))

        log(remapper.remap(in_data))
        log(out_data)

