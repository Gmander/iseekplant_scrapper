"""
This module contains functions to scrape data from iSeekPlant website.
It includes functions to get page numbers for a genre search, clear the content of the 
JSON file used for genre search output, and open and process a genre search.
"""

import html  # Import the html module
import json
import os
import re
import csv
import sys
import requests

def get_iseek_genra_search_page_numbers(doc_link):
    """
    Get the page numbers for a genre search on iSeekPlant.

    Args:
        doc_link (str): The URL of the genre search page.

    Returns:
        str: The page number found in the HTML content.

    """
    response = requests.get(doc_link, timeout=100)
    content = response.text

    targets = re.findall(r'<a role="button" class="px-0.5 text-brand-blue focus:outline-none" tabindex="0" aria-label="Page \d+">(\d+)</a>', content)

    # targets = re.findall(
    #     r'<a role="button" class="px-0.5 text-brand-blue focus:outline-none" tabindex="0" '
    #     r'aria-label="Page \d+">(\d+)</a>', 
    #     content
    # )
    for target in targets:
        return(target)

def clear_genra_search_output():
    """
    Clear the content of the JSON file used for genre search output.

    """
    # This will clear the content of the JSON file before writing new content
    open("csvSearchOutput.json", "w", encoding="utf-8").close()

def open_iseek_genra_search(doc_link, genra_name):
    """
    Open and process a genre search on iSeekPlant.

    Args:
        doc_link (str): The URL of the genre search page.
        genra_name (str): The name of the genre.

    """
    response = requests.get(doc_link, timeout=100)
    content = response.text
    new_companies_data = []  # A list to hold dictionaries for each company's new data

    targets = re.findall(r'<h2 class="block sm:flex-1 text-center sm:text-left"><a href="(.+?)">(.+?)</a></h2>', content)

    for target in targets:
        specific_company_response = requests.get('https://www.iseekplant.com.au' + target[0], timeout=100)
        specific_company_content = specific_company_response.text
        
        location_targets = re.findall(r'<li class="font-thin odd:bg-gray-200 p-2 sm:px-8 sm:py-5 text-gray-500 text-sm sm:text-md cursor-pointer">(.+?)</li>', specific_company_content)
        company_info = {
            'name': html.unescape(target[1]),  # Use html.unescape to decode HTML entities
            'link': 'https://www.iseekplant.com.au' + target[0],
            'genra': genra_name,
            'location': location_targets[0] if location_targets else 'N/A',
            'multiLocation': len(location_targets) != 1
        }
        new_companies_data.append(company_info)

    # File path
    file_path = "csvSearchOutput.json"

    # Check if file exists and has content; if so, load existing data, else initialize with empty list
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'r', encoding="utf-8") as outfile:
            existing_data = json.load(outfile)
    else:
        existing_data = []

    # Update existing_data with new_companies_data, avoiding duplicates
    for new_company in new_companies_data:
        # if new_company_data is empty, print no companies found
        if not new_companies_data:
            print("No companies found")
        # Check if the company already exists in existing_data based on a unique field (e.g., 'name' or 'link')
        if not any(company['link'] == new_company['link'] for company in existing_data):
            existing_data.append(new_company)
        else:
            # If the company already exists, and location is not N/A update the existing location with the new data
            if new_company['location'] != 'N/A':
                for company in existing_data:
                    if (company['link'] == new_company['link']) & (company['location'] != new_company['location']):
                        company['location'] = new_company['location']
                        company['multiLocation'] = new_company['multiLocation']
                        print(f"Updated location for {new_company['name']}")

    # Write the combined list of dictionaries to a JSON file
    with open(file_path, "w", encoding="utf-8") as outfile:
        json.dump(existing_data, outfile, indent=4)

def multi_page_iseek_search_n_update(doc_link, start_page_count, end_page_count, genra):
    """
    Perform a multi-page genre search on iSeekPlant and update the search output.

    Args:
        doc_link (str): The URL of the genre search page.
        start_page_count (int): The starting page number.
        end_page_count (int): The ending page number.
        genra (str): The name of the genre.

    """
    for i in range(start_page_count, end_page_count + 1):
        open_iseek_genra_search(doc_link + str(i), genra)
        print(f"Page {i} done")

# Separate regex patterns for each address component
patterns = {
    'street': re.compile(r"(?P<street>[\d-]+\s[A-z\s]+)"),
    'city': re.compile(r"(?P<city>[A-Za-z\s]+)\s[A-z]{3}[,|\s]|(?P<city2>[A-Za-z\s]+)[,|\s]+Australia"),
    'state': re.compile(r"(?P<state>ACT|NSW|NT|QLD|SA|TAS|VIC|WA|Australian Capital Territory|New South Wales|Northern Territory|Queensland|South Australia|Tasmania|Victoria|Western Australia)"),
    'postcode': re.compile(r"(?P<postcode>\d{4})")
}

def extract_address_components(address):
    """
    Extract the address components from a given address.

    Args:
        address (str): The address string.

    Returns:
        dict: A dictionary containing the extracted address components.

    """
    components = {'street': '', 'city': '', 'state': '', 'postcode': ''}
    for key, pattern in patterns.items():
        match = pattern.search(address)
        if match:
            components[key] = match.group(key) if key in match.groupdict() else match.group(key + '2')  # Handle alternative group names
    return components

def convert_json_to_csv_with_mapping(json_file_path, csv_file_path):
    """
    Convert a JSON file to a CSV file with a predefined mapping.

    Args:
        json_file_path (str): The path to the JSON file.
        csv_file_path (str): The path to the CSV file.

    """
    with open(json_file_path, 'r', encoding="utf-8") as json_file:
        data = json.load(json_file)

    with open(csv_file_path, 'w', newline='', encoding="utf-8") as csv_file:
        fieldnames = ['Account Id', 'Account Name', 'Phone', 'Website', 'Account Owner', 'Shipping Street', 'Shipping City', 'Shipping State', 'Shipping Code', 'Shipping Country', 'Status', 'Account Type', 'Industry', 'Created Time', 'Tag', 'Description', 'Currency', 'Exchange Rate']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        
        for entry in data:
            address = entry.get('location', '')  # Assuming the address is under 'address'
            components = extract_address_components(address)

            csv_entry = {
                'Account Name': entry.get('name', ''),
                'Phone': '',  # Assuming you don't have this data; leave empty
                'Website': entry.get('link', ''),
                'Account Owner': 'david@fuellox.com.au',  # Static value
                'Shipping Street': components['street'],
                'Shipping City': components['city'],
                'Shipping State': components['state'],
                'Shipping Code': components['postcode'],
                'Shipping Country': 'Australia',  # Assuming you don't have this data; leave empty
                'Status': 'Pursue',  # Static value
                'Account Type': 'Prospect',  # Static value
                'Industry': 'Civil',  # Static value
                'Created Time': '',  # Assuming you don't have this data; leave empty
                'Tag': entry.get('genra', '') + ',iSeekPlant,pursue',  # Custom logic
                'Description': entry.get('location', ''),
                'Currency': '',  # Assuming you don't have this data; leave empty
                'Exchange Rate': ''  # Assuming you don't have this data; leave empty
            }
            writer.writerow(csv_entry)

def exclusive_update():
    """
    Update the location of companies whose location is N/A.

    Returns:
        int: The number of companies that needed an update.

    """
    # File path
    file_path = "csvSearchOutput.json"
    need_update_count = 0
    updated_count = 0

    # Check if file exists and has content; if so, load existing data, else initialize with empty list
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'r', encoding="utf-8") as outfile:
            existing_data = json.load(outfile)
    else:
        existing_data = []

    # For each company in the existing data, check if the company's location is N/A, 
    # if so, search for the company's location on the website
    for company in existing_data:
        if company['location'] == 'N/A':
            specific_company_response = requests.get(company['link'], timeout=100)
            specific_company_content = specific_company_response.text
            location_targets = re.findall(r'<li class="font-thin odd:bg-gray-200 p-2 sm:px-8 sm:py-5 text-gray-500 text-sm sm:text-md cursor-pointer">(.+?)</li>', specific_company_content)
            need_update_count += 1
            if location_targets:
                company['location'] = location_targets[0]
                company['multiLocation'] = len(location_targets) != 1
                print(f"Updated location for {company['name']}")
                updated_count += 1
    # Write the updated list of dictionaries to a JSON file
    print(f"Total companies updated: {updated_count}, of {need_update_count} that needed an update, of {len(existing_data)} total companies")
    with open(file_path, "w", encoding="utf-8") as outfile:
        json.dump(existing_data, outfile, indent=4)
    return (need_update_count - updated_count)

def recursive_update(min_acceptable_blanks):
    """
    Perform recursive updates until the number of companies that needed an update is less than or equal to the minimum acceptable blanks.

    Args:
        min_acceptable_blanks (int): The minimum number of companies that can have N/A location.

    """
    while exclusive_update() > min_acceptable_blanks:
        print(exclusive_update())
    convert_json_to_csv_with_mapping('csvSearchOutput.json', 'finalOutput.csv')

def main(genre, start_page, end_page, min_acceptable_blanks, clear_output):
    """
    Perform the main process of scraping data from iSeekPlant website.

    Args:
        genre (str): The genre to search.
        start_page (int): The starting page number.
        end_page (int): The ending page number.
        min_acceptable_blanks (int): The minimum number of companies that can have N/A location.

    """
    doc_link = f"https://www.iseekplant.com.au/{genre}/qld/sunshine-coast?page="
    page_search_doc_link = f"https://www.iseekplant.com.au/{genre}/qld/sunshine-coast"
    if clear_output:
        clear_genra_search_output()
    if end_page == 0:
        total_pages = int(get_iseek_genra_search_page_numbers(page_search_doc_link))
        multi_page_iseek_search_n_update(doc_link, start_page, total_pages, genre)
    if not end_page == 0:
        multi_page_iseek_search_n_update(doc_link, start_page, end_page, genre)
    recursive_update(min_acceptable_blanks)

if __name__ == "__main__":
    genre_arg = sys.argv[1]
    start_page_arg = int(sys.argv[2])
    end_page_arg = int(sys.argv[3])
    min_acceptable_blanks_arg = int(sys.argv[4])
    clear_output_arg = sys.argv[5].lower() == 'true'
    main(genre_arg, start_page_arg, end_page_arg, min_acceptable_blanks_arg, clear_output_arg)
