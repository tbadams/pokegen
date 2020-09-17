import re
import json
import csv
import random

KEY_CLASSIFICATION = "classfication"
KEY_HEIGHT = "height_m"
KEY_NAME = "name"
KEY_DEX_NUM = "pokedex_number"
KEY_TYPE1 = "type1"
KEY_TYPE2 = "type2"
KEY_WEIGHT = "weight_kg"
KEY_GEN = "generation"


def parse(in_file, handle_row):
    file = open(in_file, "r")
    reader = csv.DictReader(file, delimiter=',')
    for row in reader:
        handle_row(row)

def print_pokemon(row):
    return [
            "<*-----\n",
            "Name: " + row[KEY_NAME] + "\n",
            "Category: " + row[KEY_CLASSIFICATION] + "\n",
            "Type: " + row[KEY_TYPE1] + " " + row[KEY_TYPE2] + "\n",
            "Height: " + row[KEY_HEIGHT] + "m\n",
            "Weight: " + row[KEY_WEIGHT] + "kg\n",
            "-----*>\n",
            "\n"]

pokemon_data = []
parse("datasets_2756_4568_pokemon.csv", lambda row: pokemon_data.append(print_pokemon(row)))
random.seed(802)
random.shuffle(pokemon_data)
line_data = []
for pokemon in pokemon_data:
    for line in pokemon:
        line_data.append(line)
out = open("poke_data.txt", "w")
out.writelines(line_data)





