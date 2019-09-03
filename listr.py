import json
import re
import sys
from mako.template import Template
from mako.lookup import TemplateLookup

def _get_all_card_data(all_card_data_path):
    with open(all_card_data_path, encoding='utf-8') as card_data_file:
        return json.load(card_data_file)


def _get_sets_requiring_SRCN_order(config_file_path):
    with open(config_file_path, encoding='utf-8') as config_file:
        config_lines = config_file.readlines()
    return list(map(lambda line: line.strip(), config_lines))


ALL_CARD_DATA_PATH = 'data/all_cards.json'
ALL_CARD_DATA = _get_all_card_data(ALL_CARD_DATA_PATH)

CONFIG_FILE_PATH = 'data/config.cnf'
SETS_REQUIRING_SRCN_ORDER = _get_sets_requiring_SRCN_order(CONFIG_FILE_PATH)

# SRCN Order = set, rarity, color, name order
#   CN Order = color, name order


def main():
    (requests_file_path, output_path) = get_cmd_args()

    # TODO: Reinstate summary output
    (requests, unparseable_lines) = get_requests(requests_file_path)
    print(unparseable_lines) # TODO: prettier output
    (enriched_requests, requests_for_unknown_cards) = enrich_requests(requests)
    print(requests_for_unknown_cards)
    output_enriched_requests(enriched_requests, output_path)


def get_cmd_args():
    return (sys.argv[1], sys.argv[2])


def get_requests(card_requests_file_path):
    '''Creates dictionaries representing card requests from the file at the
    provided path.  The request file should contain one request per line
    consisting of a quantity, the card's name, and any restrictions on the
    printings desired (preferred, excluded, and/or required).  Any unparseable
    lines in the file (along with their line numbers) are stored in a list that
    is returned along with the card request dictionaries.

    '''
    with open(card_requests_file_path) as requests_file:
        request_lines = requests_file.readlines()

    requests = []
    unparseable_lines = [] #FIXME: Better name, it's a list of triples
    for (line_number, request_line) in enumerate(request_lines, start=1):
        try:
            requests.append(parse_request_line(request_line, line_number))
        except SyntaxError as error:
            unparseable_lines.append((line_number, request_line, str(error)))
    return (requests, unparseable_lines)


def parse_request_line(request_line, line_number):
    request_line = request_line.strip()
    request_line_regexp = r"(^[0-9]{0,2}\s+)?([\w/', \-]+(?!\|))(?:(?:\s+\|)((?: \w{3,4})+)$)?"

    result = re.match(request_line_regexp, request_line, flags=re.MULTILINE)
    if not result:
        raise SyntaxError(f"Malformed request on line {line_number}")
    (quantity, name, printing_prefs) = result.groups()

    try:
        quantity = int(quantity.strip()) if quantity else 1
    except ValueError:
        raise SyntaxError(f"Invalid quantity on line {line_number}")

    if request_line[result.end(2):] != '' and printing_prefs is None:
        raise SyntaxError(f"Invalid printing preferences on line {line_number}")

    if printing_prefs:
        printing_prefs = printing_prefs.strip().split(' ')

    return {
        'name': name.strip(),
        'quantity': quantity,
        'printing_prefs': printing_prefs,
        'line_number': line_number
    }


def enrich_requests(requests):
    enriched_requests = []
    requests_for_unknown_cards = []
    for request in requests:
        card_data = lookup_card_data_by_name(request['name'], ALL_CARD_DATA)
        if card_data:
            enriched_requests.append(enrich_request(request, card_data))
        else:
            requests_for_unknown_cards.append(request)
    return (enriched_requests, requests_for_unknown_cards)


def lookup_card_data_by_name(card_name, card_data):
    if '//' in card_name:
        card_name = card_name.split('//')[0].strip()
    return card_data.get(card_name.upper())


def enrich_request(request, card_data):
    enriched_request = {**request, **card_data}
    enriched_request['printings'] = get_orderings_for_printings(card_data)
    del enriched_request['line_number']
    return enriched_request


def get_orderings_for_printings(card_data):
    printing_ordering_pairs = {}
    for printing in card_data['printings']:
        if card_data['rarity'] in ('rare', 'mythic') \
           or printing in SETS_REQUIRING_SRCN_ORDER:
            ordering = 'SRCN_order'
        else:
            ordering = 'CN_order'

        printing_ordering_pairs[printing] = 'SRCN_order'
    return printing_ordering_pairs



def output_enriched_requests(enriched_requests, output_path):
    if output_path.split('.')[-1] == 'html':
        output_func = output_html
    else:
        output_func = output_python
    return output_func(enriched_requests, output_path)


def output_html(enriched_requests, output_path):
    template_lookup = TemplateLookup(directories=['./'])
    output_template = Template(filename="templates/out_list_template.mako",
                               lookup=template_lookup)
    output = output_template.render(requests=enriched_requests)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(listings_output)


def output_python(enriched_requests, output_path):
    with open(output_path, 'w') as f:
        f.write('\n'.join([str(request) for request in enriched_requests]))


if __name__ == '__main__':
    main()
