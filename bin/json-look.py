#!/usr/bin/env python3

import json
import os
import sys
from collections import Counter

def warn(msg):
    if msg:
        print(msg, file=sys.stderr)

# def get(path, data):
#     key = path.pop(0)
#     if key in data:
#         val = data[key]
#         if path:
#             return get(path, val)
#         else:
#             return val
#     else:
#         return None

def get(path, data):
    if not path or not data:
        return None

    while True:
        key = path.pop(0)
        if key in data:
            val = data[key]
            if path: # still more to do
                data = val
            else:
                return val
        else:
            return None

def main():
    dir_name = os.path.abspath('../data/meta')
    json_files = list(
        filter(lambda f: f.name.endswith('.json'), os.scandir(dir_name)))

    warn('Found {} JSON files'.format(len(json_files)))

    print(','.join(['sample_name', 'biome']))

    #biomes = Counter()
    for i, file in enumerate(json_files):
        warn('{:5}: {}'.format(i + 1, file.name))
        sample_name, _ = os.path.splitext(file.name)

        with open(file) as fh:
            data = json.load(fh)['data']
            biome = get(['relationships', 'biome', 'data', 'id'], data)
            if biome:
                print('biome = {}'.format(biome))

            #print(json.dumps(data, indent=4))
            # if 'relationships' in data:
            #     rel = data['relationships']
            #     if 'biome' in rel:
            #         biome = rel['biome']['data']['id']
            #         #biomes.update([biome])
            #         warn('biome = {}'.format(biome))
            #         print(','.join([sample_name, biome]))
        #break

    print('Done')


main()
