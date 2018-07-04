from selenium import webdriver
from scrapy.spiders import Spider
from campusfrance import CampusfranceItem
from scrapy import Request
from tqdm import tqdm
from selenium.webdriver.support.ui import Select
from scrapy.settings.default_settings import LOG_FORMAT


class CandidatureSpider(Spider):
    name = 'candidature'

    def __init__(self, *args, **kwargs):
        self.driver = webdriver.Firefox()
        self.combinaisons = []
        self.last_position = 0
        self.items = []
        self.url = 'http://chercheurs.campusfrance.org/CandidatureAnonyme/recherche-externe'

    def start_requests(self):
        yield Request('http://chercheurs.campusfrance.org/CandidatureAnonyme/recherche-externe', self.parse)

    def parse_page_error(self, p):
        vide = "produit aucun".decode('utf8') \
                in self.driver.page_source
        if vide:
            self.log('Page vide')
            self.reinitialize_driver()
        else:
            self.log('Page non vide pour combinaison: %s' % p)

    def parse_select(self, elements):
        return [v.get_attribute('value') for v in elements[1:]]

    def construct_permutations(self, **kwargs):
        for i in kwargs['programme']:
            for j in kwargs['domaine']:
                for y in kwargs['annee_init']:
                    for z in kwargs['annee_cours']:
                        self.combinaisons.append(
                            {
                                'programme': i,
                                'domaine': j,
                                'annee_init': y,
                                'annee_cours': z
                            }
                        )
        self.log('Taille totale des permutations : %s' %
                 len(self.combinaisons))

    def configure_select_recherche(self, selections):
        pass

    def parse(self, response):
        items = []
        self.driver.get(response.url)
        self.log('Starting to fill form')
        self.session_id = response.headers.getlist('Set-Cookie')[0]\
            .split(';')[0].split('=')[1]
        self.log('Cookies Session ID :%s' % self.session_id)
        self.log('Cookie selenium %s' % self.driver.get_cookies())

        programme = self.driver.find_element_by_xpath("//select[@id='id5']")
        domaine = self.driver.find_element_by_xpath("//select[@id='idf']")
        annee_init = self.driver.find_element_by_xpath("//select[@id='id8']")
        annee_cours = self.driver.find_element_by_xpath("//select[@id='idb']")

        pprogramme = programme.find_elements_by_tag_name("option")
        pdomaine = domaine.find_elements_by_tag_name("option")
        pannee_init = annee_init.find_elements_by_tag_name("option")
        pannee_cours = annee_cours.find_elements_by_tag_name("option")

        self.log('Constructing permutations')
        self.construct_permutations(
            programme=self.parse_select(pprogramme),
            domaine=self.parse_select(pdomaine),
            annee_init=self.parse_select(pannee_init),
            annee_cours=self.parse_select(pannee_cours)
        )

        for i, p in enumerate(self.combinaisons):
            programme = self.driver.find_element_by_xpath(
                "//select[@id='id5']")
            domaine = self.driver.find_element_by_xpath(
                "//select[@id='idf']")
            annee_init = self.driver.find_element_by_xpath(
                "//select[@id='id8']")
            annee_cours = self.driver.find_element_by_xpath(
                "//select[@id='idb']")

            select1 = Select(programme)
            select1.select_by_value(p['programme'])
            select2 = Select(domaine)
            select2.select_by_value(p['domaine'])
            select3 = Select(annee_init)
            select3.select_by_value(p['annee_init'])
            select4 = Select(annee_cours)
            select4.select_by_value(p['annee_cours'])
            recherche = self.driver \
                .find_element_by_class_name("imageBoutonList")
            self.last_position = i
            recherche.click()
            self.parse_page_error(p)

        return

    def reinitialize_driver(self):
        self.log('Closing current driver')
        self.log('Reinitializing driver')
        self.driver.back()
        self.log('Cookie selenium %s' % self.driver.get_cookies())

    def spider_opened(self, spider):
        self.pbar = tqdm()  # initialize progress bar
        self.pbar.clear()
        self.pbar.write('Opening {} spider'.format(spider.name))

    def spider_closed(self, spider):
        self.driver.close()
        self.pbar.clear()
        self.pbar.write('Closing {} spider'.format(spider.name))
        self.pbar.close()  # close progress bar
