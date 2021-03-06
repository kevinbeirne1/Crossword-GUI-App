#! python3

"""
new_yorker_crossword_getter.py - GUI to pull all New Yorker Crosswords

browser template from:
https://www.geeksforgeeks.org/creating-a-simple-browser-using-pyqt5/
spider developed using Scrapy docs
https://docs.scrapy.org/en/latest/intro/tutorial.html#following-links

"""

import json
import re

import sys
import scrapy
import pyinputplus as pyip
from collections import OrderedDict
from datetime import datetime
from operator import itemgetter
from pathlib import Path
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QApplication, QDialog, QGroupBox, QVBoxLayout,
                             QListWidget, QHBoxLayout)
from scrapy.crawler import CrawlerProcess
from scrapy.item import Item, Field
from scrapy.exceptions import DropItem


class FormatItemPipeline:
    """Format spider item data for readability"""
    def process_item(self, item, spider):
        try:
            item["name"] = re.match(r".+\:\s?(.*)", item["name"]).group(1)
            item["date"] = datetime.strptime(item['date'], "%B %d, %Y")
            item['url'] = re.match("(.+weekly)", item['url']).group(1)
        except:
            DropItem("Link is article, Not crossword")
        return item


class SaveItemPipeline:
    """Append item to list in SpiderManager"""
    def process_item(self, item, spider):
        SpiderManager.spider_data.append(item)


class MyItem(Item):
    name = Field()
    date = Field()
    url = Field()
    author = Field()


class SpiderManager:
    spider_data = []
    def __init__(self):
        self.run_spider()
        self.update_json()
        self.crossword_data = self.read_json()
        self.last_updated = self.crossword_data.pop("last_updated")

    @staticmethod
    def write_json(data, filename="crossword_data.json"):
        """Write data to JSON file"""
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def read_json(filename="crossword_data.json"):
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
    def update_json(data_file="crossword_data.json"):
        """Read spider.json, update data.json, and delete spider.json"""
        sorted_spider = sorted(SpiderManager.spider_data,
                               key=itemgetter("date"))
        crossword_data = OrderedDict(SpiderManager.read_json(data_file))

        for crossword in sorted_spider:
            name = f'{crossword["name"]} - {crossword["author"]}'
            crossword_data.update({name: crossword["url"]})
            crossword_data.move_to_end(name, last=False)
        # if sorted_spider:
        crossword_data.update(
            {"last_updated": str(sorted_spider[0]["date"])}
        )
        # else:
        #     crossword_data["last_updated"] = None
        SpiderManager.write_json(crossword_data)

    def check_run(func):
        """Ask user if they wish to run the spider & run if yes"""
        def wrapper(*args, **kwargs):
            if pyip.inputYesNo("Do you want to run the spider (yes/no)?") \
                    == "yes":
                func(*args, **kwargs)
        return wrapper

    @check_run
    def run_spider(self):
        """Run Spider if Mon/Wed/Fri or if no links saved"""

        process = CrawlerProcess({
            "ITEM_PIPELINES": {
                FormatItemPipeline: 100,
                SaveItemPipeline: 200,
            },
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
            item = MyItem()
            url = crossword_link.css("a::attr(href)").get()
            item['name'] = crossword_link.css("h4::text").get()
            item['author'] = crossword_link.css("p a::text").get()
            item['date'] = crossword_link.css("h6::text").get()

            # if url in previously_scraped.values():
            #     break
            yield response.follow(url, self.parse_crossword,
                                  cb_kwargs=dict(item=item,)
                                  )

    def parse_crossword(self, response, item):
        item['url'] = response.xpath(
            "//iframe[@id='crossword']/@data-src").get()
        yield item


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
