from pypinyin import pinyin
import re
import unicodedata
import hashlib


def get_acronym(str_data):
    s = "".join([i[0][0] for i in pinyin(str_data)])
    res = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return res


def getHash(name):
    return hashlib.sha256(name.encode('utf-8')).hexdigest()


def reserve_chinese(content):
    pat = re.compile(r'[\u4e00-\u9fa5]+')
    result = pat.findall(content)
    return "".join(result)
