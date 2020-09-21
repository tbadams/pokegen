import pokeapi
# import gpt_2_simple as gpt2
import os

entries = pokeapi.get_pokedex_entries()
names = pokeapi.get_pokemon_names(entries)

# pokeapi.decode_file("out/gpoke3c_temp1.0_k0_p0.0.txt", names)
dir_path = os.path.dirname(os.path.realpath(__file__))
target_path = "/out/g3c_1200/"
f = []
for (dirpath, dirnames, filenames) in os.walk(dir_path + target_path):
    full_filenames = []
    for fn in filenames:
        if fn.endswith("txt"):
            full_filenames.append(os.path.join(dirpath, fn))
    f.extend(full_filenames)
    break
# print(str(f))
pokeapi.decode_file_group(f, names)
# for file in f:
#     try:
#         pokeapi.decode_file(file, names)
#     except UnicodeDecodeError as e:
#         print("couldn't parse file {}: {}".format(file, e))
