import json
import sys

EXCLUDED_SETS = ('archenemy', 'box', 'draft_innovation', 'funny',
                 'masterpiece', 'memorabilia', 'planechase', 'token',
                 'treasure_chest', 'vanguard')


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
    skipped_set_codes = set()
    skipped_cards = set()
    for card_set in mtg_sets_json.values():
        if is_skippable_set(card_set):
            skipped_set_codes.add(card_set['code'])
        for card in card_set['cards']:
            if card['name'] in cards_seen:
                continue
            if is_skippable_card(card):
                skipped_cards.add(card['name'])
                continue
            cards_seen.add(card['name'])
            key = card['name'].upper()
            simplified_cards[key] = create_simplified_card(card,
                                                           skipped_set_codes)
    # uncomment for debugging
    # print(list(sorted(skipped_cards)))
    # print(list(sorted(skipped_set_codes)))
    return simplified_cards


def is_skippable_set(card_set):
    return ((card_set['type'] in EXCLUDED_SETS and card_set['code'] != 'MH1')
            or card_set['isFoilOnly']
            or card_set['isOnlineOnly'])


def is_skippable_card(card):
    return not card.get("isPaper")


def create_simplified_card(card, skipped_set_codes):
    return {
        'name': card['name'],
        'printings': list(
            filter(lambda p: p not in skipped_set_codes and len(p) <= 3,
                   card['printings'])
        ),
        'rarity': card['rarity'],
        'colors': flatten_colors(card),
        'cmc': card['convertedManaCost'],
        'mana_cost': card.get('manaCost'),
        'types': card['types']
    }


def flatten_colors(card):
    colors = card['colors']
    if len(colors) > 1:
        colors = ''.join(sorted(colors, key=lambda c: 'WUBRG'.find(c)))
    elif len(colors) == 1:
        colors = colors[0]
    elif set(card['types']).intersection({'Land', 'Gate'}) != set():
        colors = 'L'
    else:
        colors = 'C'
    return colors


def write_simplified_cards_as_json(simplified_cards, card_data_output_path):
    with open(card_data_output_path, 'w') as write_file:
        json.dump(simplified_cards, write_file, indent=2)


if __name__ == '__main__':
    main()
