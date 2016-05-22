from domain import  ContactInfo, EntityData
import re
from requesthandler import get_url_soup,get_contents
import settings, persistence


def fill_in_contact_info(entity, soup):
    website=soup.select('div.sidebar a.website')
    if website:
        raw_contact_info = website[0].find_previous('p')
        if raw_contact_info:
            contact_info = ContactInfo(re.sub('</?p/?>','',str(raw_contact_info)))
            entity.contact_info = contact_info


def fill_in_entity_details(entity_data):

    soup = get_url_soup(settings.baseUrl + entity_data.entity_link)

    if soup:
        entity_data.website = get_url_from_entity_details(soup, "website")
        entity_data.twitter_url = get_url_from_entity_details(soup, "twitter")
        entity_data.status = 'ok'
        #fill_in_twitter_details(entity_data)
        #fill_in_contact_info(entity_data, soup)
    else:
        entity_data.status = 'error'


def fill_in_organization_details(organizations):

    print("Moving on to process %d organizations" % len(organizations) )
    count = 0
    faulty_orgs=0

    for org_data in organizations:

        soup = get_url_soup(settings.baseUrl+org_data.entity_link)
        if soup:
            org_data.status = 'ok'
            fill_in_entity_details(org_data)
            org_data.children = [EntityData.extract_entity_id(image.parent['href'])
                                 for image in soup.select("img.brand")]
            count += 1
            if count%10 == 0:
                print("Processed %d organizations"%count)
        else:
            org_data.status = 'error'
            faulty_orgs += 1

    print("Processed %d organizations. %d of them were faulty" % (len(organizations), faulty_orgs))


def fill_in_twitter_details(entity_data):
    soup = get_url_soup(entity_data.twitter_url)
    if soup:
        twitter_entity_url_selector = 'div.ProfileHeaderCard-url a'
        twitter_entity_url = find_one_with_css_selector(soup, twitter_entity_url_selector, 'href')
        if twitter_entity_url:
            resp= get_contents(twitter_entity_url)
            if resp:
                entity_data.twitter_entity_url = resp.url

        entity_data.twitter_entity_url_title = find_one_with_css_selector(soup, twitter_entity_url_selector, 'title')


def get_url_from_entity_details(soup, detail_name):
    if soup.select('div.sidebar a.%s' % detail_name):
        return soup.select('div.sidebar a.%s' % detail_name)[0]['href'].replace('#!/','')


def find_one_with_css_selector(soup, selector, *attr):
    if soup.select(selector):
        return soup.select(selector)[0].get(attr[0],"") if len(attr)>0 else soup.select(selector)[0]


def add_organization_details__to_brand(*,brands, organizations):
    faulty_brands = 0
    for brand in brands:
        brand.parent = organizations[brand.parent_id]
        if brand.status != 'ok':
            faulty_brands += 1

    print("Processed %d brands. %d of them were faulty" % (len(brands), faulty_brands))


def get_brand_data(article):
    brand_link_selector = 'h2 a'
    brand_link = find_one_with_css_selector(article, brand_link_selector, 'href')
    brand_name = find_one_with_css_selector(article, brand_link_selector).text

    organization_link_selector = 'h3 a'
    organization_link = find_one_with_css_selector(article, organization_link_selector, 'href')
    organization_name = find_one_with_css_selector(article, organization_link_selector).text

    brand_data = EntityData("brand", brand_link, brand_name, organization_link, organization_name)
    fill_in_entity_details(brand_data)

    return brand_data


def initialize__organization(article):

    organization_link_selector = 'h3 a'
    organization_link = find_one_with_css_selector(article, organization_link_selector, 'href')
    organization_name = find_one_with_css_selector(article, organization_link_selector).text

    return EntityData("organization", organization_link, organization_name)


