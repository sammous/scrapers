from selenium import webdriver
from scrapy.spiders import Spider
from campusfrance import CampusfranceItem
from scrapy import Request
from tqdm import tqdm
from selenium.webdriver.support.ui import Select
from scrapy.settings.default_settings import LOG_FORMAT
import time


class CandidatureSpider(Spider):
    name = 'candidature'

    def __init__(self, *args, **kwargs):
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference('browser.download.folderList', 2) # custom location
        self.profile.set_preference('browser.download.manager.showWhenStarting', False)
        self.profile.set_preference('browser.download.dir', '/home/sami/Documents/Github/scrapers/scrapy/campusfrance/csv')
        self.profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
        self.driver = webdriver.Firefox(self.profile)

        self.combinaisons = []
        self.last_position = 0
        self.items = []
        self.url = 'http://chercheurs.campusfrance.org/CandidatureAnonyme/recherche-externe'

        self.pbar = tqdm()  # initialize progress bar
        self.pbar.clear()
        self.pbar.write('Opening {} spider'.format(self.name))

    def start_requests(self):
        yield Request('http://chercheurs.campusfrance.org/CandidatureAnonyme/recherche-externe', self.parse)

    def parse_page_error(self, p):
        vide = "produit aucun".decode('utf8') \
                in self.driver.page_source
        non_vide = "ponse(s)".decode('utf8') \
                in self.driver.page_source
        erreur = "Erreur interne".decode('utf8') \
                in self.driver.page_source
        while erreur:
            self.reinitialize_driver()
            self.trigger_select(p)
            erreur = "Erreur interne".decode('utf8') \
                in self.driver.page_source
        if vide:
            self.log('Page vide')
            self.reinitialize_driver()
            return None
        elif non_vide:
            self.log('Page non vide pour combinaison: %s' % p)
            return True
    
    def parse_select(self, elements):
        return [v.get_attribute('value') for v in elements[1:]]

    def parse_list_page(self, combinaison):
        #export_button = self.driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div/div[2]/a/span')
        #export_button.click()
        #self.driver.back()
        list_event = self.driver.find_elements_by_xpath(
            '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div/div[5]/div//a')
        size_elements = len(list_event)
        for i in range(size_elements):
            list_event[i].click()
            item = self.parse_page()
            self.items.append(item)
            yield item
            self.driver.back()
            time.sleep(2)
            list_event = self.driver.find_elements_by_xpath(
                '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div/div[5]/div//a')

    def parse_page(self):
        titre = self.driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div[1]/div[1]/div/div/h3').text
        programme = self.driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div[1]/div[2]/div/div/div[2]/span').text
        domaine = self.driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div[1]/div[4]/div/div/div[2]/span').text

        sigle = self.driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div[3]/div/div/div/div/div[1]/div/div/div[2]/span').text
        nom1 = self.driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div[3]/div/div/div/div/div[2]/div/div/div[2]/span').text
        adresse1 = self.driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div[3]/div/div/div/div/div[3]/div/div/div[2]/span').text
        cp1 = self.driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div[3]/div/div/div/div/div[4]/div/div/div[2]/span').text
        ville1 = self.driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div[3]/div/div/div/div/div[5]/div/div/div[2]/span').text
        institution_rattach1 = self.driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div[3]/div/div/div/div/div[6]/div/div/div[2]/span').text

        nom2 = self.driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div[4]/div/div/div/div/div[1]/div/div/div[2]/span').text
        adresse2 = self.driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div[4]/div/div/div/div/div[2]/div/div/div[2]/span').text
        cp2 = self.driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div[4]/div/div/div/div/div[3]/div/div/div[2]/span').text
        ville2 = self.driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div[4]/div/div/div/div/div[4]/div/div/div[2]/span').text
        pays2 = self.driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div[4]/div/div/div/div/div[5]/div/div/div[2]/span').text
        institution_rattach2 = self.driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div[4]/div/div/div/div/div[6]/div/div/div[2]/span').text

        item = CampusfranceItem(
            titre=titre,
            programme=programme,
            sigle=sigle,
            nom1=nom1,
            adresse1=adresse1,
            ville1=ville1,
            cp1=cp1,
            institution_rattach1=institution_rattach1,
            nom2=nom2,
            adresse2=adresse2,
            cp2=cp2,
            ville2=ville2,
            pays2=pays2,
            institution_rattach2=institution_rattach2
        )

        self.log('-'*100)
        self.log(titre)
        self.log(programme)
        self.log(sigle)
        self.log(adresse1)
        self.log(nom1)
        self.log(cp1)
        self.log(institution_rattach1)
        return item

    def construct_permutations(self, **kwargs):
        for i in kwargs['programme']:
            for j in kwargs['domaine']:
                for y in kwargs['annee_init']:
                    self.combinaisons.append(
                        {
                            'programme': i,
                            'domaine': j,
                            'annee_init': y
                        }
                    )
        self.log('Taille totale des permutations : %s' %
                 len(self.combinaisons))

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

        pprogramme = programme.find_elements_by_tag_name("option")
        pdomaine = domaine.find_elements_by_tag_name("option")
        pannee_init = annee_init.find_elements_by_tag_name("option")

        self.log('Constructing permutations')
        self.construct_permutations(
            programme=self.parse_select(pprogramme),
            domaine=self.parse_select(pdomaine),
            annee_init=self.parse_select(pannee_init)
        )
        self.pbar.total = len(self.combinaisons)
        # debugging
        self.combinaisons = [
            {
                'programme': u"10000351",
                'domaine': u"38",
                'annee_init': u"2010"
            }
        ]
        for i, p in enumerate(self.combinaisons):
            self.trigger_select(p)
            if self.parse_page_error(p):
                for item in self.parse_list_page(p):
                    yield item

            self.pbar.update(1)
        return

    def trigger_select(self, p):
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
        recherche = self.driver \
            .find_element_by_class_name("imageBoutonList")
        
        recherche.click()

    def reinitialize_driver(self):
        self.log('Closing current driver')
        self.log('Reinitializing driver')
        self.driver.delete_all_cookies()
        self.driver.close()
        self.driver = webdriver.Firefox(self.profile)
        self.driver.get(self.url)
        self.log('Cookie selenium %s' % self.driver.get_cookies())

    def spider_closed(self, spider):
        self.driver.close()
        self.pbar.clear()
        self.pbar.write('Closing {} spider'.format(spider.name))
        self.pbar.close()  # close progress bar
