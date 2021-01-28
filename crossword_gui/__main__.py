#! python3

"""
new_yorker_crossword_getter.py - GUI to pull all New Yorker Crosswords

browser template from:
https://www.geeksforgeeks.org/creating-a-simple-browser-using-pyqt5/
spider developed using Scrapy docs
https://docs.scrapy.org/en/latest/intro/tutorial.html#following-links

"""

import datetime
import json
import re
import scrapy
import sys
import unittest

from collections import OrderedDict
from operator import itemgetter
from pathlib import Path
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QApplication, QDialog, QGroupBox,
                             QVBoxLayout, QMainWindow, QListWidget,
                             QHBoxLayout)
from scrapy.crawler import CrawlerProcess
from scrapy.exporters import JsonLinesItemExporter


class SpiderManager:
    def __init__(self):
        self.run_spider()
        self.update_json()
        self.crossword_data = self.read_json()
        self.last_updated = self.crossword_data.pop("last_updated")

    @staticmethod
    def write_json(data, filename="data.json"):
        """Write data to JSON file"""
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def read_json(filename="data.json"):
        """Get data from JSON file"""
        try:
            with open(filename) as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            data = OrderedDict()
        except ValueError:
            data = []
        return data

    @staticmethod
    def update_json(spider_file="crossword_spider.json", data_file="data.json"):
        spider_data = SpiderManager.read_json(spider_file)
        sorted_spider = sorted(spider_data, key=itemgetter("date"))
        crossword_data = OrderedDict(SpiderManager.read_json(data_file))

        for crossword in sorted_spider:
            crossword_data.update({crossword["name"]: crossword["url"]})
            crossword_data.move_to_end(crossword['name'], last=False)
        if sorted_spider:
            crossword_data.update({"last_updated": sorted_spider[0]["date"]})
        else:
            crossword_data["last_updated"] = None

        SpiderManager.write_json(crossword_data)
        try:
            Path.cwd()/Path(spider_file).unlink()
        except (FileNotFoundError, TypeError) as e:
            pass

    def run_spider(self):
        """Run Spider if Mon/Wed/Fri or if no links saved"""

        # TODO - Add check so that spider doesn't run everytime
        # last_update = self.last_updated
        """ run if - 
        - no data.json
        - if mon/wed/fri & last_update != today
        

        # if not last_update or

        # crossword_day = datetime.date.today().weekday() in [0, 2, 4]
        # data_exists = Path(".data/json").is_file()
        # if crossword_day or not data_exists:
        """
        process = CrawlerProcess({"FEED_FORMAT": "json",
                                  "FEED_URI": "crossword_spider.json",
                                  })
        process.crawl(NewYorkerSpider)
        process.start()


class NewYorkerSpider(scrapy.Spider):
    name = "new_yorker_crossword"
    temp_data = {}

    def start_requests(self):
        urls = [
            'https://www.newyorker.com/puzzles-and-games-dept/crossword',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        previously_scraped = SpiderManager.read_json()

        crossword_links = response.css("li.River__riverItem___3huWr")
        for crossword_link in crossword_links:
            url = crossword_link.css("a::attr(href)").get()
            full_name = crossword_link.css("h4::text").get()
            # Pull the crossword publish date for later sorting
            try:
                url_date = re.search("\d{4}/\d{2}/\d{2}", url).group()
                short_name = re.match(r".+\:\s?(.*)", full_name).group(1)
            except AttributeError:
                continue

            # Remove "The Crossword: " preamble on name

            author = crossword_link.css("p a::text").get()
            name_author = f"{short_name} - {author}"
            if name_author in previously_scraped:
                break

            yield response.follow(url, self.parse_crossword,
                                  cb_kwargs=dict(name=name_author,
                                                 date=url_date))

    def parse_crossword(self, response, name, date):
        url = response.css("div.crossword-embed iframe::attr(data-src)").get()
        short_url = re.match("(.+weekly)", url).group(1)
        yield{
            "name": name,
            "date": date,
            "url": short_url
        }


def window():
    app = QApplication([])
    win = WidgetGallery()
    win.showMaximized()
    sys.exit(app.exec_())


class WidgetGallery(QDialog):

    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)
        self.embedded_browser = self.create_embedded_browser()
        self.button_links = SpiderManager().crossword_data

        self.create_left_group_box()
        self.create_right_group_box()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.left_group_box)
        main_layout.addWidget(self.right_group_box)
        self.setLayout(main_layout)

    def change_site(self, url):
        self.embedded_browser.setUrl(QUrl(url))

    def clicked(self):
        item = self.crossword_list.currentItem()
        # self.change_site("https://www.newyorker.com" + self.button_links[item.text()])
        self.change_site(self.button_links[item.text()])

    def create_left_group_box(self):
        self.left_group_box = QGroupBox("Crossword list")
        self.left_group_box.setMaximumWidth(400)

        self.crossword_list = QListWidget()
        self.crossword_list.addItems(self.button_links)
        self.crossword_list.clicked.connect(self.clicked)
        # self.crossword_list.setCurrentIndex()

        layout = QVBoxLayout()
        layout.addWidget(self.crossword_list)
        layout.setContentsMargins(10, 10, 10, 10)
        self.left_group_box.setLayout(layout)

    def create_embedded_browser(self):
        _embedded_browser = QWebEngineView()
        _embedded_browser.setUrl(QUrl("http://google.com"))
        # direct_site = "https://cdn3.amuselabs.com/tny/crossword?id=c36233cb&set=tny-weekly&embed=1&compact=1&maxCols=2&src=http%3A%2F%2Fwww.newyorker.com%2Fpuzzles-and-games-dept%2Fcrossword%2F2021%2F01%2F08"
        # _embedded_browser.setUrl(QUrl(direct_site))
        return _embedded_browser

    def create_right_group_box(self):
        self.right_group_box = QGroupBox("Browser")

        layout = QVBoxLayout()
        layout.addWidget(self.embedded_browser)
        self.right_group_box.setLayout(layout)


if __name__ == '__main__':
    # SpiderManager()
    window()
    # help(QListWidget.setCurrentIndex)
