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

from collections import OrderedDict
from pathlib import Path
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QApplication, QDialog, QGroupBox,
                             QVBoxLayout, QMainWindow, QListWidget,
                             QHBoxLayout)
from scrapy.crawler import CrawlerProcess


class SpiderManager:
    def __init__(self):
        self.run_spider()
        self.crossword_data = self.read_json()

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
        return data

    @staticmethod
    def run_spider():
        """Run Spider if Mon/Wed/Fri or if no links saved"""

        # TODO - Add check so that spider doesn't run everytime
        # crossword_day = datetime.date.today().weekday() in [0, 2, 4]
        # data_exists = Path(".data/json").is_file()
        # if crossword_day or not data_exists:
        process = CrawlerProcess()
        process.crawl(NewYorkerSpider)
        process.start()


class NewYorkerSpider(scrapy.Spider):
    name = "new_yorker_crossword"

    def start_requests(self):
        urls = [
            'https://www.newyorker.com/puzzles-and-games-dept/crossword',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        data = SpiderManager.read_json()
        for crossword_link in response.css("li.River__riverItem___3huWr"):
            extension = crossword_link.css("a::attr(href)").get()
            name = crossword_link.css("h4::text").get()

            # TODO - Add regex to remove "The Crossword" preamble from name
            # test = re.match(r"(.+\:\s)?(.*)")
            # print(test)
            # res = test.group(1)
            # print(name)
            # test = name.split(":")
            # test[1]
            # test = test[1]
            author = crossword_link.css("p a::text").get()
            if name in data:
                break
            data[name] = extension
        SpiderManager.write_json(data)

    # TODO - Add secondary parse to get get embedded crossword link


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
        self.change_site("https://www.newyorker.com" + self.button_links[item.text()])

    def create_left_group_box(self):
        self.left_group_box = QGroupBox("Crossword list")
        self.left_group_box.setMaximumWidth(400)

        self.crossword_list = QListWidget()
        self.crossword_list.addItems(self.button_links)
        self.crossword_list.clicked.connect(self.clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.crossword_list)
        layout.setContentsMargins(10, 10, 10, 10)
        self.left_group_box.setLayout(layout)

    def create_embedded_browser(self):
        _embedded_browser = QWebEngineView()
        _embedded_browser.setUrl(QUrl("http://google.com"))
        return _embedded_browser

    def create_right_group_box(self):
        self.right_group_box = QGroupBox("Browser")

        layout = QVBoxLayout()
        layout.addWidget(self.embedded_browser)
        self.right_group_box.setLayout(layout)


if __name__ == '__main__':
    # SpiderManager()
    window()
