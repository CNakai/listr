import sys

CUTOFF_SET_CODE = 'HOU'
SET_RELEASE_DATE_FILE_PATH = 'set_release_dates.json'


def main():
	# Collect card sets that require 'complex' sorting
	sets_requiring_further_sorting = get_all_sets_after(CUTOFF_SET_CODE)
	card_listings = get_card_listings(get_card_objects(get_card_name_list()))
	(cs_listings, ss_listings) = separate_listings(card_listings,
	                                               sets_requiring_further_sorting)
	cs_listings = complex_sort(cs_listings)
	ss_listings = simple_sort(ss_listings)

	output_listings([cs_listings, ss_listings])


# TODO: Ask about sorting of commander sets
def get_all_sets_after(CUTOFF_SET_CODE):
	with open(SET_RELEASE_DATE_FILE_PATH) as SRDF:
		set_release_date_pairs = json.read(SRDF)
	cutoff_date = set_release_date_pairs[CUTOFF_SET_CODE]
	return [set_date_pair[0] for set_date_pair
	        in set_release_date_pairs.items()
	        if set_date_pair[1] > cutoff_date]


	# For the first, simply order alphabetically within color (group multicolor)
	# For the second, order alphabetically within color within rarity within set
	# Output sorted list entries one per line
