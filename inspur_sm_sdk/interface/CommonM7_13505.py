# -*- coding:utf-8 -*-

from inspur_sm_sdk.interface.CommonM7 import CommonM7
from inspur_sm_sdk.command import RestFunc
from inspur_sm_sdk.interface.ResEntity import ResultBean



retry_count = 0


# 2023年3月30日 M7 1.35.05 通过redfish配置bios body 必须带Attributes
class CommonM7_13505(CommonM7):
    def formatBiosPatchBody(self, user_bios):
        return {"Attributes": user_bios}

    def delsession(self, client, args):
        result = ResultBean()
        headers = RestFunc.login_M6(client)
        if headers == {}:
            login_res = ResultBean()
            login_res.State("Failure")
            login_res.Message(["login error, please check username/password/host/port"])
            return login_res
        client.setHearder(headers)

        # 先get
        id_list = []
        res = RestFunc.getSessionsBMCByRest(client)
        if res.get('code') == 0 and res.get('data') is not None and len(res.get('data')) != 0:
            num = len(res.get('data'))
            for i in range(num):
                id_list.append(str(res.get('data')[i].get('session_id')))

            # 如果输入参数，检查参数范围，如果正确，进行删除
            if args.id == 'all':
                # 如果不输入，循环调用，全部删除
                flag = []
                # 比通用多一个data
                del_data = {"id": 1}
                for i in range(num):
                    res1 = RestFunc.deleteSessionBMCByRestA7(client, id_list[i], del_data)
                    if res1.get('code') == 0 and res1.get('data') is not None and res1.get('data').get('cc', 1) == 0:
                        continue
                    else:
                        flag.append(str(id_list[i]))
                        continue
                if len(flag) != 0:
                    result.State('Failure')
                    result.Message(['delete session id {0} failed.'.format(','.join(flag) if len(flag) > 1 else flag)])
                else:
                    result.State('Success')
                    result.Message(['delete session id {0} success, please wait a few seconds.'.format(
                        ','.join(id_list) if len(id_list) > 1 else id_list)])
            else:
                if str(args.id) in id_list:
                    # 比通用多一个data
                    del_data = {"id": 1}
                    res1 = RestFunc.deleteSessionBMCByRestA7(client, args.id, del_data)
                    if res1.get('code') == 0 and res1.get('data') is not None and res1.get('data').get('cc', 1) == 0:
                        result.State('Success')
                        result.Message(['delete session id {0} success, please wait a few seconds.'.format(args.id)])
                    elif res1.get('code') == 0 and res1.get('data') is not None and res1.get('data').get('cc', 1) != 0:
                        result.State('Failure')
                        result.Message(['delete vnc session request parsing failed.'])
                    else:
                        result.State('Failure')
                        result.Message(['delete session id {0} failed， '.format(args.id) + res1.get('data')])
                else:
                    result.State('Failure')
                    result.Message(['wrong session id, please input right id, id list is {0}.'.format(
                        ','.join(id_list) if len(id_list) > 1 else id_list)])
        elif res.get('code') == 0 and res.get('data') is not None and len(res.get('data')) == 0:
            result.State('Failure')
            result.Message(['session count is 0.'])
        else:
            result.State('Failure')
            result.Message(['failed to get session info, ' + res.get('data')])

        RestFunc.logout(client)
        return result

