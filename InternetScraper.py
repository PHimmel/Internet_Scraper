"""
Application overview:

    a general-purpose tool designed for extracting data from websites with ease and simplicity
I/O:
    input:
    the url of the target site
    or alternatively - running a module that is compatible with the included interface

    prebuilt modules that are built on top of this program include: todo expand, Indeed, Monster, News, etc.

Program structure:
    the implementation layer comprises this program currently - its interface is todo currently JobScraper...

    the primary functionality of the program is contained in three related classes:

        1. RawHtml(base_class) - takes a single working URL as a parameter - creates an http session with it
            - gets and returns the full page html data

        2. ParseHtml(RawHtml) (contains 'filters' as an additional argument) - receives the html page in its
            entirety from its parent class - converts it into a BeautifulSoup object(that has been further
            distilled by the 'filters' parameter if one is entered)

        3. ExtractData(ParseHtml) - takes the BeautifulSoup instance attribute generated from its parent class
            and can perform two types of data extraction

            1. get the links that are found on the page itself by the following:

                a. locate the 'a' element identifiers present in the BeautifulSoup object
                b. extract the link data associated with the 'href' identifier from step a.

            2. extract the natural language text that said page contains by using the simple
                BeautifulSoup function of '.text'
Program flow:

How to use:

"""


from bs4 import BeautifulSoup, SoupStrainer
import urllib
from urllib import request
from urllib import error
from NLP import TextAnalysis as TA
import re


class RawHtml(object):

    def __init__(self, url, link_filters=None, text_filters=None):
        self.url = url
        self.link_filters = link_filters
        self.text_filters = text_filters

        self.filters = None

        self.set_filters()

        self.raw_html = self.http_session()

    def __repr__(self):
        return 'RawHtml(link = {}, filters = {}, \n subclasses = {})'.format(self.url, self.filters,
                                                                             RawHtml.__subclasses__())

    def set_filters(self):
        if self.link_filters is None:
            self.filters = self.text_filters
        else:
            self.filters = self.link_filters
        return self.filters

    def http_session(self):
        try:
            return urllib.request.urlopen(self.url).read()
        except urllib.error.URLError:
            print('URLError: bad link!')


class ParseHtml(RawHtml):

    def __init__(self, url, link_filters=None, text_filters=None):
        super().__init__(url, link_filters, text_filters)
        self.link_filters = link_filters
        self.text_filters = text_filters
        self.soup = self.make_link_soup()

    def __repr__(self):
        return 'ParseHtml(link = {}, filters = {}, BeautifulSoup attribute = {})'.format(self.url, self.filters,
                                                                                         bool(self.soup))

    def make_link_soup(self):
        # todo must be further abstracted
       ## if self.filters is not None:
         ##   self.filters = SoupStrainer(self.filters)

        # if no data has been generate, a precaution in the event of a bad link
        if self.raw_html is None:
            return
        else:
            return BeautifulSoup(self.raw_html, 'html.parser', parse_only=self.filters)


class ExtractData(ParseHtml):

    extracted_text = []

    def __init__(self, url, link_filters=None, text_filters=None): # removed =None on both inits here
        super().__init__(url, link_filters, text_filters)
        self.link_filters = link_filters
        self.text_filters = text_filters

    def __repr__(self):
        return 'ExtractData(link = {}, filters = {}), attribute of BeautifulSoup = {}'.format(self.url, self.filters,
                                                                                              bool(self.soup))

    def none_type_check(self):
        if self.soup is None:
            print('No soup at', self)
            return False
        else:
            return True

    def get_links(self):
        soup_is_here = self.none_type_check()
        if soup_is_here is False:
            print('No soup at', self)
            return
        links = []

        for link in self.soup('a'):
            links.append(link.get('href'))
        return links

    def get_text(self):
        # if no data has been generate, a precaution in the event of a bad link
        if self.soup is None:
            return
        return self.soup.text

    def appended_text_to_class_attribute(self):
        ExtractData.extracted_text.append(self.soup.text)


"""
todo MUST BE REFACTORED, SIMPLIFIED, REWRITTEN, ETC.
OVERLY COMPLICATED, UNREADABLE, ETC.
"""


class CheckLinkQuality(object):

    def __init__(self, link_list, link_stem, link_keywords=None):
        self.link_list = link_list
        self.link_list = self.filter_none_types_from_link_list()

        self.link_stem = link_stem
        self.link_keywords = link_keywords

        self.missing_stems = []

    def filter_none_types_from_link_list(self):
        self.link_list = [link for link in self.link_list if link is not None]
        # previous statement --> list(filter(None, self.link_list))
        return self.link_list

    def check_link_stem(self):
        holder = []
        for link in self.link_list:

            if link.startswith(self.link_stem):
                holder.append(link)
            else:
                self.missing_stems.append(link)

        holder += self.add_link_stem()
        self.link_list = holder
        return self.filter_none_types_from_link_list()

    def add_link_stem(self):
        holder = []
        for link in self.missing_stems:

            stemmed_link = self.link_stem + link
            holder.append(stemmed_link)
        # why does it fail with self.link_list return?
        return holder

    def check_links_for_keywords(self):
        holder = []
        for link in self.link_list:

            if re.search(r'{}'.format(self.link_keywords), link):
                holder.append(link)

        self.link_list = holder
        return self.link_list

    def number_of_links_corrected(self):
        pass


def type_check(data):
    if type(data) is None:
        return False


class ScraperInterface(object):

    def __init__(self, url, html_link_filters=None, html_text_filters=None, link_stem=None, link_keywords=None):
        self.url = url
        self.link_filters = html_link_filters
        self.text_filters = html_text_filters
        self.link_stem = link_stem
        self.link_keywords = link_keywords

        self.extract_links = None
        self.check_link_quality = None
        self.extract_text = None

    def links_from_page(self):
        self.extract_links = ExtractData(self.url, self.link_filters)
        return self.extract_links.get_links()

    def filter_and_stem_links(self):
        self.check_link_quality = CheckLinkQuality(self.links_from_page(), link_stem=self.link_stem,
                                                   link_keywords=self.link_keywords)
        if self.link_keywords is not None:
            return self.check_link_quality.check_links_for_keywords()

        # check_link_stem() returns to a method that concatenates the missing and returns the final list
        return self.check_link_quality.check_link_stem()

    def iterate_links_and_print_their_text(self):
        for link in self.filter_and_stem_links():
            self.url = link
            print(self.text_from_page())

    def iterate_links_and_save_their_text(self, file):
        for link in self.filter_and_stem_links():
            self.url = link
            TA.EnterTextIntoFile(file, self.text_from_page()).enter_data()

    def text_from_page(self):
        self.extract_text = ExtractData(self.url, self.text_filters)
        return self.extract_text.get_text()


"""
must remove control characters, white space, etc.
"""


class CheckTextQuality(object):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return 'CheckTextQuality({})'.format(type(self.text))

    def __str__(self):
        return 'An object that consists of text extracted from job descriptions.'
    """
    NEEDS WORK!
    """

    @property
    def sentences(self):
        return TA.TextInterface(self.text).sentence_analysis.make_sentences()

    def filter_out_control_characters(self):
        print(self.text)
        for char in ''.join(self.text):
            print(char)
            filtered_text = re.sub(r'^\W+', 'TEST', char)
        print(filtered_text)
        _text = re.sub(r'^\S\s*', 'TWO', filtered_text)
        print(_text)


class ErrorMitigation(object):

    def type_error(self):
        pass


#test = ExtractData('https://www.indeed.com/jobs?q=software+engineer&start=0') #, link_filters=SoupStrainer('a', target='_blank', title=True))

#link_list_indeed = test.get_links()

#check = CheckLinkQuality(link_list_indeed, link_stem='https://www.indeed.com', link_keywords='/jobs?')
#check.check_links_for_keywords()
#print(check.check_link_stem())


class Indeed:
    html_page_link_filers = SoupStrainer('a', target='_blank', title=True)
    html_job_description_text_filters = SoupStrainer('div', id='jobDescriptionText')
    indeed_start_link = 'https://www.indeed.com/jobs?q=software+engineer&start=0'
    indeed_url_stem = 'https://www.indeed.com'
    # indeed_url_keywords = '/jobs?q=software+engineer&taxo'
    indeed_txt_file = 'indeed_posts.txt'

    def __init__(self):
        self.scraper_interface = ScraperInterface(url=Indeed.indeed_start_link,
                                                  html_link_filters=Indeed.html_page_link_filers,
                                                  html_text_filters=Indeed.html_job_description_text_filters,
                                                  link_stem=Indeed.indeed_url_stem,
                                                  link_keywords=None)

    def __repr__(self):
        return 'Indeed({})'.format(self.scraper_interface)

    def get_full_links(self):
        return self.scraper_interface.filter_and_stem_links()

    def print_job_descriptions(self):
        return self.scraper_interface.iterate_links_and_print_their_text()


start = Indeed()
print(start.get_full_links())

main_links = SoupStrainer('a', target='_blank', title=True)
main_info = SoupStrainer('div', id='jobDescriptionText')
indeed_main_link = 'https://www.indeed.com/jobs?q=software+engineer&start=0'
indeed_stem = 'https://www.indeed.com'
indeed_url_keywords = '/jobs?q=software+engineer&taxo'
indeed_file = 'indeed_posts.txt'


def indeed_interface_layer_test():
    indeed = ScraperInterface(indeed_main_link, main_links, main_info, indeed_stem)
    print(help(indeed))
    indeed.iterate_links_and_save_their_text(indeed_file)


def indeed_implementation_layer_test():
    test_indeed = ExtractData(indeed_main_link, link_filters=main_links)

    raw_links = test_indeed.get_links()
    print(raw_links)
    link = CheckLinkQuality(raw_links, link_stem=indeed_stem)
    print(link.check_link_stem())

    for li in link.check_link_stem():
        final_one = ExtractData(li, text_filters=main_info).get_text()
        TA.EnterTextIntoFile('indeed_posts.txt', final_one).enter_data()
        print('entered')

