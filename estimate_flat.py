from itertools import permutations
import numpy as np
import matplotlib.pyplot as plt
import json
from PIL import Image

locations = {
    "E": "Entrance",
    "1": "Chair shelf",
    "2": "Middle table",
    "3": "Lever",
    "4": "Below lever",
    "5": "Lever shelf",
    "A": "First socket from left",
    "B": "Second socket",
    "C": "Third socket",
    "D": "Fourth socket"
}

coords = { # coords are only for visualization on the diagram
    "E": (256, 830),
    "1": (28, 353),
    "2": (487, 371),
    "3": (776, 718),
    "4": (830, 134),
    "5": (831, 26),
    "A": (204, 31),
    "B": (316, 31),
    "C": (604, 31),
    "D": (716, 31),
}

detours_to = { # detours always required to reach these targets
    "1": (85, 569),
    "5": (813, 208)
}

detours_to_from = { # detours required when going to a specific target, from another specific origin
    "2": {
        "E": (255, 273)
    },
    "3": {
        "A": (601, 268),
        "B": (601, 268),
    },
    "A": {
        "3": (601, 268),
    },
    "B": {
        "3": (601, 268),
    }
}

# VERY rough estimates of distances (arbitrary unit) between locations
with open("distances.json", "r") as infile:
    distances = json.loads(infile.read())

distances_from_to = distances["distances_from_to"]
extra_time_3_to_4_to_socket = distances["extra_time_3_to_4_to_socket"]
extra_time_3_to_socket_to_5 = distances["extra_time_3_to_socket_to_5"]

# count = 0
# for key, val in distances_from_to.items():
#     count += len(val)
#     print("\n")
#     for target in val:
#         print(f"{key} -> {target}")
# print(count)

start_location = "E"
socket_locations = ["A", "B", "C", "D"]
battery_locations = ["1", "2", "4", "5"]
initial_targets = ["1", "2", "3"]
lever_targets = ["4", "5"] # these are only available _after_ the lever has been reached

must_visit = socket_locations + initial_targets + lever_targets

all_paths = list(permutations(must_visit, len(must_visit)))
valid_paths = []
valid_path_lengths = []

for path in all_paths:
    if any([path.index("3") > path.index(x) for x in lever_targets]): # if the lever comes after any of the lever targets
        continue # skip this path
    if path[0] not in initial_targets:
        continue # first target needs to be 1, 2 or 3, if not skip this path
    path = list(path)

    cur_path = ["E"]
    cur_path_length = 0
    carrying_battery = False
    broken = False
    while path: # simulate the path step by step
        target = path.pop(0)
        if (not carrying_battery and target in socket_locations) or (carrying_battery and target in battery_locations):
            # if a path goes to a socket without the cat carrying a battery OR the cat is carrying a battery and goes to another battery, this path is broken
            broken = True
            break
        cur_path.append(target)
        cur_path_length += distances_from_to[cur_path[-2]][cur_path[-1]]
        if target in battery_locations:
            carrying_battery = True # pick up the battery for the next iteration if the target is a battery
        elif target in socket_locations:
            carrying_battery = False # drop the battery for the next iteration if the target is a socket

    if broken:
        continue # skip broken paths

    if cur_path.index("4") - cur_path.index("3") == 1:
        # if 3 comes immediately before 4, there's an added distance to run from 4 to the sockets
        cur_path_length += extra_time_3_to_4_to_socket

    if cur_path.index("5") - cur_path.index("3") == 2:
        # if 5 comes two steps after 3, there's an added time to wait for the machine
        cur_path_length += extra_time_3_to_socket_to_5

    valid_paths.append(cur_path)
    valid_path_lengths.append(cur_path_length)

inds = np.argsort(valid_path_lengths)

# print("Best:")
# for i in inds[:10]:
#     print(" -> ".join(valid_paths[i]), "  Dist:", f"{valid_path_lengths[i]:.2f}")

# print("Worst:")
# for i in inds[-10:]:
#     print(" -> ".join(valid_paths[i]), "  Dist:", f"{valid_path_lengths[i]:.2f}")

for n, i in enumerate(inds):
    print(f"{n:>4d}:", " -> ".join(valid_paths[i]), "  Dist:", f"{valid_path_lengths[i]:.2f}")

visualize_paths = [
    valid_paths[inds[0]],
    valid_paths[inds[5]],
    valid_paths[inds[17]],
    valid_paths[inds[71]],
    valid_paths[inds[92]],
    valid_paths[inds[-1]],
]

titles = [
    "Fast, but tricky",
    "",
    "",
    "",
    "",
    "Possibly the slowest possible route",
]

fig, axs = plt.subplots(2, 3)

im = Image.open("Flat2.png")
for path, ax, title in zip(visualize_paths, np.ravel(axs), titles):
    ind = valid_paths.index(path)
    ax.imshow(im)
    ax.set_title(f"Path length: {valid_path_lengths[ind]:.2f}  {title}")
    for key, item in coords.items():
        ax.plot(*item, "o", markersize = 10, label = key)

    for subpath_start, subpath_target in zip(path[:-1], path[1:]):
        start_coord = coords[subpath_start]
        target_coord = coords[subpath_target]
        if subpath_target in detours_to:
            detour_coord = detours_to[subpath_target]
            ax.plot([start_coord[0], detour_coord[0], target_coord[0]],
                     [start_coord[1], detour_coord[1], target_coord[1]], color = "black")
        elif subpath_target in detours_to_from and subpath_start in detours_to_from[subpath_target]:
            detour_coord = detours_to_from[subpath_target][subpath_start]
            ax.plot([start_coord[0], detour_coord[0], target_coord[0]],
                        [start_coord[1], detour_coord[1], target_coord[1]], color = "black")
        else:
            ax.plot([start_coord[0], target_coord[0]],
                     [start_coord[1], target_coord[1]], color = "black")

plt.show()