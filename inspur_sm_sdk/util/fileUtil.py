# -*- coding:utf-8 -*-
import re
import os


def parseUrl(fileurl):
    if fileurl == ".":
        file_name = ""
        file_path = os.path.abspath(".")
    elif fileurl == "..":
        file_name = ""
        file_path = os.path.abspath("..")
    elif os.path.isdir(fileurl):
        file_name = ""
        file_path = os.path.abspath(fileurl)
    else:
        file_name = os.path.basename(fileurl)
        file_path = os.path.dirname(fileurl)

    # 只输入文件名字，则默认为当前路径

    if file_path == "":
        file_path = os.path.abspath(".")
    return True, file_path, file_name


def checkUrl(fileurl):
    file_name = os.path.basename(fileurl)
    file_path = os.path.dirname(fileurl)

    #fileurl = os.path.join(file_path, file_name)

    if not os.path.exists(file_path):
        try:
            os.makedirs(file_path)
        except BaseException:
            return False, "can not create path."
    else:
        if os.path.exists(fileurl):
            name_id = 1
            name_extension = os.path.splitext(file_name)[1]
            name_prefix = os.path.splitext(file_name)[0]
            if name_extension == ".gz" and os.path.splitext(name_prefix)[
                    1] == ".tar":
                name_prefix = os.path.splitext(name_prefix)[0]
                name_extension = ".tar.gz"
            name_new = name_prefix + "(1)" + name_extension
            file_new = os.path.join(file_path, name_new)
            while os.path.exists(file_new):
                name_id = name_id + 1
                name_new = name_prefix + \
                    "(" + str(name_id) + ")" + name_extension
                file_new = os.path.join(file_path, name_new)
            fileurl = file_new

    return True, fileurl
