import pprint, re, jsonpickle
from datetime import datetime

class EntityData:

    entityIdRegEx = re.compile(r'[^\d]+(\d+)[^\d]+')

    def __init__(self, entity_type=None, entity_link=None, entity_name=None, entity_parent_link=None, entity_parent_name=None):
        self.created_time = datetime.now()
        self.last_mod_time = self.created_time
        self.entity_type = entity_type
        self.entity_link = entity_link
        self.entity_id = self.extract_entity_id(entity_link)
        self.entity_name = entity_name
        if entity_type == "brand":
            self.entity_parent_link = entity_parent_link
            self.entity_parent_name= entity_parent_name
            self.parent_id = self.extract_entity_id(entity_parent_link)
        self.website = None
        self.twitter_url = None
        self.twitter_entity_url = None
        self.twitter_entity_url_title = None
        self.children = None
        self.parent = None
        self.contact_info = None

    def __str__(self):
        return jsonpickle.encode(self,unpicklable=False)

    @classmethod
    def extract_entity_id(cls, entity_url):
        if entity_url:
            match = cls.entityIdRegEx.search(entity_url)
            if match:
                return match.group(1)
            else:
                entity_url

    def to_dict(self):
        return jsonpickle.loads(str(self))


class ContactInfo:
    contactDetailPhoneRegEx = re.compile(r'Phone\s*:\s*([^s]+)')
    contactDetailFaxRegEx = re.compile(r'Fax\s*:\s*([^s]+)')

    def __init__(self, raw_contact_info):
        contact_info_array = re.split(r'</?br/?>', raw_contact_info, flags=re.IGNORECASE)
        self.address = ''
        for index, line in enumerate(contact_info_array):
            if line:
                if index == 0:
                    self.name = line
                elif "phone" in line.lower():
                    self.phone = self.extract_phone(line)
                elif "fax" in line.lower():
                    self.fax = self.extract_fax(line)
                else:
                    self.address += ' '+line


    @classmethod
    def extract_phone(cls, phone_text):
        match = cls.contactDetailPhoneRegEx.search(phone_text)
        if match:
            return match.group(1)

    @classmethod
    def extract_fax(cls, fax_text):
        match = cls.contactDetailFaxRegEx.search(fax_text)
        if match:
            return match.group(1)

    def __str__(self):
        return pprint.pformat(vars(self))
