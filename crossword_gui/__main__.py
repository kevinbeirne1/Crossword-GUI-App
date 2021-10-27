#! /home/kevin/.virtualenvs/crossword_gui/bin python
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
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QApplication, QDialog, QGroupBox, QVBoxLayout,
                             QListWidget, QHBoxLayout)
from scrapy.crawler import CrawlerProcess
from scrapy.item import Item, Field
from scrapy.exceptions import DropItem


class FormatItemPipeline:
    """Pipeline to format scraped spider item data to desired style"""
    def process_item(self, item, spider):
        """
        Attempt to format the scraped item. If error raised, drop the item
        """
        try:
            item["name"] = re.match(r".+:\s?(.*)", item["name"]).group(1)
            item["date"] = datetime.strptime(item['date'], "%B %d, %Y")
            item['url'] = re.match("(.+weekly)", item['url']).group(1)
        except (AttributeError, ValueError, TypeError) as ItemError:
            raise DropItem(f"{ItemError} - Link is article, Not crossword")

        return item


class SaveItemPipeline:
    """Append item to list in SpiderManager"""
    def process_item(self, item, spider):
        SpiderManager.spider_data.append(item)


class MyItem(Item):
    """Specify Item fields that the spider is going to collect"""
    name = Field()
    date = Field()
    url = Field()
    author = Field()


class SpiderManager:
    """Class to manage and run the scrapy spider"""
    spider_data = []

    def __init__(self):
        """Run the spider, add scraped data a json file, read json for crossword links"""
        self.run_spider()
        self.update_json()
        self.crossword_data = self.read_json()

    @staticmethod
    def write_json(data, filename="crossword_data.json"):
        """Write data to a JSON file"""
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
        """
        Sort the scraped spider data by the date field.
        Read the existing crossword data from crossword_data.json
        Add the scraped data to the crossword data.
        Write the updated crossword data to crossword_data.json
        """
        sorted_spider = sorted(SpiderManager.spider_data,
                               key=itemgetter("date"))
        crossword_data = OrderedDict(SpiderManager.read_json(data_file))

        for crossword in sorted_spider:
            name = f'{crossword["name"]} - {crossword["author"]}'
            crossword_data.update({name: crossword["url"]})
            crossword_data.move_to_end(name, last=False)
        SpiderManager.write_json(crossword_data)

    def check_run(self):
        """Ask user if they wish to run the spider & run if yes"""
        def wrapper(*args, **kwargs):
            if pyip.inputYesNo("Do you want to fetch the latest puzzles (yes/no)?") \
                    == "yes":
                self(*args, **kwargs)
        return wrapper

    @check_run
    def run_spider(self):
        """Run NewYorkerSpider"""

        process = CrawlerProcess({
            "ITEM_PIPELINES": {
                FormatItemPipeline: 100,
                SaveItemPipeline: 200,
            },
        })
        process.crawl(NewYorkerSpider)
        process.start()


class NewYorkerSpider(scrapy.Spider):
    """
    Spider to scrape the direct crossword urls from the New Yorker puzzles page
    """
    name = "new_yorker_crossword"
    temp_data = {}

    def start_requests(self):
        """Specify the URLs to crawl through"""
        urls = [
            'https://www.newyorker.com/puzzles-and-games-dept/crossword',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """
        Parse the crossword puzzles main page to get the following for each puzzle:
        - URL
        - Crossword Title
        - Crossword Author
        - Publish Date

        Then follow each URL and scrape with `parse_crossword`
        """

        crossword_links = response.css("li.River__riverItem___3huWr")
        for crossword_link in crossword_links:
            item = MyItem()
            main_page_url = crossword_link.xpath("div/a/@href").get()
            item['name'] = crossword_link.css("h4::text").get()
            item['author'] = crossword_link.css("p a::text").get()
            item['date'] = crossword_link.xpath(".//h6/text()").get()

            yield response.follow(main_page_url, self.parse_crossword,
                                  cb_kwargs=dict(item=item,)
                                  )

    def parse_crossword(self, response, item):
        """
        Parse the url from the main page to get the url to the crossword host site
        """
        item['url'] = response.xpath(
            "//iframe[@id='crossword']/@data-src").get()
        # item['date'] = response.xpath(
        #     ".//time[@data-testid='ContentHeaderPublishDate']/text()").get()
        yield item


def window():
    """Start the PyQt window"""
    app = QApplication([])
    win = WidgetGallery()
    win.showMaximized()
    sys.exit(app.exec_())


class WidgetGallery(QDialog):

    def __init__(self, parent=None):
        """
        Get the crossword from SpiderManager and start the GUI
        """
        super(WidgetGallery, self).__init__(parent)
        self.button_links = SpiderManager().crossword_data

        self.embedded_browser = self.create_embedded_browser()

        self.create_left_group_box()
        self.create_right_group_box()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.left_group_box)
        main_layout.addWidget(self.right_group_box)
        self.setLayout(main_layout)

    def create_left_group_box(self):
        """
        Left box group contains:
         - list of crosswords
         - Clicking item in the list loads it's url with self.clicked
        """
        self.left_group_box = QGroupBox("Crossword list")
        self.left_group_box.setMaximumWidth(400)

        self.crossword_list = QListWidget()
        self.crossword_list.addItems(self.button_links)
        self.crossword_list.clicked.connect(self.clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.crossword_list)
        layout.setContentsMargins(10, 10, 10, 10)
        self.left_group_box.setLayout(layout)

    def create_right_group_box(self):
        """
        Create right box group with the embedded browser
        """
        self.right_group_box = QGroupBox("Browser")

        layout = QVBoxLayout()
        layout.addWidget(self.embedded_browser)
        self.right_group_box.setLayout(layout)

    def change_site(self, url):
        """Change the embedded browser url to the provided url"""
        self.embedded_browser.setUrl(QUrl(url))

    def clicked(self):
        """
        Get the url from the crossword_data dictionary and change
        the embedded browser to this url
        """
        item = self.crossword_list.currentItem()
        self.change_site(self.button_links[item.text()])

    @staticmethod
    def create_embedded_browser(self):
        """Create an embedded browser for the GUI """
        _embedded_browser = QWebEngineView()
        _embedded_browser.setUrl(QUrl("http://google.com"))
        return _embedded_browser


if __name__ == '__main__':
    window()

