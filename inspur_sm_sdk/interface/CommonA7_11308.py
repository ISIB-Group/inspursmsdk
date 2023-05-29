# -*- coding:utf-8 -*-


from inspur_sm_sdk.interface.CommonA7 import CommonA7


retry_count = 0


# 2023年3月30日 M7 1.13.08 通过redfish配置bios body 必须带Attributes

class CommonA7_11308(CommonA7):
    def formatBiosPatchBody(self, user_bios):
        return {"Attributes": user_bios}


