# -*- coding:utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import copy
import os
import yaml
import sys
import xml.etree.ElementTree as ET

routePath = os.path.join(
    os.path.abspath(
        os.path.dirname(
            os.path.dirname(__file__))),
    "route",
    "route.yml")


# get yaml config util,singleton type
class configUtil():
    def __init__(self):
        pass

    # sinlge
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            if sys.version_info < (3, 0):
                cls._instance = super(configUtil, cls).__new__(cls, *args, **kwargs)
            else:
                cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    # get all configuration option
    def getRouteConfig(self):
        '''
        get route configuration to dict
        :return: all route  dict
        '''
        if os.path.exists(routePath):
            with open(routePath, 'r') as f:
                serverconfig = yaml.load(f.read())
                return serverconfig

    def getRouteOption(self, productName, bmcVersion):
        # try:
        yaml1 = open(routePath)
        content = yaml.load(yaml1, Loader=yaml.BaseLoader)
        yaml1.close()
        if "G220-A" in productName.upper():
            productName = "G220-A"
        elif "G226-A" in productName.upper():
            productName = "G226-A"
        elif "S520-A" in productName.upper():
            productName = "S520-A"
        if content.get(productName.upper(), None):
            model_info = content.get(productName.upper())
            model_keys = copy.deepcopy(list(model_info.keys()))
            model_keys.remove('common')
            if (bmcVersion is None or len(bmcVersion) == 0 or len(model_keys) == 0) and model_info.get('common'):
                return model_info.get("common")
            elif len(model_keys) >= 1:
                model_keys.sort()
                # model_keys = map(eval, model_keys)
                if float(bmcVersion) < float(model_keys[0]):
                    return model_info.get("common")
                if len(model_keys) > 1:
                    for i in range(len(model_keys) - 1):
                        if float(bmcVersion) >= float(model_keys[i]) and float(bmcVersion) < float(model_keys[i + 1]):
                            return model_info.get(str(model_keys[i]))
                return model_info.get(str(model_keys[len(model_keys) - 1]))
            else:
                return "Error: Not find interface of {0}".format(productName)
        return "Error: sdk does not support {0} at present.".format(productName)

    def getModelSupport(self):
        # try:
        yaml1 = open(routePath)
        content = yaml.load(yaml1, Loader=yaml.BaseLoader)
        yaml1.close()
        return list(content.keys())


    # xmlfilepath 文件路径
    def getSetOption(self,xmlfilepath):

        tree = ET.parse(xmlfilepath)  # 调用parse方法返回解析树
        server = tree.getroot()     # 获取根节点

        blongtoSet = set()   # 存储所有的分类
        descriptionList = []  # 存储所有的描述
        infoList = []  # 存储所有xml表示的数据 字典列表


        def sortByKey(obj):
            return obj['key']

        for cfgItems in server:
            for cfgItem in cfgItems:

                info = {}  # 字典
                # name标签
                blongto_text = ''  # 此处只允许有个Item有一个描述和分类
                description_text = ''  # 只有一个描述,
                for name in cfgItem.iter('name'):
                    for belongto in name.iter('belongto'):
                        blongto_text = belongto.text
                    for description in name.iter('description'):
                        description_text = str(description.text).replace(" ", "")

                blongtoSet.add(blongto_text)
                descriptionList.append(description_text)


                # getter标签
                getterCMD=''
                for getter in cfgItem.iter('getter'):
                    getterCMD = getter.text

                # parent标签
                parentKey=''
                for getter in cfgItem.iter('parent'):
                    parentKey = getter.text


                # condition 标签
                predict = {}
                for conditions in cfgItem:
                    if conditions.tag == "conditions":
                        for precon in conditions.iter('condition'):
                            for cmd in precon.iter('key'):
                                # 将tab键替换，换行键替换
                                prekey = cmd.text.replace("\\t","").replace("\\n","")
                            for value in precon.iter('value'):
                                prevalue = value.text
                            predict[prekey]=prevalue

                # #setters标签
                setterlist = []  # 后面嵌套了setOption，是一个字典列表，每一项都是一个字典，字典里面包含{cmd，value，validation}
                sin = False
                for setters in cfgItem.iter('setters'):
                    for setter in setters.iter('setter'):
                        setOption = {}
                        for cmd in setter.iter('cmd'):
                            # 将tab键替换，换行键替换
                            setOption['cmd'] = cmd.text.replace("\\t","").replace("\\n","")
                            #2021年9月13日 不再依赖validation字段判断是否为范围
                            #改为通过看cmd里面是否有$in
                            if "$in" in cmd.text:
                                sin = True
                        for value in setter.iter('value'):
                            setOption['value'] = value.text
                        for validation in setter.iter('validation'):
                            setOption['validation'] = validation.text
                            sin = True
                        # condition 标签
                        for conditions in setter.iter('conditions'):
                            cmdpredict={}
                            for precon in conditions.iter('condition'):
                                for cmd in precon.iter('key'):
                                    # 将tab键替换，换行键替换
                                    prekey = cmd.text.replace("\\t","").replace("\\n","")
                                for value in precon.iter('value'):
                                    prevalue = value.text
                                cmdpredict[prekey] = prevalue
                            setOption["condition"] = cmdpredict
                        setterlist.append(setOption)

                info['getter'] = getterCMD
                info['condition'] = predict
                info['key'] = blongto_text + "_" + description_text
                info['description'] = description_text
                info['blongto'] = blongto_text
                info['input'] = sin
                info['setter'] = setterlist
                info['parent'] = parentKey
                infoList.append(info)

        # infoList=sorted(infoList,key=lambda i:i['key'])
        return blongtoSet, descriptionList ,infoList