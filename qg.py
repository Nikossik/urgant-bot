from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import requests

from question_generation.pipelines import pipeline

import transformers
from deep_translator import GoogleTranslator

class QgTrans:
    def __init__(self, translator_ru_to_en, translator_en_to_ru, nlp):
        self.translator_ru_to_en = translator_ru_to_en
        self.translator_en_to_ru = translator_en_to_ru
        self.nlp = nlp


    def preprocessing(self, corpus):
        for i in range(len(corpus)):
            corpus[i] = corpus[i].replace('\xa0', ' ')


    def parse_text_ria(self, name):
        link = 'https://ria.ru/search/?query='

        for word in name.split():
            link += f'{word}+'
        link = link[:-1]

        
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(url=link)
        sleep(2.5)
        html = driver.page_source
        driver.close()
        soup = BeautifulSoup(html, "html.parser")
        a = soup.findAll("a", {"class" : "list-item__title"})

        els = []
        for link in a:
            for word in name.lower().split():
                if word in link.text.lower():
                    els.append((link.text, link['href']))
                    break

        res = []

        for el in els:
            
            url = el[1]

            main_text = ""
            soup = BeautifulSoup(requests.get(url).content, "html.parser")
            texts = soup.findAll("div", {"class" : "article__text"})
            for text in texts:
                main_text += text.text

            res.append(main_text)

        return res

    def parse_text_cosmo(self, name):
        url = "https://www.cosmo.ru/search/?query="

        for word in name.split():
            url += f'{word}%20'
        url = url[:-3]

        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(url=url)
        sleep(2.5)
        html = driver.page_source
        driver.close()

        soup = BeautifulSoup(html, "html.parser")
        a = soup.findAll("a", {"class" : "search-article search__article"})

        els = []
        for link in a:
            for word in name.lower().split():
                if word in link.text.lower():
                    els.append((link.text, link['href']))
                    break

        res = []
        for el in els:
            url = f"https://www.cosmo.ru{el[1]}"
            main_text = ""
            soup = BeautifulSoup(requests.get(url).content, "html.parser")
            texts = soup.findAll("p", {"class" : "article-element"})
            for text in texts:
                main_text += text.text
            
            res.append(main_text)

        return res

    def parse_text_mh(self, name):
        url = "https://www.mhealth.ru/search/?query="

        for word in name.split():
            url += f'{word}%20'
        url = url[:-3]

        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(url=url)
        sleep(2.5)
        html = driver.page_source
        driver.close()

        soup = BeautifulSoup(html, "html.parser")
        a = soup.findAll("a", {"class" : "search-article search__article"})

        els = []
        for link in a:
            for word in name.lower().split():
                if word in link.text.lower():
                    els.append((link.text, link['href']))
                    break

        res = []
        for el in els:
            url = f"https://www.mhealth.ru{el[1]}"
            main_text = ""
            soup = BeautifulSoup(requests.get(url).content, "html.parser")
            texts = soup.findAll("p", {"class" : "article-element"})
            for text in texts:
                main_text += text.text
            
            res.append(main_text)

        return res


    def parse(self, name, lim=5000):
        ria = self.parse_text_ria(name)
        cosmo = self.parse_text_cosmo(name)
        mh = self.parse_text_mh(name)
        
        parsed = ria + cosmo + mh

        for i in range(len(parsed)):
            parsed[i] = parsed[i][:lim]

        return parsed 


    def translate_ru_to_en(self, corpus):
        translated = []
        for sentence in corpus:
            translated.append(self.translator_ru_to_en.translate(text=sentence))
        return translated


    def qg_en_to_en(self, corpus):
        qg = []
        for i in corpus:
            qg.append(self.nlp(i))
        return qg


    def translate_en_to_ru(self, corpus):
        translated = []
        for t in corpus:
            for sentence in t:
                translated.append(self.translator_en_to_ru.translate(text=sentence))
        return translated


    def predict(self, name):
        corpus = self.parse(name, lim=1000)
        self.preprocessing(corpus)
        print(corpus)
        ru_to_en = self.translate_ru_to_en(corpus)
        qg = self.qg_en_to_en(ru_to_en)
        en_to_ru = self.translate_en_to_ru(qg)
        return en_to_ru