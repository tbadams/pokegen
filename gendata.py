import pokeapi

import random

random.seed(802)  # arbitrary
entries = pokeapi.get_pokedex_entries()
names = pokeapi.get_pokemon_names(entries)
encoded_entries = pokeapi.get_encoded(entries, 2)

pokeapi.lines_to_file("poke_names" + pokeapi.VERSION, names)  # write names
pokeapi.write_display_entries(entries, "poke_dex")
# Actual gen data
pokeapi.get_stats("encoded data", encoded_entries)
pokeapi.lines_to_file("poke_data", encoded_entries)
pokeapi.lines_to_file("poke_data" + pokeapi.VERSION, encoded_entries)
