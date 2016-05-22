#!/usr/bin/env python3

import time, logging, jsonpickle
from contextlib import contextmanager
import persistence
from requesthandler import get_url_soup
import extractors, settings
from domain import EntityData


def main():


    brands = {}
    organizations = {}

    def update_progress():
        brands[brand_data.entity_id] = brand_data
        organizations[org_data.entity_id] = org_data

    soup = get_url_soup(settings.baseUrl + '/index.html')
    if not soup:
        logging.error("Index page unavailable")
        exit()

    brands_link = soup.find_all('a', href=True, text='Brands')[0]['href']

    def has_more_pages():
        return True

    while True:
        count = 0
        soup = get_url_soup(settings.baseUrl + brands_link)
        current_page_link = soup.find('a', {"class": "currentPage"})

        articles = soup.find_all('article')
        for article in articles:
            if article.find('h2'):

                brand_data = extractors.get_brand_data(article)
                org_data = extractors.initialize__organization(article)
                update_progress()
                count +=1

        print("Page %s finished. %d brands processed"%(current_page_link.text.replace('\n', ''),count))

        if current_page_link.find_next_sibling('a'):
            brands_link = current_page_link.next_sibling['href']

        else:
            break

    extractors.fill_in_organization_details(list(organizations.values()))
    extractors.add_organization_details__to_brand(brands=list(brands.values()),organizations=organizations)

    # Store in mongodb
    persistence.mongodb_persist(organizations=list(organizations.values()),brands=list(brands.values()))


def fixing_entities():

    faulty_orgs = list(persistence.find_entities(entity_type='organization',status='error'))
    print("There are %d faulty organizations"%len(faulty_orgs))
    fixed_orgs = []

    for db_org in faulty_orgs:
        db_org.pop("_id", None)
        db_org.pop("last_mod_time", None)
        entity = EntityData()
        entity.__dict__ = db_org
        fixed_orgs.append(entity)

    extractors.fill_in_organization_details(fixed_orgs)
    persistence.store_entities(entities=fixed_orgs)

    db_orgs = list(persistence.find_entities(entity_type='organization'))
    faulty_brands = list(persistence.find_entities(entity_type='brand', status='error'))
    print("There are %d faulty brands" % len(faulty_brands))
    fixed_brands = []
    for db_brand in faulty_brands:
        db_brand.pop("_id", None)
        db_brand.pop("last_mod_time", None)
        entity = EntityData()
        entity.__dict__ = db_brand
        extractors.fill_in_entity_details(entity)
        fixed_brands.append(entity)

    extractors.add_organization_details__to_brand(brands=fixed_brands, organizations=db_orgs)
    persistence.store_entities(entities=fixed_brands)

@contextmanager
def timeit_context(name):
    start_time = time.time()
    print("Crawler started at %s"%time.strftime("%H:%M:%S"))
    yield
    end_time =time.time()
    print("Crawler ended at %s" % time.strftime("%H:%M:%S"))
    elapsed_time = end_time- start_time
    print('[{}] finished in {} seconds'.format(name, int(elapsed_time)))


if __name__ == "__main__":

    logging.basicConfig(level=logging.WARNING, format=' %(asctime)s -  %(levelname)s-  %(message)s')

    jsonpickle.set_preferred_backend('json')
    jsonpickle.set_encoder_options('json', indent=2)

    repair= settings.init()

    with timeit_context('crawler'):
        if repair:
            fixing_entities()
        else:
            main()

    settings.destroy()



