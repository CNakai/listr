import json
import sys

CUTOFF_SET_CODE = 'HOU'
SET_RELEASE_DATE_FILE_PATH = 'data/set_release_dates.json'


def main():
	# Collect card sets that require 'complex' sorting
	sets_requiring_further_sorting = get_all_sets_after(CUTOFF_SET_CODE)
	card_objects = get_card_objects(get_card_name_list())
	(cs_listings, ss_listings) = generate_listings(card_objects,
	                                               sets_requiring_further_sorting)
	cs_listings = complex_sort(cs_listings)
	ss_listings = simple_sort(ss_listings)

	output_listings([cs_listings, ss_listings])


def get_all_sets_after(cutoff_set_code):
	with open(SET_RELEASE_DATE_FILE_PATH) as SRDF:
		set_code_release_date_pairs = json.read(SRDF)
	cutoff_date = set_code_release_date_pairs[CUTOFF_SET_CODE]
	return [set_code for set_code
	        in set_code_release_date_pairs.keys()
	        if set_code_release_date_pairs[set_code] > cutoff_date]


	# For the first, simply order alphabetically within color (group multicolor)
	# For the second, order alphabetically within color within rarity within set
	# Output sorted list entries one per line



# Listings:
# A listing is the printable version of a card's set, color, rarity, and name
# data.  One listing is emitted for *all printings* of a card that falls under
# the simple sorting algorithm.  One listing is emitted *per printing* of a card
# that falls under the complex sorting algorithm (rares, mythics, and standard
# sets).
