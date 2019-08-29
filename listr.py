import json
import sys
from mako.template import Template
from mako.lookup import TemplateLookup

CUTOFF_SET_CODE = 'HOU'
SET_RELEASE_DATE_FILE_PATH = 'data/set_release_dates.json'
ALL_CARDS_FILE_PATH = 'data/all_cards.json'
CONFIG_FILE_PATH = 'data/config.cnf'
PAGE_SEPARATOR = '------------------------------------------------------------'


# SRCNO = set, rarity, color, name order
#   CNO = color, name order


# Point to the location of the card list and where you want the output
# card_objects is built in this order:
#    open the user's cardlist and make it into a python list
#    open the all_cards.json and return all json entries that match the cards
#      in the card list; we can ditch the card list after this step
#    card_objects is a list of dictionaries

# Figure out which sets are standard so they can be formatted in SRCNO or CNO
def main():
    (card_list_file_path, formatted_list_output_path) = get_cmd_args()

    print(f"Reading Card List from {card_list_file_path} ...")
    requested_cards = get_card_objects(get_card_name_list(card_list_file_path))
    print(f"Done building card_objects")

    # Commenting this out for now
    #sets_requiring_SRCNO = get_all_sets_after(CUTOFF_SET_CODE)

    sets_requiring_SRCNO = get_standard_sets(CONFIG_FILE_PATH)
    (listings_for_SRCNO, listings_for_CNO) = generate_listings(requested_cards,
                                sets_requiring_SRCNO)

    SRCNO_listings = SRCNO_sort(listings_for_SRCNO)
    CNO_listings = CNO_sort(listings_for_CNO)

    output_listings(SRCNO_listings + CNO_listings,
                    formatted_list_output_path)


def get_standard_sets(config_file):
    ''' Get the standard sets from the config file '''
    standard_sets = []
    with open(config_file, encoding='utf-8') as read_file:
        config_lines = read_file.readlines()
        for line in config_lines:
            standard_sets.append(line.strip())
    return standard_sets


# Needs work; not sure it's doing what we originally envisioned
def generate_listings(card_list, sets_requiring_SRCNO):
    ''' Builds a list of cards grouped based on SRCNO or CNO
    listing. '''
    # Currently, this just splits the list of dictionaries into two lists
    #so we'll have to make some changes to this
    SRCNO_cards = []
    CNO_cards = []
    seen_CNO_card_names = set()
    for card_name in card_list:
        current_card_printings = card_name.get('printings')
        for printing in current_card_printings:
            if card_name['rarity'] in ('rare', 'mythic') or \
               printing in sets_requiring_SRCNO:
                SRCNO_cards.append(create_listing(card_name, printing, 'SRCNO'))
            else:
                CNO_listing = create_listing(card_name, printing, 'CNO')
                if CNO_listing['name'] not in seen_CNO_card_names:
                    CNO_cards.append(CNO_listing)
                    seen_CNO_card_names.add(CNO_listing['name'])
    return (SRCNO_cards, CNO_cards)


def create_listing(card_object, printing, sort_type):
    ''' Puts a card object into SRCNO format '''
    listing = {
        'set': printing,
        'rarity':card_object['rarity'],
        'color': card_object['colors'],
        'name': card_object['name'],
        'sort_type': sort_type
    }
    return listing


def SRCNO_sort(listings):
    return sorted(sorted(CNO_sort(listings), key=lambda l: l['rarity']),
                  key=lambda l: l['set'])


def CNO_sort(listings):
    return sorted(sorted(listings, key=lambda l: l['name']),
                  key=lambda l: l['color'])


# This may be bugged; gonna test it, standalone, in IDLE
def get_card_name_list(card_list_file_path):
    ''' Builds a list of a cards using a user provided file \n
    The file will be provided when the listr.py script is run through the
    CLI '''
    card_list = []
    with open(card_list_file_path) as read_file:
        for card in read_file:
            card_list.append(card.strip())
        return card_list


def get_all_cards_json(all_cards_file_path):
    ''' Helper function for get_card_objects '''
    with open(all_cards_file_path, encoding='utf-8') as read_file:
        return json.load(read_file)


def get_card_objects(card_list):
    ''' returns a list of dictionaries using all_cards.json \n
    card_list : a list of cards built using get_card_name_list() '''
    found_cards = []
    all_cards_json = get_all_cards_json(ALL_CARDS_FILE_PATH)
    for card_name in card_list:
        card_object = all_cards_json.get(card_name.upper(), "NOT FOUND")
        if card_object == "NOT FOUND":
            print(f"{card_name} not found!")
        else:
            found_cards.append(card_object)
    print(f"Found {len(found_cards)} / {len(card_list)} cards")
    return found_cards


def get_cmd_args():
    ''' Helper function to get CLI arguments '''
    return (sys.argv[1], sys.argv[2])


def output_listings(listings, output_file_path):
    if output_file_path.split('.')[-1] == 'html':
        output_func = output_html_listings
    else:
        output_func = output_python_listings
    return output_func(listings, output_file_path)


def output_python_listings(listings, output_file_path):
    with open(output_file_path, 'w') as f:
        f.write('\n'.join([str(listing) for listing in listings]))


def output_html_listings(listings, output_file_path):
    template_lookup = TemplateLookup(directories=['./'])
    output_template = Template(filename="templates/out_list_template.mako",
                               lookup=template_lookup)
    listings_output = output_template.render(listings=listings)
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(listings_output)

if __name__ == '__main__':
    main()
