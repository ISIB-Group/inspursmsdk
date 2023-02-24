# -*- coding:utf-8 -*-
import sys
import os

from inspur_sm_sdk.command import RestFunc, IpmiFunc
from inspur_sm_sdk.interface.CommonM7 import CommonM7
from inspur_sm_sdk.interface.ResEntity import (
    ResultBean,
    fwBean,
    fwSingleBean
)

retry_count = 0


class CommonA7(CommonM7):
    def _get_xml_file(self):
        xml_path = os.path.join(IpmiFunc.command_path, "bios") + os.path.sep
        return xml_path + 'A7.xml'

    def setpowerbudget(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The A7 model does not support this feature.'])
        return result

    def getpowerbudget(self, client, args):
        result = ResultBean()
        result.State("Not Support")
        result.Message(['The A7 model does not support this feature.'])
        return result

    def getfw(self, client, args):
        '''
        get fw version
        :param client:
        :param args:
        :return:fw version
        '''
        result = ResultBean()
        fw = fwBean()
        fwlist = []
        Type = {'P1V05_PCH_AUX': 'BMC', 'PVNN_PCH_AUX': 'BMC', 'BMC': 'BMC', 'BMC0': 'BMC', 'BMC1': 'BMC',
                'BIOS': 'BIOS', 'PSU': 'PSU', 'TPM': 'TPM', 'CPU': 'CPU', 'CPLD': 'CPLD', 'ME': 'ME', 'FPGA': 'FPGA',
                'PVDDIO': "CPLD"}
        Name_Format = {'BIOS': 'BIOS', 'ME': 'ME', 'PSU_0': 'PSU0', 'PSU_1': 'PSU1', 'CPLD': 'MainBoardCPLD',
                       'Front_HDD_CPLD0': 'DiskBPCPLD', 'Rear_HDD_CPLD0': 'RearDiskBPCPLD', 'FPGA': 'FPGA'}
        SupportActivateType = {
            'P1V05_PCH_AUX': ['resetbmc'],
            'PVNN_PCH_AUX': ['resetbmc'],
            'BMC': ['resetbmc'],
            'BMC1': ['resetbmc'],
            'BMC0': ['resetbmc'],
            'CPU': ['resetbmc'],
            'BIOS': ['resethost', 'poweroff', 'dcpowercycle'],
            'CPLD': ['resethost', 'poweroff', 'dcpowercycle'],
            'ME': ['resethost', 'poweroff', 'dcpowercycle'],
            'FPGA': ['resethost', 'poweroff', 'dcpowercycle'],
            'PSU': ['resethost', 'poweroff', 'dcpowercycle']}
        Update = {'BMC': True, 'BMC0': True, 'BMC1': True, 'BIOS': True, 'ME': True, 'PSU': True, 'CPLD': True}
        if 'target' in args:
            if args.target is not None:
                shuishan_fw_list = ["BMC0", "BMC1", 'BIOS', 'CPLD', 'FPGA']
                cbmc = IpmiFunc.getSmartnicCurrentBMC(client)
                for key in shuishan_fw_list:
                    fwversion, info = IpmiFunc.getShuishanBMCVersionT6(client, key)
                    fwsingle = fwSingleBean()
                    if cbmc == key:
                        fwsingle.Name("ActiveBMC")
                    elif key == "BMC0" or key == "BMC1":
                        fwsingle.Name("BackupBMC")
                    else:
                        fwsingle.Name(Name_Format.get(key))
                    if info == "":
                        fwsingle.Type(Type[key])
                        fwsingle.Version(fwversion)
                        fwsingle.Updateable(Update.get(key, False))
                        fwsingle.SupportActivateType(SupportActivateType.get(key, ['none']))
                    else:
                        fwsingle.Type(None)
                        fwsingle.Version(None)
                        fwsingle.Updateable(None)
                        fwsingle.SupportActivateType([])
                    fwlist.append(fwsingle.dict)
                fw.Firmware(fwlist)
                result.State("Success")
                result.Message([fw.dict])
                return result
        # login
        headers = RestFunc.login_M6(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        # get
        res = RestFunc.getFwVersion(client)
        if res == {}:
            result.State("Failure")
            result.Message(["cannot get information"])
        elif res.get('code') == 0 and res.get('data') is not None:
            result.State("Success")
            data = res.get('data')
            size = len(data)
            for i in range(size):
                fwsingle = fwSingleBean()
                fwversion = None
                flag = 0
                name_raw = data[i].get('dev_name')
                if name_raw in Name_Format:
                    fwsingle.Name(Name_Format[name_raw])
                elif 'Inactivate' in name_raw:
                    fwsingle.Name('BackupBMC')
                elif 'Activate' in name_raw:
                    fwsingle.Name('ActiveBMC')
                else:
                    fwsingle.Name(name_raw)
                index_version = data[i].get('dev_version').find('(')
                if index_version == -1:
                    fwversion = None if data[i].get('dev_version') == '' else data[i].get('dev_version')
                else:
                    fwversion = None if data[i].get('dev_version') == '' else data[i].get('dev_version')[
                                                                              :index_version].strip()
                for key in Type.keys():
                    if key in data[i].get('dev_name'):
                        fwsingle.Type(Type[key])
                        fwsingle.Version(fwversion)
                        fwsingle.Updateable(Update.get(key, False))
                        fwsingle.SupportActivateType(SupportActivateType.get(key, ['none']))
                        flag = 1
                        break
                if flag == 0:
                    fwsingle.Type(None)
                    fwsingle.Version(None)
                    fwsingle.Updateable(None)
                    fwsingle.SupportActivateType([])
                fwlist.append(fwsingle.dict)
            fw.Firmware(fwlist)
            result.Message([fw.dict])
        else:
            result.State("Failure")
            result.Message(["get fw information error, " + str(res.get('data'))])
        # logout
        RestFunc.logout(client)
        return result
