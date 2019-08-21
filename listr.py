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
    requested_cards = get_card_objects(get_card_name_list(card_list_file_path))
    print(f"Done building card_objects")

    sets_requiring_SRCNO = get_all_sets_after(CUTOFF_SET_CODE)
    (listings_for_SRCNO, listings_for_CNO) = generate_listings(requested_cards,
                                sets_requiring_SRCNO)
    SRCNO_listings = SRCNO_sort(listings_for_SRCNO)
    CNO_listings = CNO_sort(listings_for_CNO)

    output_listings(SRCNO_listings + CNO_listings,
                    formatted_list_output_path)


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
            if card_name['rarity'] in ('rare', 'mythic') or \
               printing in sets_requiring_SRCNO:
                SRCNO_cards.append(create_listing(card_name, printing, 'SRCNO'))
            else:
                CNO_listing = create_listing(card_name, printing, 'CNO')
                if CNO_listing not in CNO_cards:
                    CNO_cards.append(CNO_listing)
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


def get_all_sets_after(cutoff_set_code):
    ''' Builds a list containing the sets that are currently in standard \n
    cutoff_set_code : a string representing the 3 character set code as
    defined by WOTC '''
    with open(SET_RELEASE_DATE_FILE_PATH) as SRDF:
        set_code_release_date_pairs = json.load(SRDF)
    cutoff_date = set_code_release_date_pairs[CUTOFF_SET_CODE]
    return [set_code for set_code
        in set_code_release_date_pairs.keys()
        if set_code_release_date_pairs[set_code] > cutoff_date]


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
    prefix = """
<!DOCTYPE html>
<html>
  <head>
    <title>Listr</title>
    <style>
      span {
        display: inline-block;
      }
      .set {
        width: 3em;
      }
      .rarity {
        width: 5.5em;
      }
      .color {
        width: 4em;
      }
    </style>
  </head>

  <body>
"""

    suffix = """
    <script type="text/javascript">
      function setUpListeners() {
        for (let cb of document.querySelectorAll('input')) {
          cb.addEventListener('change', checkboxListener)
        }
      }

      function checkboxListener() {
        console.log(this)
        const card_name = this.parentNode.dataset['name']
        const set = this.parentNode.dataset['set']
        const all_occurrences = document.querySelectorAll(`[data-name="${card_name}"]`)

        for (const occurrence of all_occurrences) {
          if (this.checked && set !== occurrence.dataset['set']) {
            occurrence.style.display = 'none'
          } else {
            occurrence.style.display = 'block'
          }
        }
      }

      setUpListeners()
    </script>
  </body>
</html>
"""
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(prefix)
        for listing in listings:
            f.write(f"""
    <div data-name="{listing['name']}" data-set="{listing['set']}">""")
            if listing['sort_type'] == 'SRCNO':
                f.write(f"""
      <input type="checkbox"> | <span class="set">{listing['set']}</span> | <span class="rarity">{listing['rarity']}</span> | <span class="color">{listing['color']}</span> | <span class="name">{listing['name']}</span>""")
            else:
                f.write(f"""
      <input type="checkbox"> | <span class="color">{listing['color']}</span> | <span class="name">{listing['name']}</span>""")
            f.write("""
    </div>""")
        f.write(suffix)

if __name__ == '__main__':
    main()
