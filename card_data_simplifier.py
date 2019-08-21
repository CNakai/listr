import json
import sys


def main():
	(mtg_sets_file_path, card_data_output_path) = get_cmd_args()

	print(f"Reading JSON from {mtg_sets_file_path} ...")
	mtg_sets_json = get_mtg_sets_json(mtg_sets_file_path)
	print("Done!")

	print("Getting simplified card data...")
	simplified_cards = get_card_data(mtg_sets_json)
	print("Done!")

	print("Writing simplified card data...")
	write_simplified_cards_as_json(simplified_cards, card_data_output_path)
	print("Done!")


def get_cmd_args():
	return (sys.argv[1], sys.argv[2])


def get_mtg_sets_json(mtg_sets_file_path):
	with open(mtg_sets_file_path, encoding='utf-8') as read_file:
		return json.load(read_file)


def get_card_data(mtg_sets_json):
	simplified_cards = {}
	cards_seen = set()
	for card_set in mtg_sets_json.values():
		if is_skippable_set(card_set):
			continue
		for card in card_set['cards']:
			if card['name'] in cards_seen or is_skippable_card(card):
				continue
			cards_seen.add(card['name'])
			simplified_cards[card['name'].upper()] = create_simplified_card(card)
	return simplified_cards


def is_skippable_set(card_set):
	excluded_sets = ('funny', 'box', 'promo', 'memorabilia', 'starter',
	                 'vanguard', 'masterpiece')
	return card_set['type'] in excluded_sets


def is_skippable_card(card):
	return card.get("isPaper") is False


def create_simplified_card(card):
	return {
		'name': card['name'],
		'printings': card['printings'],
		'rarity': card['rarity'],
		'colors': flatten_colors(card)
	}


def flatten_colors(card):
	colors = card['colors']
	if len(colors) > 1:
		colors = 'MC:' + ''.join(colors)
	elif len(colors) == 1:
		colors = colors[0]
	elif card['type'].lower() == 'land':
		colors = 'L'
	else:
		colors = 'C'
	return colors


def write_simplified_cards_as_json(simplified_cards, card_data_output_path):
	with open(card_data_output_path, 'w') as write_file:
		json.dump(simplified_cards, write_file, indent=2)


if __name__ == '__main__':
	main()
