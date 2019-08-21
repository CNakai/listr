import json
import sys

CUTOFF_SET_CODE = 'HOU'
SET_RELEASE_DATE_FILE_PATH = 'data/set_release_dates.json'
ALL_CARDS_FILE_PATH = 'data/all_cards.json'


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
    requested_cards = get_card_objects(get_card_name_list())
    print(f"Done building card_objects")

    sets_requiring_srcno = get_all_sets_after(CUTOFF_SET_CODE)
    (listings_for_SRCNO, listings_for_CNO) = generate_listings(requested_cards,
                                sets_requiring_SRCNO)
    SRCNO_listings = SRCNO_sort(listings_for_SRCNO)
    CNO_listings = CNO_sort(listings_for_CNO)

    output_listings([SRCNO_listings, CNO_listings])


# Needs work; not sure it's doing what we originally envisioned
def generate_listings(card_list, sets_requiring_SRCNO):
    ''' Builds a list of cards grouped based on SRCNO or CNO
    listing. '''
    # Currently, this just splits the list of dictionaries into two lists
    #so we'll have to make some changes to this
    SRCNO_cards = []
    CNO_cards = []
    for card_name in card_list:
        current_card_printings = card_name.get('printings')
        for printing in current_card_printings:
            if printing in sets_requiring_SRCNO or \
               card_name['rarity'] in ('rare', 'mythic'):
                SRCNO_cards.push(create_SRCNO_entry(card_name, printing))
            else:
                if card_name not in CNO_cards:
                CNO_cards.push(create_CNO_entry(card_name))
    return (SRCNO_cards, CNO_cards)


def create_SRCNO_entry(card_object, printing):
    ''' Puts a card object into SRCNO format '''
    ret_string = (f"{printing}, {card_object.get('rarity')}, \
    {card_object.get('colors')}, {card_object.get('name')}")
    return ret_string


def create_CNO_entry(card_object):
    ''' Puts a card object into CNO format '''
    ret_string = (f"{card_object.get('colors')}, {card_object.get('name')}")
    return ret_string


# This may be bugged; gonna test it, standalone, in IDLE
def get_card_name_list(card_list_file_path):
    ''' Builds a list of a cards using a user provided file \n
    The file will be provided when the listr.py script is run through the
    CLI '''
    card_list = []
    with open(card_list_file_path) as read_file:
        for card in read_file:
            card_list.push(card.strip())
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
        card_object = all_card_json.get(card_name.upper(), "NOT FOUND")
        if card_object == "NOT FOUND":
            print(f"{card_name} not found!")
        else:
            found_cards.push(card_object)
    print(f"Found {len(found_cards)} / {len(card_list)} cards")
    return found_cards


def get_cmd_args():
    ''' Helper function to get CLI arguments '''
    return (sys.argv[1], sys.argv[2])


def get_all_sets_after(cutoff_set_code):
    ''' Builds a list containing the sets that are currently in standard \n
    cutoff_set_code : a string representing the 3 character set code as
    defined by WOTC '''
    with open(SET_RELEASE_DATE_FILE_PATH) as SRDF:
        set_code_release_date_pairs = json.read(SRDF)
    cutoff_date = set_code_release_date_pairs[CUTOFF_SET_CODE]
    return [set_code for set_code
        in set_code_release_date_pairs.keys()
        if set_code_release_date_pairs[set_code] > cutoff_date]




# Listings:
# A listing is the printable version of a card's set, color, rarity, and name
# data.  One listing is emitted for *all printings* of a card that falls under
# the simple sorting algorithm.  One listing is emitted *per printing* of a card
# that falls under the complex sorting algorithm (rares, mythics, and standard
# sets).
