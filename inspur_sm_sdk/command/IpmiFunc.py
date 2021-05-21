# -*- coding:utf-8 -*-

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import ctypes
import json
import sys
import re
import os
import math
import platform
import time

sys.path.append(os.path.dirname(sys.path[0]))
rootpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(rootpath, "util"))


DEVICE_ID = {
    0x0014: "MegaRAID Tri-Mode SAS3516",
    0x0016: "MegaRAID Tri-Mode SAS3508",
    0x005b: "MegaRAID SAS 2208",
    0x005d: "MegaRAID SAS-3 3108",
    0x005f: "MegaRAID SAS-3 3008",
    0x0097: "SAS3008 PCI-Express Fusion-MPT SAS-3",
    0x00ac: "SAS3416 Fusion-MPT Tri-Mode I/O Controller Chip (IOC)",
    0x2261: "ISP2722-based 16/32Gb Fibre Channel to PCIe Adapter",
    0xe200: "Lancer-X: LightPulse Fibre Channel Host Adapter",
    0xe300: "Lancer Gen6: LPe32000 Fibre Channel Host Adapter",
    0x5180: "9100 PRO NVMe SSD",
    0x16d7: "BCM57414 NetXtreme-E 10Gb/25Gb RDMA Ethernet Controller",
    0x1003: "MT27500 Family [ConnectX-3]",
    0x1017: "MT27800 Family [ConnectX-5]",
    0x0710: "OneConnect 10Gb NIC (be3)",
    0x1013: "MT27700 Family [ConnectX-4]",
    0x0a03: "SFC9220 10/40G Ethernet Controller",
    0xa804: "NVMe SSD Controller SM961/PM961",
    0x1007: "MT27520 Family [ConnectX-3 Pro]",
    0x1015: "MT27710 Family [ConnectX-4 Lx]",
    0x37d1: "Ethernet Connection X722 for 1GbE",
    0x37d2: "Ethernet Connection X722 for 10GBASE-T",
    0x37d3: "Ethernet Connection X722 for 10GbE SFP+",
    0x0953: "PCIe Data Center SSD",
    0x0a54: "Express Flash NVMe P4510",
    0x10c9: "82576 Gigabit Network Connection",
    0x10f8: "82599 10 Gigabit Dual Port Backplane Connection",
    0x10fb: "82599ES 10-Gigabit SFI/SFP+ Network Connection",
    0x1521: "I350 Gigabit Network Connection",
    0x1528: "Ethernet Controller 10-Gigabit X540-AT2",
    0x1529: "82599 10 Gigabit Dual Port Network Connection with FCoE",
    0x152a: "82599 10 Gigabit Dual Port Backplane Connection with FCoE",
    0x1557: "82599 10 Gigabit Network Connection",
    0x1572: "Ethernet Controller X710 for 10GbE SFP+",
    0x0540: "PBlaze4 NVMe SSD",
    0x0550: "PBlaze5 NVMe SSD",
    # 0xc4: "SAS9305",
    0x028d: "Series 8 12G SAS/PCIe 3",
    0x9361: "MegaRAID SAS 9361-8i",
    0x9371: "MegaRAID SAS 9361-16i",
    0x9364: "MegaRAID SAS 9364-8i",
    0x0017: "MegaRAID Tri-Mode SAS3408",
    0x3090: "SAS9311-8i",
    0x30a0: "SAS9300-8e",
    0x30e0: "SAS9300-8i",
    0x00af: "SAS3408 Fusion-MPT Tri-Mode I/O Controller Chip (IOC)",
    0x00ce: "MegaRAID SAS-3 3316 [Intruder]",
    0x37c8: "PF0 for Intel QuikAssist Technology",
    0x37cc: "10 Gb Ethernet",
    0x37ce: "Ethernet Connection X722 for 10GbE backplane",
    0x37d0: "Ethernet Connection X722 for 10GbE SFP+",
    0x1522: "I350 Gigabit Fiber Network Connection",
    0x1537: "I210 Gigabit Backplane Connection",
    0x1584: "Ethernet Controller XL710 for 40GbE SFP+",
    0x24f0: "Omni-Path HFI Silicon 100 Series [discrete]",
    0x028f: "Smart Storage PQI 12G SAS/PCIe 3",
    0x0100: "MLU100-C3/C4",
    0x13f2: "Tesla M60",
    0x15f8: "Tesla P100 PCIe 16GB",
    0x1b30: "Quadro P6000",
    0x1bb0: "Quadro P5000",
    0x1bb1: "Quadro P4000",
    0x1bb3: "P4 GPU",
    0x1c30: "Quadro P2000",
    0x1db1: "V100-SXM2 GPU",
    0x1db5: "V100-SXM2 GPU",
    0x1b38: "P40 GPU",
    0x1db4: "V100-PCIE GPU",
    # NF5468M5补充
    0x2031: "ISP8324-based 16Gb Fibre Channel to PCI Express Adapter",
    0x2532: "ISP2532-based 8Gb Fibre Channel to PCI Express HBA",
    0x101e: "GK110GL [Tesla K20X]",
    0x101f: "GK110GL [Tesla K20]",
    0x1020: "GK110GL [Tesla K20X]",
    0x1021: "GK110GL [Tesla K20Xm]",
    0x1022: "GK110GL [Tesla K20c]",
    0x1023: "GK110BGL [Tesla K40m]",
    0x1024: "GK110BGL [Tesla K40c]",
    0x1026: "GK110GL [Tesla K20s]",
    0x1027: "GK110BGL [Tesla K40st]",
    0x1028: "GK110GL [Tesla K20m]",
    0x1029: "GK110BGL [Tesla K40s]",
    0x102a: "GK110BGL [Tesla K40t]",
    0x102d: "GK210GL [Tesla K80]",
    0x102e: "GK110BGL [Tesla K40d]",
    0x13bc: "GM107GL [Quadro K1200]",
    0x1431: "GM206GL [Tesla M4]",
    0x13bd: "GM107GL [Tesla M10]",
    0x17fd: "GM200GL [Tesla M40]",
    0x1b06: "GTX1080TI GPU",
    0x1db6: "Tesla V100 PCIE 32G GPU",
    0x15f7: "GP100GL [Tesla P100 PCIe 32GB]",
    0x15f9: "GP100GL [Tesla P100 SXM2 16GB]",
    0xf100: "Saturn-X: LightPulse Fibre Channel Host Adapter",
    0xf180: "LLPSe12002 EmulexSecure Fibre Channel Adapter",
    0x00d1: "HBA 9405W-16i"

}
VENDOR_ID = {

    0x1000: "LSI Logic / Symbios Logic",
    0x1001: "Kolter Electronic",
    0x1002: "Advanced Micro Devices, Inc",
    0x1003: "ULSI Systems",
    0x1004: "VLSI Technology Inc",
    0x1005: "Avance Logic Inc",
    0x1006: "Reply Group",
    0x1007: "NetFrame Systems Inc",
    0x1008: "Epson",
    0x100a: "Phoenix Technologies",
    0x100b: "National Semiconductor Corporation",
    0x100c: "Tseng Labs Inc",
    0x100d: "AST Research Inc",
    0x100e: "Weitek",
    0x1010: "Video Logic, Ltd",
    0x1011: "Digital Equipment Corporation",
    0x1012: "Micronics Computers Inc",
    0x1013: "Cirrus Logic",
    0x1014: "IBM",
    0x1015: "LSI Logic Corp of Canada",
    0x1016: "ICL Personal Systems",
    0x1017: "SPEA Software AG",
    0x1018: "Unisys Systems",
    0x1019: "Elitegroup Computer Systems",
    0x101a: "AT&T GIS (NCR)",
    0x101b: "Vitesse Semiconductor",
    0x101c: "Western Digital",
    0x101d: "Maxim Integrated Products",
    0x101e: "American Megatrends Inc",
    0x101f: "PictureTel",
    0x1020: "Hitachi Computer Products",
    0x1021: "OKI Electric Industry Co. Ltd",
    0x1022: "Advanced Micro Devices, Inc",
    0x1023: "Trident Microsystems",
    0x1024: "Zenith Data Systems",
    0x1025: "Acer Incorporated",
    0x1028: "Dell",
    0x1029: "Siemens Nixdorf IS",
    0x102a: "LSI Logic",
    0x102b: "Matrox Electronics Systems Ltd",
    0x102c: "Chips and Technologies",
    0x102d: "Wyse Technology Inc",
    0x102e: "Olivetti Advanced Technology",
    0x102f: "Toshiba America",
    0x1030: "TMC Research",
    0x1031: "Miro Computer Products AG",
    0x1032: "Compaq",
    0x1033: "NEC Corporation",
    0x1034: "Framatome Connectors USA Inc",
    0x1035: "Comp. & Comm. Research Lab",
    0x1036: "Future Domain Corp",
    0x1037: "Hitachi Micro Systems",
    0x1038: "AMP, Inc",
    0x1039: "Silicon Integrated Systems",
    0x103a: "Seiko Epson Corporation",
    0x103b: "Tatung Corp. Of America",
    0x103c: "Hewlett-Packard Company",
    0x103e: "Solliday Engineering",
    0x103f: "Synopsys/Logic Modeling Group",
    0x1040: "Accelgraphics Inc",
    0x1041: "Computrend",
    0x1042: "Micron",
    0x1043: "ASUSTeK Computer Inc",
    0x1044: "Adaptec",
    0x1045: "OPTi Inc",
    0x1046: "IPC Corporation, Ltd",
    0x1047: "Genoa Systems Corp",
    0x1048: "Elsa AG",
    0x1049: "Fountain Technologies, Inc",
    0x104a: "STMicroelectronics",
    0x104b: "BusLogic",
    0x104c: "Texas Instruments",
    0x104d: "Sony Corporation",
    0x104e: "Oak Technology, Inc",
    0x104f: "Co-time Computer Ltd",
    0x1050: "Winbond Electronics Corp",
    0x1051: "Anigma, Inc",
    0x1052: "?Young Micro Systems",
    0x1053: "Young Micro Systems",
    0x1054: "Hitachi, Ltd",
    0x1055: "Microchip Technology / SMSC",
    0x1056: "ICL",
    0x1057: "Motorola",
    0x1058: "Electronics & Telecommunications RSH",
    0x1059: "Kontron",
    0x105a: "Promise Technology, Inc",
    0x105b: "Foxconn International, Inc",
    0x105c: "Wipro Infotech Limited",
    0x105d: "Number 9 Computer Company",
    0x105e: "Vtech Computers Ltd",
    0x105f: "Infotronic America Inc",
    0x1060: "United Microelectronics",
    0x1061: "I.I.T.",
    0x1062: "Maspar Computer Corp",
    0x1063: "Ocean Office Automation",
    0x1064: "Alcatel",
    0x1065: "Texas Microsystems",
    0x1066: "PicoPower Technology",
    0x1067: "Mitsubishi Electric",
    0x1068: "Diversified Technology",
    0x1069: "Mylex Corporation",
    0x106a: "Aten Research Inc",
    0x106b: "United Microelectronics",
    0x106c: "Hynix Semiconductor",
    0x106d: "Sequent Computer Systems",
    0x106e: "DFI, Inc",
    0x106f: "City Gate Development Ltd",
    0x1070: "Daewoo Telecom Ltd",
    0x1071: "Mitac",
    0x1072: "GIT Co Ltd",
    0x1073: "Yamaha Corporation",
    0x1074: "NexGen Microsystems",
    0x1075: "Advanced Integrations Research",
    0x1076: "Chaintech Computer Co. Ltd",
    0x1077: "QLogic Corp",
    0x1078: "Cyrix Corporation",
    0x1079: "I-Bus",
    0x107a: "NetWorth",
    0x107b: "Gateway, Inc",
    0x107c: "LG Electronics",
    0x107d: "LeadTek Research Inc",
    0x107e: "Interphase Corporation",
    0x107f: "Data Technology Corporation",
    0x1080: "Contaq Microsystems",
    0x1081: "Supermac Technology",
    0x1082: "EFA Corporation of America",
    0x1083: "Forex Computer Corporation",
    0x1084: "Parador",
    0x1086: "J. Bond Computer Systems",
    0x1087: "Cache Computer",
    0x1088: "Microcomputer Systems (M) Son",
    0x1089: "Data General Corporation",
    0x108a: "SBS Technologies",
    0x108c: "Oakleigh Systems Inc",
    0x108d: "Olicom",
    0x108e: "Oracle/SUN",
    0x108f: "Systemsoft",
    0x1090: "Compro Computer Services, Inc",
    0x1091: "Intergraph Corporation",
    0x1092: "Diamond Multimedia Systems",
    0x1093: "National Instruments",
    0x1094: "First International Computers",
    0x1095: "Silicon Image, Inc",
    0x1096: "Alacron",
    0x1097: "Appian Technology",
    0x1098: "Quantum Designs (H.K.) Ltd",
    0x1099: "Samsung Electronics Co., Ltd",
    0x109a: "Packard Bell",
    0x109b: "Gemlight Computer Ltd",
    0x109c: "Megachips Corporation",
    0x109d: "Zida Technologies Ltd",
    0x109e: "Brooktree Corporation",
    0x109f: "Trigem Computer Inc",
    0x123f: "LSI Logic",
    0x11ca: "LSI Systems, Inc",
    0x11c1: "LSI Corporation",
    0x10db: "Rohm LSI Systems, Inc",
    0x10df: "Emulex Corporation",
    0x1166: "Broadcom",
    0x10de: "NVIDIA Corporation",
    0x11f8: "PMC-Sierra Inc.",
    0x1344: "Micron Technology Inc.",
    0x15b3: "Mellanox Technologies",
    0x19a2: "Emulex Corporation",
    0x1c5f: "Beijing Memblaze Technology Co. Ltd.",
    0x1fc1: "QLogic, Corp.",
    0x8086: "Intel Corporation",
    0x9005: "Adaptec",
    0x9004: "Adaptec",
    0x14e4: "Brodcom Limited",
    0x144d: "Samsung Electronics Co Ltd",
    0x1924: "Solarflare Communications",
    0xcabc: "Cambricon"
}


# 获取传感器信息
# getsensor
def getSensorByNameByIpmi(client, findname):
    res = {}
    import platform
    sysstr = platform.system()
    cmd_get = 'sensor list'
    if findname != None:
        if sysstr == 'Windows':
            cmd_get = cmd_get + ' | find "' + findname + '" '
        elif sysstr == 'Linux':
            cmd_get = cmd_get + ' | grep "' + findname + '" '
    result = getLinesRawByIpmi(client, cmd_get)
    if result['code'] != 0:
        return result
    line_list = result['data']
    Normal_list = ['ok', '0x8080', '0x4080', '0x0280', '0x0180']
    Absent_list = ['na', '0x0080']
    Critical_list = ['nr']
    list = []
    sdrNumber = __getSdrElist(client)
    for line in line_list:
        item_json = {}
        str_tul = str(line).split('|')
        item_json['name'] = str_tul[0].strip()
        item_json['num'] = sdrNumber[str_tul[0].strip()]
        item_json['value'] = str_tul[1].strip()
        item_json['unr'] = str_tul[9].strip()
        item_json['uc'] = str_tul[8].strip()
        item_json['unc'] = str_tul[7].strip()
        item_json['lnr'] = str_tul[6].strip()
        item_json['lc'] = str_tul[5].strip()
        item_json['lnc'] = str_tul[4].strip()
        item_json['unit'] = str_tul[2].strip()
        status = str_tul[3].strip()
        if status in Normal_list:
            item_json['status'] = "Normal"
        elif status in Absent_list:
            item_json['status'] = "Absent"
        elif status in Critical_list:
            item_json['status'] = "Critical"
        else:
            item_json['status'] = "Critical"
        list.append(item_json)
    res['code'] = 0
    res['data'] = list
    return res


def getSensorByIpmi(client):
    return getSensorByNameByIpmi(client, None)


# 获取temp信息
# gettemp
def getSensorsTempByIpmi(client):
    return getSensorByNameByIpmi(client, 'degrees C')


# 获取volt信息
# getvolt
def getSensorsVoltByIpmi(client):
    return getSensorByNameByIpmi(client, 'Volts')


def getAllFruByIpmi(client):
    JSON = {}
    cmd_get = ' fru print 0 '
    result = getLinesRawByIpmi(client, cmd_get)
    if result['code'] != 0:
        return JSON
    line_list = result['data']
    if line_list is None or len(line_list) == 0:
        return JSON
    for line in line_list:
        if ':' in line:
            str_tul = str(line).split(':')
            name = str_tul[0].strip()
            value = str_tul[1].strip()
            JSON[name] = value
    return JSON


def getProductNameByIpmi(client):
    JSON = getAllFruByIpmi(client)
    productName = None
    if "Product Name" in JSON:
        productName = JSON['Product Name']
    return productName


# 获取传感器序号 和sensor联合可以确定传感器序号
# getsensor
def __getSdrElist(client):
    JSON = {}
    cmd_get = 'sdr elist'
    result = getLinesRawByIpmi(client, cmd_get)
    if result['code'] != 0:
        return JSON
    line_list = result['data']
    if line_list is not None:
        for line in line_list:
            item_json = {}
            str_tul = str(line).split('|')
            JSON[str_tul[0].strip()] = int(str_tul[1].strip().replace('h', ''), 16)
    # JSON = json.dumps(JSON, sort_keys=False, indent=4)
    return JSON


def setM5BiosByipmi(client, cmd):
    return sendRawByIpmi(client, cmd)


def setM5BiosEffectiveByipmi(client):
    cmd = '0x3c 0x4a 0x02'
    return sendRawByIpmi(client, cmd)


def getRaidTypeByIpmi(client):
    cmd = '0x3c 0x3b 0x02'
    return getLineRawByIpmi(client, cmd)


def getM5PcieCountByIpmi(client):
    """
    get pcie count
    :param client:
    :return:
    """
    cmd_count = 'raw 0x3c 0x02 0x04 0xff 0xff'
    count_info = getLineRawByIpmi(client, cmd_count)
    if count_info['code'] == 0:
        count_info['data'] = int(str(count_info['data']).strip(), 16)
    return count_info


def getM5PcieByIpmi(client, pcie_count):
    """
    get pcie info
    :param client:
    :return:  pcie info
    """
    pcie_data = ''
    Pcie = {}
    pcie_xcount = hex(pcie_count - 1)
    cmd_get = '0x3c 0x02 0x04 0x00 ' + str(pcie_xcount)
    pcieInfo_all = getLinesRawByIpmi(client, cmd_get)
    if pcieInfo_all["code"] == 0:
        pcie_data = pcieInfo_all['data']
    else:
        return pcieInfo_all
    cmd_str = ' '.join(pcie_data).replace(' ', '').replace('\n', '')
    if len(cmd_str) < 19 * 2 * pcie_count + 6:
        Pcie['code'] = 1
        Pcie['data'] = "this command is incompatible with current server."
        return Pcie
    cmd_str = cmd_str[6:]
    present_dict = {'00': 'Absent', '01': 'Present'}
    enable_dict = {'00': 'Disabled', '01': 'Enabled'}
    present_status_dict = {'00': 'onboard', '01': 'offboard'}
    width_dict = {
        '00': 'unknown',
        '01': 'X1',
        '02': 'X2',
        '04': 'X4',
        '08': 'X8',
        '10': 'X16'}
    speed_dict = {'00': 'unknown', '01': 'GEN1', '02': 'GEN2', '03': 'GEN3'}
    type_dict = {
        '00': 'Device was built before Class Code definitions were finalized',
        '01': 'Mass storage controller',
        '02': 'Network controller',
        '03': 'Display controller',
        '04': 'Multimedia device',
        '05': 'Memory controller',
        '06': 'Bridge device',
        '07': 'Simple communication controller',
        '08': 'Base system peripherals',
        '09': 'input device',
        '0a': 'Docking stations',
        '0b': 'Processors',
        '0c': 'Serial bus controller',
        '0d': 'Wireless controller',
        '0e': 'intelligent I/O controller',
        '0f': 'Satellite communication controllers',
        '10': 'Encryption/Decryption controllers',
        '11': 'Data acquisition and signal processing controllers',
        '12': 'Processing accelerators',
        '13': 'reserved',
        'ff': 'Device does not fit in any defined classes',
    }
    riser_type_dict = {
        '00': 'unknown',
        '01': 'X8+X8+X8',
        '02': 'X8+X16',
        '03': 'X8+X8',
        '04': 'X16',
        'ff': 'NO Riser'}
    location_dict = {
        '00': 'UP',
        '01': 'middle',
        '02': 'down',
        'ff': 'NO Riser'}
    list = []
    for i in range(pcie_count):
        item_json = {}
        if len(cmd_str) < 19 * 2 * (i + 1):
            Pcie['code'] = 1
            Pcie['data'] = "this command is incompatible with current server."
            return Pcie
        pcie_str = '00010001' + cmd_str[19 * 2 * i:19 * 2 * (i + 1)]
        text = cmd_str[19 * 2 * i + 2:19 * 2 * (i + 1)]
        if max(text) == '0':
            continue
        index = pcie_str[8:10]
        item_json['Id'] = int(index, 16)
        type = pcie_str[38:40]
        item_json['Type'] = type_dict.get(type, 'null')
        busNumber = pcie_str[24:26]
        item_json['busNumber'] = '0x' + busNumber
        deviceNumber = pcie_str[26:28]
        item_json['deviceNumber'] = '0x' + deviceNumber
        functionNumber = pcie_str[28:30]
        item_json['functionNumber'] = '0x' + functionNumber
        enableStat = pcie_str[12:14]
        item_json['enableStat'] = enable_dict.get(enableStat, 'null')
        presentStat = pcie_str[10:12]
        item_json['presentStat'] = present_dict.get(presentStat, 'null')
        presentStatus = pcie_str[14:16]
        item_json['presentStatus'] = present_status_dict.get(
            presentStatus, 'null')
        vendorId = '0x' + str(pcie_str[18:20]) + str(pcie_str[16:18])
        item_json['vendorId'] = VENDOR_ID.get(int(vendorId, 16), 'null')
        deviceId = '0x' + str(pcie_str[22:24]) + str(pcie_str[20:22])
        item_json['deviceId'] = DEVICE_ID.get(int(deviceId, 16), 'null')
        # print(hex(int(deviceId,16)))
        # print(DEVICE_ID.get(hex(int(deviceId,16)),'null'))
        maxLinkWidth = pcie_str[30:32]
        item_json['maxLinkWidth'] = width_dict.get(maxLinkWidth, 'null')
        maxLinkSpeed = pcie_str[32:34]
        item_json['maxLinkSpeed'] = speed_dict.get(maxLinkSpeed, 'null')
        NegotiatedLinkWidth = pcie_str[34:36]
        item_json['NegotiatedLinkWidth'] = width_dict.get(
            NegotiatedLinkWidth, 'null')
        CurrentLinkSpeed = pcie_str[36:38]
        item_json['CurrentLinkSpeed'] = speed_dict.get(
            CurrentLinkSpeed, 'null')
        pcieSlot = pcie_str[40:42]
        item_json['pcieSlot'] = pcieSlot
        RiserType = pcie_str[42:44]
        item_json['RiserType'] = riser_type_dict.get(RiserType, 'null')
        pcieLocationOnRiser = pcie_str[44:46]
        item_json['pcieLocationOnRiser'] = location_dict.get(
            pcieLocationOnRiser, 'null')
        list.append(item_json)
    Pcie['code'] = 0
    Pcie['data'] = list
    return Pcie


def locateServerByIpmi(client, state):
    cmd = "raw 0x00 0x04 0x00 " + state
    return sendRawByIpmi(client, cmd)


# Configure SNMPTrap Policy
def setSNMPTrapPolicyByIpmi(client, policyId, channel, enable):
    res = {}
    if 1 <= policyId <= 3:
        policyId_raw = "0x0" + str(policyId)
    else:
        res["code"] = 1
        return res
    if enable == 1:
        enable_raw = "0x" + str(policyId) + "8"
    elif enable == 0:
        enable_raw = "0x" + str(policyId) + "0"
    channel_raw = "0x" + str(channel) + str(policyId)

    cmd_set = 'raw 0x04 0x12 0x09 ' + policyId_raw + \
        " " + enable_raw + " " + channel_raw + " 0x00"
    return sendRawByIpmi(client, cmd_set)


# Set alert type to SNMPTrap
def setAlertTypeByIpmi(client, policyId, channel, type):
    res = {}
    channel_raw = "0x0" + str(channel)
    if 1 <= policyId <= 3:
        policyId_raw = "0x0" + str(policyId)
    else:
        res["code"] = 1
        return res
    if type == "snmp":
        type_raw = "0x00"
    else:
        type_raw = "0x06"

    cmd_set = 'raw 0x0C 0x01 ' + channel_raw + " 0x12 " + \
        policyId_raw + " " + type_raw + " 0x03 0x03"
    return sendRawByIpmi(client, cmd_set)



# Set destination IP
def setDestIPByIpmi(client, destinationId, channel, ip):
    res = {}
    channel_raw = "0x0" + str(channel)
    destinationId_raw = "0x0" + str(destinationId)
    ip_raw = hex(int(ip.split(".")[0])) + " " + hex(int(ip.split(".")[1])) + \
        " " + hex(int(ip.split(".")[2])) + " " + hex(int(ip.split(".")[3]))
    cmd_set = 'raw 0x0C 0x01 ' + channel_raw + " 0x13 " + destinationId_raw + \
        " 0x00 0x00 " + ip_raw + " 0x00 0x00 0x00 0x00 0x00 0x00"
    return sendRawByIpmi(client, cmd_set)


# 设置用户权限
# priv: 2为user权限 3为operator权限 4为administrator
def setUserPrivByIpmi(client, userId, priv):
    cmd_get = 'user priv ' + str(userId) + ' ' + str(priv) + ' 1'
    return sendRawByIpmi(client, cmd_get)


def getHostname(client):
    cmd_get = "raw 0x32 0x6b 0x01 0x00"
    return sendRawByIpmi(client, cmd_get)


def setHostname(client, hostname):
    res = {}
    length = len(hostname)
    hostname_cmd = " "
    for i in range(length):
        hostname_cmd = hostname_cmd + " " + str(hex(ord(hostname[i])))
    len16 = hex(length)
    if len(len16) == 3:
        len16 = "0x0" + len16[2]
    # 5-132为hostname
    cmd_set = 'raw 0x32 0x6c 0x01 0x00 0x00 ' + len16 + \
        hostname_cmd + " 0x00" * (132 - 5 + 1 - length)
    return sendRawByIpmi(client, cmd_set)


# M5 UPDATE BMC
def getMac(client):
    cmd_get = "raw 0x3c 0x11 0x00 0x06 0x08 0x00"
    return sendRawByIpmi(client, cmd_get)


def setDedicatedMac(client, mac1):
    res = {}
    mac_cmd = ""
    mac_list = mac1.splite(" ")
    if len(mac_list) == 6:
        for m in mac_list:
            mac_cmd = mac_cmd + " 0x" + m
        cmd_set = 'raw 0x3c 0x11 0x01 0x06 0x08 0x00 ' + mac_cmd
        return sendRawByIpmi(client, cmd_set)
    else:
        return {"code": 1, "data": mac1 + " is not a valid MAC"}


def resetBMCByIpmi(client):
    cmd_get = 'mc reset cold'
    return sendRawByIpmi(client, cmd_get)


# fruid int
# c0 Chassis Part Number
# c1 Chassis Serial
# c2 error
# b0 Board Mfg
# b1 Board Product
# b2 Board Serial
# b3 Board Part Number
# p0 Product Manufacturer
# p1 Product Name
# p2 Product Part Number
# p3 Product Version
# p4 Product Serial
# p5 Product Asset Tag
def editFruByIpmi(client, fruid, section, index, value):
    cmd_get = 'fru edit ' + str(fruid) + ' field' + str(section) + ' ' + str(index) + ' ' + value
    return sendRawByIpmi(client, cmd_get)


# nouse
def getM5WebByIpmi(client):
    cmd_get = 'raw 0x32 0x69 0x01 0x00 0x00 0x00 '
    web_Info = __Service(client, cmd_get, 'web')
    return web_Info


def __Service(client, cmd_get, serviceName):
    """
    common get service info
    :param client:
    :param cmd_get:
    :param serviceName:
    :return: service info
    """
    get_Info = getLinesRawByIpmi(client, cmd_get)
    if get_Info['code'] == 0:
        data = get_Info['data']
    else:
        return get_Info
    cmd_str = ' '.join(data).replace(' ', '').replace('\n', '')
    if len(cmd_str) < 88:
        get_Info['code'] = 4
        get_Info['data'] = 'this command is incompatible with current server.'
        return get_Info
    item_json = {}
    status_dict = {'00': 'Disabled', '01': 'Enabled'}
    id = cmd_str[0:8]
    if id[0:2] == "00":
        item_json['Id'] = 0
    else:
        item_json['Id'] = str(math.log(int(id[0:2], 16), 2) + 1)
    item_json['ServiceName'] = serviceName
    status = cmd_str[8:10]
    item_json['Status'] = status_dict[status]
    InterfaceName = cmd_str[10:44]
    item_json['InterfaceName'] = __hex2ascii(InterfaceName)
    if item_json['InterfaceName'] not in ["both", "eth0", "eth1", "bond1"]:
        item_json['InterfaceName'] = 'N/A'
    NonsecurePort = cmd_str[44:52]
    if "ff" in NonsecurePort:
        item_json['NonsecurePort'] = 'N/A'
    else:
        item_json['NonsecurePort'] = __hex2int(NonsecurePort)

    SecurePort = cmd_str[52:60]
    if "ff" in SecurePort:
        item_json['SecurePort'] = 'N/A'
    else:
        item_json['SecurePort'] = __hex2int(SecurePort)
    Timeout = cmd_str[60:68]
    if "ff" in Timeout:
        item_json['Timeout'] = 'N/A'
        item_json['MinimumTimeout'] = 'N/A'
        item_json['MaximumTimeout'] = 'N/A'
    else:
        item_json['Timeout'] = __hex2int(Timeout)
        MinimumTimeout = cmd_str[72:80]
        item_json['MinimumTimeout'] = __hex2int(MinimumTimeout)
        MaximumTimeout = cmd_str[80:88]
        item_json['MaximumTimeout'] = __hex2int(MaximumTimeout)

    MaximumSessions = cmd_str[68:70]
    if "ff" in MaximumSessions:
        item_json['MaximumSessions'] = 'N/A'
    else:
        binmax = '{:08b}'.format(int(MaximumSessions, 16))
        item_json['MaximumSessions'] = int(binmax[2:8], 2)
    ActiveSessions = cmd_str[70:72]
    binac = '{:08b}'.format(int(ActiveSessions, 16))
    item_json['ActiveSessions'] = int(binac[2:8], 2)
    get_Info['data'] = item_json
    return get_Info


# nouse
def setM5WebByIpmi(client, enabled, interface, nonsecure, secure, time):
    set_web = __setService(
        client,
        '0x01 0x00 0x00 0x00',
        enabled,
        interface,
        nonsecure,
        secure,
        time,
        '0x00')
    return set_web


def getM5BiosByipmi(client, cmd, List):
    Info_data = getLinesRawByIpmi(client, cmd)
    if Info_data.get('code') == 0:
        cmd_result = Info_data.get('data')
    else:
        return Info_data
    bios_Info = {}
    result = M5biosResultExplanByIpmi(cmd_result, List)
    if result:
        if result.get('code') == 0:
            bios_Info['code'] = 0
            bios_Info['data'] = result.get('data')
        else:  # 解析的返回值不是9或6，暂时未解析
            bios_Info['code'] = 1
            bios_Info['data'] = 'failed to get info.'
    else:  # 解析失败
        bios_Info['code'] = 2
        bios_Info['data'] = 'failed to get info.'
    return bios_Info


def M5biosResultExplanByIpmi(cmd_result, List):
    """
    # 根据返回结果，对应解析出它的状态
    # 返回值格式：01 00 00 C8 00 01 00 01 00
    # 从左到右返回值说明：
    # 01 00 -- 高位00 低位01 --返回值个数
    # 00 C8 -- 高位00 -- GroupIndex 低位C8--SubIndex
    # 00--标志位，是否有修改过，00 表示未被修改，01 表示被修改。
    # 01 00 -- 高位00 低位01 --Current Value  关注当前值Current Value，与set时相似
    # 01 00 -- 高位00 低位01 --Default Value
    # 将get和set的Current Value相比较，对应找到当前值并进行展示
    :param cmd_result:
    :param List:
    :return:
    """
    result = {}
    result_split = str(cmd_result).split()
    if len(result_split) == 9:
        currentValueL = result_split[5]  # 取出低位，索引从0开始
        currentValueH = result_split[6]  # 取出高位
        Flag_set = False
        set_Attribute = List['setter']
        attribute = List['description']
        for set_cmd in set_Attribute:
            temp_set_cmd = set_cmd['cmd']
            set_split = str(temp_set_cmd).split()
            set_L = set_split[-2]
            set_H = set_split[-1]
            if currentValueL.lower() == set_L[2:].lower(
            ) and currentValueH.lower() == set_H[2:].lower():
                Flag_set = True
                key = str(attribute)
                value = set_cmd['value']
                result['code'] = 0
                result['data'] = {}
                result['data']['key'] = key
                result['data']['value'] = value
                break
        if not Flag_set:
            # 出现这种现象的原因有两种
            # 一种是可能输入的BIOS项拼写错误，
            # 一种是设置项输入是数字，不能直接将get和set的直接进行对比，直接将get的值读出即可
            if List['input']:
                value_int = (str(currentValueH) + (str(currentValueL)))
                getValue = int(value_int, 16)
                key = str(attribute)
                value = getValue
                result['code'] = 0
                result['data'] = {}
                result['data']['key'] = key
                result['data']['value'] = value
            else:
                key = str(attribute)
                value = "Unsupport"
                result['code'] = 0
                result['data'] = {}
                result['data']['key'] = key
                result['data']['value'] = value
    elif len(result_split) == 6:
        currentValueH = ''.join(result_split[2:])  # 取出选项值
        Flag_set = False
        set_Attribute = List['setter']
        attribute = List['description']
        for set_cmd in set_Attribute:
            temp_set_cmd = set_cmd['cmd']
            set_split = str(temp_set_cmd).split()
            leng = len(set_split)
            for s in range(1, leng + 1):
                set_split[s - 1] = set_split[s - 1].replace("0x", "")
            set_H = ''.join(set_split[-4:])
            if currentValueH.upper() == set_H.upper():
                Flag_set = True
                key = str(attribute)
                value = set_cmd['value']
                result['code'] = 0
                result['data'] = {}
                result['data']['key'] = key
                result['data']['value'] = value
                break
        if not Flag_set:
            # 出现这种现象的原因有两种
            # 一种是可能输入的BIOS项拼写错误，
            # 一种是设置项输入是数字，不能直接将get和set的直接进行对比，直接将get的值读出即可
            if List['input']:
                s = list(reversed(result_split[2:]))
                value_int = ''.join(s)
                getValue = int(value_int, 16)
                key = str(attribute)
                value = str(getValue)
                result['code'] = 0
                result['data'] = {}
                result['data']['key'] = key
                result['data']['value'] = value
            else:
                key = str(attribute)
                value = 'Unsupport'
                result['code'] = 0
                result['data'] = {}
                result['data']['key'] = key
                result['data']['value'] = value
    else:
        result['code'] = 1
        result['data'] = {}
    return result


def getRaidStatusByIpmi(client, cid):
    cmd_get = "raw 0x3c 0xb9 0x05 0x00 " + hex(int(cid))
    result = getLineRawByIpmi(client, cmd_get)
    flg = ''
    if result['code'] != 0:
        flg = result['data']
    return flg


# nouse
def getM5BiosVersionByIpmi(client):
    res = {}
    cmd_get = 'raw 0x3c 0x03 0x01 0x00'
    result = getLinesRawByIpmi(client, cmd_get)
    if result['code'] != 0:
        return result
    num_list = result['data']
    cmd_str = ' '.join(num_list).replace(' ', '').replace('\n', '')
    res['code'] = 0
    res['data']['Version'] = __hex2ascii(cmd_str)
    return res

def getPowerStatusByIpmi(client):
    res = {}
    cmd_get = 'power status'
    result = getLineRawByIpmi(client, cmd_get)
    if result['code'] != 0:
        return result
    cmd_str = result['data']
    cmd_str = cmd_str.replace('\n', '')
    cmd_str = str(cmd_str).split(' ')[-1]
    res['code'] = 0
    res['data']['status'] = cmd_str
    return res


# 设置电源开关状态
# status : on off soft reset cycle
def powerControlByIpmi(client, status):
    list = ['on', 'off', 'soft', 'reset', 'cycle']
    res = {}
    if status in list:
        cmd_get = 'power ' + status
        result = getLineRawByIpmi(client, cmd_get)
        if result['code'] != 0:
            return result
        cmd_str = result['data']
        if 'Chassis Power Control' in cmd_str:
            res['code'] = 0
            time.sleep(3)
            result = getPowerStatusByIpmi(client)
            res['data'] = result['data']
        else:
            res['code'] = -1
            res['data'] = 'None'
    return res


def getSysbootByIpmi(client):
    cmd_set = 'raw 0x00 0x09 0x05 0x00 0x00 '
    return getLineRawByIpmi(client, cmd_set)


def clearSelByIpmi(client):
    cmd_get = ' sel clear'
    return getLineRawByIpmi(client, cmd_get)


# BIOS boot mode
def setBootModeByIpmi(client, mode):
    if mode.upper() == "UEFI":
        mode_raw = "0x02"
    else:
        mode_raw = "0x01"
    cmd_set = 'raw 0x3c 0x48 0x00 0x2d ' + mode_raw + " 0x00 "
    return sendRawByIpmi(client, cmd_set)


# BIOS boot options
def setBIOSBootOptionByIpmi(client, timeliness, option):
    res = {}
    if timeliness == "next":
        timeliness_raw = "0x20"
    else:
        timeliness_raw = "0x60"
    if option == "none":
        option_raw = "0x00"
    elif option == "HDD":
        option_raw = "0x02"
    elif option == "PXE":
        option_raw = "0x01"
    elif option == "CD":
        option_raw = "0x05"
    elif option == "BIOSSETUP":
        option_raw = "0x06"
    else:
        res["code"] = 1
        res["data"] = option + " is not supported"
        return res

    cmd_unlock = 'raw 0x00 0x08 0x05 '
    cmd_set = 'raw 0x00 0x08 0x05 ' + timeliness_raw + \
        " " + option_raw + " 0x00 0x00 0x00"

    res_unlock = sendRawByIpmi(client, cmd_unlock)
    if res_unlock["code"] == 0:
        return sendRawByIpmi(client, cmd_set)
    else:
        return res_unlock


# 时间戳
def setBMCTimeByIpmi(client, stamptime):
    res = {}
    try:
        # 本地时间戳1555400100+28800
        stamptimelocal = stamptime - time.timezone
        # 本地时间戳16进制
        stampHex = hex(stamptimelocal)
        # 命令的16进制
        time16 = "0x" + stampHex[8:10] + " 0x" + stampHex[6:8] + \
            " 0x" + stampHex[4:6] + " " + stampHex[0:4]
    except ValueError as e:
        res["code"] = 1
        return res
    # 执行
    cmd_time = 'raw 0x0A 0x49 ' + time16
    return sendRawByIpmi(client, cmd_time)


# zone minutes in string
def setBMCTimezoneByIpmi(client, zoneMinutes):
    if zoneMinutes < 0:
        zoneMinutes16 = (0xffff + zoneMinutes + 0x1)
        zoneMinutes16 = hex(zoneMinutes16)
    elif zoneMinutes > 0:
        zoneMinutes16 = hex(zoneMinutes)
    else:
        zoneMinutes16 = "0x0000"
    # 执行
    cmd_time = 'raw 0x0A 0x5D 0x' + zoneMinutes16[-2:] + " " + zoneMinutes16[:-2]
    return sendRawByIpmi(client, cmd_time)


# 修改密码
def setUserPassByIpmi(client, userId, code):
    cmd_get = 'user set password ' + str(userId) + ' ' + code
    return getLineRawByIpmi(client, cmd_get)


# 获取用户信息
def getUserByIpmi(client):
    cmd_get = 'user list 1'
    result = getLinesRawByIpmi(client, cmd_get)
    if result['code'] != 0:
        return result
    res = {}
    list = []
    user_list = result['data']
    if user_list is not None:
        for line in user_list[1:]:
            item_json = {}
            str_tul = re.sub(' +', ' ', str(line))
            str_tul = str_tul.split(' ')
            if len(str_tul) == 6 and 'NO ACCESS' in line:
                continue
            item_json['UserId'] = str_tul[0].strip()
            item_json['UserName'] = str_tul[1].strip()
            item_json['RoleId'] = str_tul[5].strip()
            item_json['Privilege'] = 'None'
            item_json['Enabled'] = 'None'
            item_json['Callin'] = str_tul[2].strip()
            item_json['LinkAuth'] = str_tul[3].strip()
            item_json['IPMIMsg'] = str_tul[4].strip()
            list.append(item_json)
        res['code'] = 0
        res['data'] = list
    else:
        res['code'] = 1
        res['data'] = 'user not exits'
    return res


# 获取vnc配置信息
def getM5VncByIpmi(client):
    """
    get vnc ifo
    :param client:
    :return: ssh info
    """
    cmd_get = 'raw 0x32 0x69 0x00 0x01 0x00 0x00 '
    vnc_Info = __Service(client, cmd_get, 'vnc')
    return vnc_Info


def setM5VncByIpmi(client, enabled, interface, nonsecure, secure, time):
    set_vnc = __setService(
        client,
        '0x00 0x01 0x00 0x00',
        enabled,
        interface,
        nonsecure,
        secure,
        time,
        '0x00')
    return set_vnc


def setM5VncPwdByIpmi(client, pwd):
    cmd = 'raw 0x3c 0x59 ' + pwd
    return sendRawByIpmi(client, cmd)


def setM5BiosPwdByIpmi(client, type, pwd):
    cmd = "raw 0x3c 0x4a 0x0f " + type + ' ' + pwd
    return sendRawByIpmi(client, cmd)


def clearBiospwdM5ByIpmi(client, type):
    cmd = "raw 0x3c 0x4a 0x10 " + type
    return sendRawByIpmi(client, cmd)


# {'code': 0, 'data': '01'}
def getFirewallByIpmi(client):
    cmd_set = 'raw 0x3c 0x3b 0x15 '
    return getLinesRawByIpmi(client, cmd_set)


def restoreBiosM5ByIpmi(client):
    cmd = "raw 0x3c 0x4a 0x0c 0x20"
    return sendRawByIpmi(client, cmd)


# {'data': '', 'code': 0}
def setFirewallByIpmi(client, state):
    res = {}
    if state == "close":
        state_raw = "0x00"
    elif state == "black":
        state_raw = "0x01"
    elif state == "white":
        state_raw = "0x02"
    else:
        res["code"] = 2
        res["data"] = "unsupport firewall state " + state
        return res
    cmd_set = 'raw 0x3c 0x3a 0x15 ' + state_raw
    return sendRawByIpmi(client, cmd_set)


def getFirmwareVersoinByIpmi(client):
    JSON ={}
    cmd_get = 'raw 0x3c 0x37 '+hex(int(0))
    result = getLinesRawByIpmi(client, cmd_get)
    if result['code'] != 0:
        return ''
    num_list = result['data']
    cmd_str = ' '.join(num_list).replace(' ', '').replace('\n', '')
    if len(cmd_str) < 24:
        return ''
    version = cmd_str[4:10]
    bmcversion = str(int(version[0:2],16))+'.'+str(int(version[2:4],16))
    return bmcversion


# 获取设备信息
def getM6DeviceNumByIpmi(client,data):
    '''
    get Device Number info
    :param client:
    :return: Device Number
    '''
    cmd_get = 'raw 0x3c 0x2b ' + data
    Num_Info = sendRawByIpmi(client, cmd_get)
    Num = {}
    if Num_Info['code'] == 0:
        data_list = Num_Info['data'].split(' ')
        if len(data_list) == 2:
            Num['code'] = 0
            Num['data'] = {}
            Num['data']['DevNum'] = int(data_list[0],16)
            if data_list[1] == 'ff':
                Num['data']['DevConfNum'] = int(data_list[0], 16)
            else:
                Num['data']['DevConfNum'] = int(data_list[1],16)
        elif len(data_list) == 3:
            Num['code'] = 0
            Num['data'] = {}
            Num['data']['DevNum'] = int(data_list[1],16)
            if data_list[2] == 'ff':
                Num['data']['DevConfNum'] = int(data_list[1], 16)
            else:
                Num['data']['DevConfNum'] = int(data_list[2],16)
        else:
            Num['code'] = 1
            Num['data'] = Num_Info['data']
    else:
        return Num_Info


def getMcInfoByIpmi(client):
    '''
    get Product FRU  information
    :param client:
    :return product FRU  information:
    '''
    JSON = {}
    result = getLinesRawByIpmi(client, 'mc info')
    if result['code'] != 0:
        return result
    line_list = result['data']
    data = {}
    for line in line_list:
        if 'Firmware Revision' in line:
            str_tul = str(line).split(':')
            value = str_tul[1].strip()
            data['firmware_revision'] = value
        elif 'Aux Firmware Rev Info' in line:
            value = line_list[line_list.index(line) + 1].strip()
            data['aux_firmware_rev_info'] = value[2:]
            break
    JSON['code'] = 0
    JSON['data'] = data
    return JSON


# 设置service
def __setService(
        client,
        serviceid_hex,
        enabled,
        interface,
        nonsecure,
        secure,
        time,
        maximum_hex):
    cmd_set = 'raw 0x32 0x6a  ' + serviceid_hex + ' ' + enabled + ' ' + interface + \
        ' ' + nonsecure + ' ' + secure + ' ' + time + ' ' + maximum_hex + ' 0x00'
    return sendRawByIpmi(client, cmd_set)


def sendRawByIpmi(client, raw):
    res = {}
    result = __getCmd_type(client, raw, 'readline')
    if result['code'] != 0:
        return result
    cmd_str = result['data']
    if cmd_str != '\n':
        res['code'] = -1
        res['Data'] = 'Failure: ' + cmd_str
        return res
    res['code'] = 0
    res['data'] = 'Success'
    return res


def getLineRawByIpmi(client, raw):
    res = __getCmd_type(client, raw, 'readline')
    return res


def getLinesRawByIpmi(client, raw):
    res = __getCmd_type(client, raw, 'readlines')
    return res


# ip地址转换十六进制
def __ip2hex(ip):
    tup_ip = str(ip).split('.')
    list_s = []
    for item in tup_ip:
        hex_item = str(hex(int(item)))
        list_s.append(hex_item)
    return ' '.join(list_s)


# 十六进制字符串逆序
def __hexReverse(data):
    pattern = re.compile('.{2}')
    time_hex = ' '.join(pattern.findall(data))
    seq = time_hex.split(' ')[::-1]
    data = '0x' + ' 0x'.join(seq)
    return data


# 十六进制字符串拆分
def __hexsplit(data):
    pattern = re.compile('.{2}')
    time_hex = ' 0x'.join(pattern.findall(data))
    data = '0x' + time_hex
    return data


# 十六进制转换Ascii
def __hex2ascii(data):
    list_s = []
    if data is not None and len(data) % 2 == 0:
        if data == '':
            return ''
        # for i in range(0,len(data),2):
        #     list_s.append(chr(int(data[i:i+2],16)))
        i = 0
        while (True):
            hex_str = data[i:i + 2]
            if '00' == hex_str:
                break
            chr_str = chr(int(hex_str, 16))
            list_s.append(chr_str)
            i += 2
            if i == len(data):
                break
    hex_str = ''
    if list_s:
        hex_str = ''.join(list_s).replace('\n', '').replace('\r', '')
    return hex_str


# Ascii转十六进制
def __ascii2hex(data, length):
    if len(data) > length:
        return -1, ''
    count = length - len(data)
    list_h = []
    for c in data:
        list_h.append(str(hex(ord(c))))
    data = ' '.join(list_h) + ' 0x00' * count
    return 0, data


# 十六进制字符串转int
#  先逆序 后转换
def __hex2int(data):
    if data is not None and len(data) % 2 == 0:
        pattern = re.compile('.{2}')
        time_hex = ' '.join(pattern.findall(data))
        seq = time_hex.split(' ')[::-1]
        data = ''.join(seq)
    if data == '':
        return 0
    return int(data, 16)


# 十六进制字符串转int
# 求多个的和
def __hex2int_sum(data):
    sum = 0
    if data is not None and len(data) % 2 == 0:
        i = 0
        while (True):
            hex_str = data[i:i + 2]
            sum = sum + int(hex_str, 16)
            i += 2
            if i == len(data):
                break
    return sum


# int转换hex
# -65535 ~ 65535
def __int2hex(data):
    data_hex = ''
    if data >= 0:
        data_hex = hex(data)
        data_hex = data_hex[2:len(data_hex)]
        if len(data_hex) % 2 != 0:
            data_hex = '0' + data_hex
        data_hex = __hexReverse(data_hex)
    else:
        data_hex = __negative2hex(data)
    return data_hex


# 求一个负数的十六进制
# neg 负数
# 返回格式 0x00 0x00
def __negative2hex(neg):
    neg_hex = hex(neg & 0xFFFF)
    neg_hex = neg_hex[2:len(neg_hex)]
    return __hexReverse(neg_hex)


# 根据截取位数转字符串
def __byte2string(byte, arg0, arg1):
    if arg1 is None:
        str = ' '.join(byte[arg0]).replace(' ', '').replace('\n', '')
    else:
        str = ' '.join(byte[arg0:arg1]).replace(' ', '').replace('\n', '')
    return str


def __getCmd_type(client, cmd_get, rt):
    res = {}
    import platform
    sysstr = platform.system()
    if sysstr == 'Windows':
        cmdPrefix = "..\\tools\\ipmitool\\ipmitool.exe -U " + client.username + " -P " + client.passcode + " -H " + client.host + "-I " + client.lantype + " " + cmd_get + " 2>nul"
    elif sysstr == 'Linux':
        cmdPrefix = "ipmitool -U " + client.username + " -P " + client.passcode + " -H " + client.host + " -I " + client.lantype + " " + cmd_get + " 2>/dev/null"
    cmd_str = ''
    str_list = []
    try:
        with os.popen(cmdPrefix, 'r') as p:
            if rt == 'readline':
                cmd_str = p.readline()
            elif rt == 'readlines':
                str_list = p.readlines()
            else:
                cmd_str = p.readline()
    except IOError:
        res['code'] = 1
        res['data'] = 'error occurs while reading file!'
        return res
    except:
        print('Failure: error executing IPMI command.')
        res['code'] = 2
        res['data'] = 'error executing IPMI command.'
        return res
    res['code'] = 0
    if rt == 'readlines':
        res['data'] = str_list
    else:
        res['data'] = cmd_str
    return res
