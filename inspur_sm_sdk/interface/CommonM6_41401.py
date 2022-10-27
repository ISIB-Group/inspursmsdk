# -*- coding:utf-8 -*-

import collections
from inspur_sm_sdk.command import RestFunc
from inspur_sm_sdk.interface.CommonM6 import CommonM6
from inspur_sm_sdk.interface.ResEntity import ResultBean


class CommonM6_41401(CommonM6):

    def setpdisk(self, client, args):
        # login
        headers = RestFunc.login_M6(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        try:
            pdisk = setPhysicalDrive(client, args)
        except BaseException:
            RestFunc.logout(client)
        RestFunc.logout(client)
        return pdisk

    def setldisk(self, client, args):
        # login
        headers = RestFunc.login_M6(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(
                ["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)
        try:
            ldisk = setVirtualDrive(client, args)
        except BaseException:
            RestFunc.logout(client)
        RestFunc.logout(client)
        return ldisk


def setPhysicalDrive(client, args):
    result = ResultBean()
    ctrl_type_dict = {
        "LSI": [],
        "PMC": []
    }
    ctrl_id_name_dict = {}
    ctrl_id_list = []
    res = RestFunc.getRaidCtrlInfo(client)
    if res.get('code') == 0 and res.get('data') is not None:
        ctrls = res.get('data')
        for ctrl in ctrls:
            if str(ctrl.get("RaidType")).upper() == "PMC":
                ctrl_type_dict['PMC'].append(ctrl["Name"])
            else:
                ctrl_type_dict['LSI'].append(ctrl["Name"])
            if "Index" in ctrl.keys():
                ctrl_id_name_dict[ctrl["Index"]] = ctrl["Name"]
                ctrl_id_list.append(str(ctrl["Index"]))
            elif "id" in ctrl.keys():
                ctrl_id_name_dict[ctrl["id"]] = ctrl["Name"]
                ctrl_id_list.append(str(ctrl["id"]))
    else:
        result.State("Failure")
        result.Message(["ctrl Information Request Fail!" + res.get('data')])
        return result
    if ctrl_id_list == []:
        result.State("Failure")
        result.Message(["No raid controller!"])
        return result

    ctrl_list_dict = {}
    pds = {}
    res = RestFunc.getPhysicalDiskInfo(client)
    if res.get('code') == 0 and res.get('data') is not None:
        pds = res.get('data')
        for pd in pds:
            if pd['ControllerName'] not in ctrl_list_dict:
                ctrl_list_dict[pd['ControllerName']] = []
            ctrl_list_dict[pd['ControllerName']].append(pd['DeviceID'])
    else:
        result.State("Failure")
        result.Message([res.get('data')])

    for pd in ctrl_list_dict:
        ctrl_list_dict.get(pd).sort()

    if args.Info is not None:
        LSI_flag = False
        raidList = []
        for ctrlid in ctrl_id_name_dict:
            raidDict = collections.OrderedDict()
            raidDict['Controller ID'] = ctrlid
            raidDict['Controller Name'] = ctrl_id_name_dict.get(ctrlid)
            pdiskList = []
            for pd in pds:
                if pd.get("ControllerName") == ctrl_id_name_dict.get(ctrlid):
                    LSI_flag = True
                    pdiskDict = collections.OrderedDict()
                    pdiskDict['Physical Drive ID'] = pd.get("DeviceID")
                    pdiskDict['Physical Drive Name'] = pd.get("Name")
                    pdiskDict['Interface Type'] = pd.get("InterfaceType")
                    pdiskDict['Media Type'] = pd.get("MediaType")
                    pdiskDict['Non Coerced Size'] = pd.get("NONCoercedSize")
                    pdiskDict['Firmware State'] = pd.get("FWState")
                    pdiskList.append(pdiskDict)
            raidDict['pdisk'] = pdiskList
        raidList.append(raidDict)
        if not LSI_flag:
            result.State('Failure')
            result.Message(['No LSI raid controller'])
            return result
        result.State('Success')
        result.Message(raidList)
        return result

    if args.ctrlId is None:
        result.State('Failure')
        result.Message(['Controller id is needed.'])
        return result
    if args.deviceId is None:
        result.State('Failure')
        result.Message(['Physical drive id is needed.'])
        return result

    if args.ctrlId not in ctrl_id_name_dict:
        result.State('Failure')
        result.Message(["Invalid controller id, choose from " + ",".join(ctrl_id_list) + "."])
        return result

    the_pd_list = ctrl_list_dict.get(ctrl_id_name_dict.get(args.ctrlId))
    if str(ctrl_id_name_dict.get(args.ctrlId)) in ctrl_type_dict.get('PMC'):
        ctrl_type = "PMC"
        if args.option != "LOC" and args.option != "STL":
            result.State('Failure')
            result.Message(["Physical drive under PMC raid controller only support LOC and STL."])
            return result
        if args.option == "LOC" and args.duration is None:
            result.State('Failure')
            result.Message(["Please input duration parameter while setting LOC of physical drive under PMC raid controller"])
            return result
    else:
        ctrl_type = "LSI"
    args.ctrl_type = ctrl_type
    if args.deviceId not in the_pd_list:
        result.State('Failure')
        result.Message(["Invalid physical drive slot num, choose from " + str(the_pd_list)])
        return result

    args.location = None
    args.erase = None
    args.status = None
    if args.option == 'LOC':
        args.location = 'StartLocate'
    elif args.option == 'STL':
        args.location = 'StopLocate'
    elif args.option == 'ES':
        args.erase = 'EraseStop'
    elif args.option == 'EM':
        args.erase = 'EraseSimple'
    elif args.option == 'EN':
        args.erase = 'EraseNormal'
    elif args.option == 'ET':
        args.erase = 'EraseThrough'
    elif args.option == 'UG':
        args.status = 'UNCONFIGURED GOOD'
    elif args.option == 'UB':
        args.status = 'UNCONFIGURED BAD'
    elif args.option == 'OFF':
        args.status = 'OFFLINE'
    elif args.option == 'ON':
        args.status = 'ONLINE'
    elif args.option == 'JB':
        args.status = 'JBOD'
    if args.location is not None:
        if args.ctrl_type == "LSI":
            res = RestFunc.locateDiskByRest(client, args.ctrlId, args.deviceId, args.location)
        else:
            if args.duration is not None:
                if args.duration < 1 or args.duration > 255:
                    result.State("Failure")
                    result.Message(["Please enter an integer from 1 to 255."])
                    return result
            res = RestFunc.locateDiskByRestPMC_41401(client, args.ctrlId, args.deviceId, args.location,
                                                     args.duration)
    elif args.erase is not None:
        res = RestFunc.erasePhysicalDisk(
            client, args.ctrlId, args.deviceId, args.erase)
    elif args.status is not None:
        res = RestFunc.setPhysicalDisk(
            client, args.ctrlId, args.deviceId, args.status)
    if res == {}:
        result.State("Failure")
        result.Message(["disk operation failed"])
    elif res.get('code') == 0 and res.get('data') is not None:
        result.State('Success')
        result.Message(
            ['operation is successful,please wait a few seconds.'])
    else:
        result.State("Failure")
        result.Message(
            ['operation failed, ' + str(res.get('data'))])
    return result


def setVirtualDrive(client, args):
    result = ResultBean()
    ctrl_id_name_dict = {}
    ctrl_type_dict = {
        "LSI": [],
        "PMC": []
    }
    ctrl_id_list = []
    res = RestFunc.getRaidCtrlInfo(client)
    if res.get('code') == 0 and res.get('data') is not None:
        ctrls = res.get('data')
        for ctrl in ctrls:
            if str(ctrl.get("RaidType")).upper() == "PMC":
                ctrl_type_dict['PMC'].append(ctrl["Name"])
            else:
                ctrl_type_dict['LSI'].append(ctrl["Name"])
            if "Index" in ctrl.keys():
                ctrl_id_name_dict[ctrl["Index"]] = ctrl["Name"]
                ctrl_id_list.append(str(ctrl["Index"]))
            elif "id" in ctrl.keys():
                ctrl_id_name_dict[ctrl["id"]] = ctrl["Name"]
                ctrl_id_list.append(str(ctrl["id"]))
    else:
        result.State("Failure")
        result.Message(["ctrl Information Request Fail!" + res.get('data')])
        return result
    if ctrl_id_list == []:
        result.State("Failure")
        result.Message(["No raid controller!"])
        return result
    # ld
    ctrl_ld_list_dict = {}
    lds = {}
    res = RestFunc.getLogicalDiskInfo(client)
    if res.get('code') == 0 and res.get('data') is not None:
        lds = res.get('data')
        for ld in lds:
            if ld['ControllerName'] not in ctrl_ld_list_dict:
                ctrl_ld_list_dict[ld['ControllerName']] = []
            if "Index" in ld:
                ctrl_ld_list_dict[ld['ControllerName']].append(ld['Index'])
            elif "TargetID" in ld:
                ctrl_ld_list_dict[ld['ControllerName']].append(ld['TargetID'])
    else:
        result.State("Failure")
        result.Message([res.get('data')])
        return result

    for pd in ctrl_ld_list_dict:
        ctrl_ld_list_dict.get(pd).sort()

    if args.Info is not None:
        LSI_flag = False
        raidList = []
        for ctrlid in ctrl_id_name_dict:
            raidDict = collections.OrderedDict()
            raidDict['Controller ID'] = ctrlid
            raidDict['Controller Name'] = ctrl_id_name_dict.get(ctrlid)
            raidDict['Virtual Drive ID'] = ctrl_ld_list_dict.get(ctrl_id_name_dict.get(ctrlid))
            ldiskList = []
            for ld in lds:
                if ld.get("ControllerName") == ctrl_id_name_dict.get(ctrlid):
                    LSI_flag = True
                    ldiskDict = collections.OrderedDict()
                    ldiskDict['Virtual Drive ID'] = ld.get("Index")
                    ldiskDict['Capacity (GB)'] = ld.get("CAPACITY")
                    ldiskDict['Raid Level'] = ld.get("VOLUME_RAID_LEVEL")
                    ldiskDict['PhysicalDisks'] = ld.get("PhysicalDisks")
                    ldiskDict['Firmware State'] = ld.get("State")
                    ldiskList.append(ldiskDict)
            raidDict['ldisk'] = ldiskList
            raidList.append(raidDict)
        if not LSI_flag:
            result.State('Failure')
            result.Message(['No LSI raid controller'])
            return result
        result.State('Success')
        result.Message(raidList)
        return result

    if args.ctrlId is None:
        result.State('Failure')
        result.Message(['Controller id is needed.'])
        return result
    if args.ldiskId is None:
        result.State('Failure')
        result.Message(['Logical drive id is needed.'])
        return result

    if args.ctrlId not in ctrl_id_name_dict:
        result.State('Failure')
        result.Message(["Invalid controller id, choose from " + ",".join(ctrl_id_list) + "."])
        return result

    the_ld_list = ctrl_ld_list_dict.get(ctrl_id_name_dict.get(args.ctrlId))
    if str(ctrl_id_name_dict.get(args.ctrlId)) in ctrl_type_dict.get('PMC'):
        ctrl_type = "PMC"
        if args.option != "LOC" and args.option != "STL" and args.option != "DEL":
            result.State('Failure')
            result.Message(["Logical drive under PMC raid controller only support LOC, STL, DEL."])
            return result
        if args.option == "LOC" and args.duration is None:
            result.State('Failure')
            result.Message(["Please input duration parameter while setting LOC of logical drive under PMC raid controller."])
            return result
    else:
        ctrl_type = "LSI"

    args.ctrl_type = ctrl_type
    args.location = None
    args.init = None
    args.delete = None
    if args.ldiskId not in the_ld_list:
        result.State('Failure')
        result.Message(["Invalid virtual drive id, choose from " + str(the_ld_list)])
        return result
    if args.option == 'LOC':
        args.location = 'StartLocate'
    elif args.option == 'STL':
        args.location = 'StopLocate'
    elif args.option == 'FI':
        args.init = 'FastInit'
    elif args.option == 'SFI':
        args.init = 'SlowFullInit'
    elif args.option == 'SI':
        args.init = 'StopInit'
    elif args.option == 'DEL':
        args.delete = "NotNone"
    if args.location is not None:
        if args.ctrl_type == "LSI":
            res = RestFunc.locateLogicalDisk(client, args.ctrlId, args.ldiskId, args.location)
        else:
            if args.duration is not None:
                if args.duration < 1 or args.duration > 255:
                    result.State("Failure")
                    result.Message(["Please enter an integer from 1 to 255."])
                    return result
            res = RestFunc.locateLogicalDiskPMC(client, args.ctrlId, args.ldiskId, args.location, args.duration)
    elif args.init is not None:
        res = RestFunc.initLogicalDisk(client, args.ctrlId, args.ldiskId, args.init)
    elif args.delete is not None:
        if args.ctrl_type == "LSI":
            res = RestFunc.deleteLogicalDisk(client, args.ctrlId, args.ldiskId)
        else:
            res = RestFunc.deleteLogicalDiskPMC(client, args.ctrlId, args.ldiskId)
    if res == {}:
        result.State("Failure")
        result.Message(["disk operation failed"])
    elif res.get('code') == 0 and res.get('data') is not None:
        result.State('Success')
        result.Message(
            ['operation is successful,please wait a few seconds.'])
    else:
        result.State("Failure")
        result.Message(
            ['operation failed, ' + str(res.get('data'))])
    return result


def addPMCLogicalDisk(client, args, pds, ctrl_id_name_dict):
    result = ResultBean()
    if args.size is None or args.vname is None or args.accelerator is None or args.slot is None or \
            args.rlevel is None:
        result.State('Failure')
        result.Message(['some parameters are missing'])
        return result

    # args.pd
    args.pdlist = args.slot
    pd_para_len = len(args.pdlist)

    # set raid
    if args.rlevel == 1:
        if pd_para_len < 2:
            result.State('Failure')
            result.Message(['raid 1 need 2 disks at least'])
            return result
    elif args.rlevel == 5:
        if pd_para_len < 3:
            result.State('Failure')
            result.Message(['raid 5 need 3 disks at least'])
            return result
    elif args.rlevel == 6:
        if pd_para_len < 4:
            result.State('Failure')
            result.Message(['raid 6 need 4 disks at least'])
            return result
    elif args.rlevel == 10:
        if pd_para_len < 4:
            result.State('Failure')
            result.Message(['raid 10 need 4 disks at least'])
            return result
    raid_dict = {0: "raid0", 1: "raid1", 5: "raid5", 6: "raid6", 10: "raid10"}
    stripsize_dict_pmc = {1: 7, 2: 8, 3: 9, 4: 10, 5: 11}
    args.rlevel = raid_dict.get(args.rlevel)
    args.size = stripsize_dict_pmc.get(args.size)
    pd_dev_list = []
    for pd_slot_num in args.pdlist:
        for pd in pds:
            if pd['ControllerName'] == ctrl_id_name_dict.get(args.ctrlId) and pd['SlotNum'] == int(pd_slot_num):
                pd_dev_list.append(pd['DeviceID'])
                if pd.get("array_number") != 65535:
                    result.State('Failure')
                    result.Message(['The array number of physical disk is ' + pd.get("array_number")
                                    + ", logical disk can be created only when its array number is 65535."])
                    return result
    deviceId = "~".join(pd_dev_list)
    data = {
        "CTRLID": args.ctrlId,
        "StripeSize": args.size,
        "VDNAME": args.vname,
        "accelerator": args.accelerator,
        "array_number": 65535,
        "deviceId": deviceId,
        "numdrives": len(pd_dev_list),
        "parity_group_count": 1,
        "raid_level": args.rlevel,
        "vendor_type": 1
    }
    res = RestFunc.createVirtualDrive_41401(client, data)
    if res == {}:
        result.State("Failure")
        result.Message(["create virtual drive failed"])
    elif res.get('code') == 0 and res.get('data') is not None:
        result.State('Success')
        result.Message(['create virtual drive successful.'])
    else:
        result.State("Failure")
        result.Message(['create virtual drive failed, ' + str(res.get('data'))])
    return result
