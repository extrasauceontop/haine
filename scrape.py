import csv
from lxml import etree

from sgselenium.sgselenium import webdriver


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    items = []
    scraped_items = []

    DOMAIN = "haineandsmith.co.uk"
    start_url = "https://www.haineandsmith.co.uk/practice-finder"

    all_locations = []
    options = webdriver.chrome.options.Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    with webdriver.Chrome(chrome_options=options) as driver:
        params = {"latitude": 50.1109, "longitude": 8.6821, "accuracy": 100}
        driver.execute_cdp_cmd("Page.setGeolocationOverride", params)

        driver.get(start_url)
        dom = etree.HTML(driver.page_source)
        all_locations += dom.xpath("//div[@data-lat]")

        next_page = driver.find_element_by_xpath('//a[contains(text(), "Next")]')
        while next_page:
            try:
                next_page.click()
                dom = etree.HTML(driver.page_source)
                all_locations += dom.xpath("//div[@data-lat]")
                next_page = driver.find_element_by_id("store_locator_next")
            except:
                next_page = None

    for poi_html in all_locations:
        location_name = poi_html.xpath(".//b/text()")[0]
        store_url = "https://www.haineandsmith.co.uk/practice-finder/{}".format(
            location_name.lower().replace(",", "").replace(" ", "-")
        )
        with webdriver.Chrome(chrome_options=options) as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)

        raw_address = loc_dom.xpath(
            '//article[@class="uk-article"]/div/div[h1]/p/text()'
        )[0].split(", ")
        street_address = raw_address[0].strip()
        city = raw_address[1].strip()
        state = raw_address[2].strip()
        zip_code = raw_address[3].strip()
        country_code = "GB"
        store_number = poi_html.xpath("@data-id")[0]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi_html.xpath("@data-lat")[0]
        longitude = poi_html.xpath("@data-lng")[0]
        hoo = loc_dom.xpath(
            '//h3[contains(text(), "Opening Hours")]/following-sibling::table//td/text()'
        )
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = [
            DOMAIN,
            store_url,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
