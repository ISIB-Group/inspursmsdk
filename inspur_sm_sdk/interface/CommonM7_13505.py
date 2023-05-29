# -*- coding:utf-8 -*-

from inspur_sm_sdk.interface.CommonM7 import CommonM7


retry_count = 0


# 2023年3月30日 M7 1.35.05 通过redfish配置bios body 必须带Attributes
class CommonM7_13505(CommonM7):
    def formatBiosPatchBody(self, user_bios):
        return {"Attributes": user_bios}


