# -*- coding: utf-8 -*-

from hugi.items import HugiArticle, HugiUser
from hugi.settings import DATA_DIR
import logging
from scrapy.utils.serialize import ScrapyJSONEncoder
import os
from dateutil import parser
import gzip

logger = logging.getLogger(__name__)

_encoder = ScrapyJSONEncoder()


class HugiUserPipeline(object):
    def __init__(self):
        pass

    def process_item(self, item, spider):
        if isinstance(item, HugiUser):
            directory = os.path.join(DATA_DIR, "users")
            username = item["username"].strip().replace(" ", "_").lower()
            json_filename = os.path.join(directory, username + ".json")
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(json_filename, "w") as f:
                f.write(_encoder.encode(item))
            return item
        else:
            return item


class HugiArticlePipeline(object):
    def __init__(self):
        pass

    def process_item(self, item, spider):
        if isinstance(item, HugiArticle):
            date_parsed = parser.parse(item["date"])
            directory = os.path.join(DATA_DIR, item["type"],
                                 date_parsed.strftime("%Y"),
                                 date_parsed.strftime("%m"),
                                 date_parsed.strftime("%d")
                                    )
            json_filename = os.path.join(directory, item["id"] + ".json")
            txt_filename = os.path.join(directory, item["id"] + ".txt")
            raw_filename = os.path.join(directory, item["id"] + "-html.gz")
            if not os.path.exists(directory):
                os.makedirs(directory)
            with gzip.open(raw_filename, "w") as f:
                f.write(item["body"])
            with open(txt_filename, "w") as f:
                f.write(item["title"].encode("utf-8"))
                f.write("\n\n")
                f.write(item["content"].encode("utf-8"))
                if len(item["comments"]) > 0:
                    f.write("\n--\n")
                    for comment in item["comments"]:
                        f.write(comment.encode("utf-8"))
                        f.write("\n-\n")
            item.pop("content", None)
            item.pop("comments", None)
            item.pop("body")
            with open(json_filename, "w") as f:
                f.write(_encoder.encode(item))
            return item
        else:
            return item
