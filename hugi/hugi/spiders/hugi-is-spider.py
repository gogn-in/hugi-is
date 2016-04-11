# -*- coding: utf-8 -*-

import logging
import scrapy
from bs4 import BeautifulSoup
from hugi.items import HugiArticle, HugiUser
from urlparse import urlparse, urlunparse
from dateutil import parser
import datetime


logger = logging.getLogger(__name__)

DETAIL_URL = "http://www.hugi.is{}"
OVERVIEW_URL = "http://www.hugi.is/forsida/{}/"

CATEGORIES = ["greinar",
              "tilkynningar",
              "pistlar",
              "korkar",
              ]


class parserinfo_IS(parser.parserinfo):
    WEEKDAYS = [(u"Mán", u"Mánudagur"),
                (u"Þri", u"Þriðjudagur"),
                (u"Mið", u"Miðvikudagur"),
                (u"Fim", u"Fimmtudagur"),
                (u"Fös", u"Föstudagur"),
                (u"Lau", u"Laugardagur"),
                (u"Sun", u"Sunnudagur")]
    MONTHS   = [(u"Jan", u"Janúar"),
                (u"Feb", u"Febrúar"),
                (u"Mar", u"Mars"),
                (u"Apr", u"Apríl"),
                (u"Maí", u"Maí"),
                (u"Jún", u"Júní"),
                (u"Júl", u"Júlí"),
                (u"Ágú", u"Ágúst"),
                (u"Sep", u"September"),
                (u"Okt", u"Október"),
                (u"Nóv", u"Nóvember"),
                (u"Des", u"Desember")]


class HugiSpider(scrapy.Spider):
    name = "hugi-spider"
    allowed_domains = ["hugi.is"]
    start_urls = [OVERVIEW_URL.format(cat) for cat in CATEGORIES]

    def parse(self, response):
        logger.info("Parsing {}".format(response.url))
        soup = BeautifulSoup(response.body, "html.parser")
        trs = soup.find_all("tr", "item")
        if trs:
            for tr in trs:
                link = tr.find("a")
                article_url = DETAIL_URL.format(link["href"])
                r = scrapy.Request(article_url,
                                         callback=self.parse_article)
                yield r
        # next urls
        try:
            next_url = soup.find(class_="next").a
            cat_url = response.url
            u = urlparse(cat_url)
            query = None
            # Strip the query part
            u = u._replace(query=query)
            follow_url = urlunparse(u) + next_url["href"]
            r = scrapy.Request(follow_url, callback=self.parse)
            yield r
        except AttributeError:
            logger.info("Done with".format(response.url))
            pass

    def text_with_newlines(self, elem):
        """
        Extract text from an element converting br to newlines
        """
        text = ""
        for e in elem.recursiveChildGenerator():
            if isinstance(e, basestring):
                text += e
            elif e.name == "br":
                text += "\n"
        text.replace("\t", "")
        return "\n".join([x for x in text.splitlines() if x.strip()])

    def clean_items(self, item):
        temp = HugiArticle()
        for k, v in item.items():
            if not isinstance(v, list):
                temp[k.strip()] = v.strip().replace("\t", "")
            else:
                if len(v) > 0:
                    templist = []
                    for x in v:
                        templist.append(x.strip().replace("\t", ""))
                    temp[k.strip()] = templist
                else:
                    temp[k.strip()] = v
        return temp

    def parse_user(self, response):
        item = HugiUser()
        soup = BeautifulSoup(response.body, "html.parser")
        username = soup.find(class_="username").text
        id = soup.find(class_="username")["data-userid"]
        points = soup.find(class_="points").text.replace(" stig", "")
        stats_lis = soup.find(class_="threadtypes clearfixme").find_all("li")
        stats = []
        for li in stats_lis:
            if li.a.text != u"Allt":
                stats.append(li.a.text)
        try:
            datestring = soup.find(class_="date")["title"]
            date_parsed = parser.parse(datestring, parserinfo=parserinfo_IS())
        except:
            date_parsed = datetime.date(1970, 1, 1)
        item["date_joined"] = str(date_parsed)
        item["username"] = username
        item["points"] = points
        item["url"] = response.url
        item["stats"] = stats
        item["id"] = id
        yield item

    def parse_article(self, response):
        soup = BeautifulSoup(response.body, "html.parser")
        # drop cruft
        crufts = ["signature",
                  ]
        for k in crufts:
            tags = soup.find_all(class_=k)
            for tag in tags:
                tag.extract()
        article_category, article_type = urlparse(response.url).path.split("/")[1:-3]
        title = soup.find(class_="article content").h1.text
        id = soup.find(class_="article content")["id"]
        content = soup.find(class_="articlebody")
        content = self.text_with_newlines(content)
        datestring = soup.find(class_="date")["title"]
        date_parsed = parser.parse(datestring, parserinfo=parserinfo_IS())
        authorinfo = soup.find(class_="username author")
        author = authorinfo.text
        try:
            author_url = authorinfo["href"]
        except KeyError:
            # No author link - most likely deleted user
            author_url = None
        if author_url:
            author_url = DETAIL_URL.format(author_url)
            r = scrapy.Request(author_url,
                                         callback=self.parse_user)
            yield r
        # comments
        comments = []
        replies = soup.find(class_="replies")
        contents = replies.find_all(class_="replycontent ")
        if contents:
            commentcount = len(contents)
            for comment in contents:
                comments.append(self.text_with_newlines(comment))
            reply_authors = replies.find_all(class_="username author")
            for reply_author in reply_authors:
                try:
                    reply_author_url = reply_author["href"]
                except KeyError:
                    # No author link - most likely deleted user
                    reply_author_url = None
                if reply_author_url:
                    reply_author_url = DETAIL_URL.format(reply_author_url)
                    r = scrapy.Request(reply_author_url,
                                         callback=self.parse_user)
                    yield r
        else:
            commentcount = 0
        item = HugiArticle()
        item["body"] = response.body
        item["title"] = title
        item["date"] = str(date_parsed)
        item["content"] = content
        item["comments"] = comments
        item["commentcount"] = str(commentcount)
        item["url"] = response.url
        item["author"] = author
        item["category"] = article_category
        item["type"] = article_type
        item["id"] = id
        item = self.clean_items(item)
        yield item
