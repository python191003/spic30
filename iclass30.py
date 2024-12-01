import requests
import json

class User:
    details = {}
    def __init__(self, id="", token=""):
        self.details["id"] = id
        self.details["token"] = token
    def __getattr__(self, name):
        return self.details[name]


class iclass30:
    """C30大多数功能的封装，首先，你应该登录：
        iclass30(账号，密码)
    如果你已经获得了用户的id和token或其他人token，你可以使用：
        iclass30(id,token)
    C30中的大多数api已经被安全环保的封装，比如你可以这样：
        c30 = iclass30(账，密)
        info = c30.getUserInfo({"userId":c30.user.id,"serviceVersion":"13.0"})
    这只是一个举例，获取当前用户信息远没有这么麻烦，你可以通过
        c30.user.avatar
        c30.user.realname
        c30.user.sex_text
    等信息直接获取"""
    user:User = User()
    INDEX = {
        'getLoginUserInfo': 'service.iclass30.com/userMgr/baselogin/getLoginUserInfo',
        'getUserRoleIdList': 'service.iclass30.com/operag/operator/getUserRoleIdList',
        'getCommonCatchListByAppTypes': 'service.iclass30.com/public/catch/getCommonCatchListByAppTypes',
        'getAppMenuByUser': 'service.iclass30.com/appmgr/roleAppMeun/getAppMenuByUser',
        'getUserInfo': 'homeworkservice.iclass30.com/userMgr/baselogin/getUserInfo',
        'getPublicConfigBySchoolInfo': 'homeworkservice.iclass30.com/public/config/getPublicConfigBySchoolInfo',
        'getStuWorkList': 'homeworkservice.iclass30.com/homework/stuhomework/getStuWorkList',
        'getSubjectListByPhase': 'homeworkservice.iclass30.com/userMgr/basesubject/getSubjectListByPhase',
        'getSchoolYearList': 'homeworkservice.iclass30.com/homeworkstatic/common/getSchoolYearList',
        'checkPass': 'homeworkservice.iclass30.com/base/register/checkPass',
        'findShareResourceList': 'service.iclass30.com/resource/share/findShareResourceList',
        'getSubjectListByPhase_2': 'service.iclass30.com/userMgr/basesubject/getSubjectListByPhase',
        'findShareCourseWaresList': 'service.iclass30.com/resource/share/findShareCourseWaresList',
        'getHistoryStuHomeWorkList': 'homeworkservice.iclass30.com/homeworkstatic/analysis/getHistoryStuHomeWorkList',
        'getResourceDetails': 'service.iclass30.com/resource/resource/getDetails',
        'recordResViews': 'service.iclass30.com/online/common/recordResViews',
        'getScoreInfo': 'service.iclass30.com/online/courseWares/getScoreInfo',
        'getLoginUrl': 'service.iclass30.com/thirdpartyinterface/newtencentliveroom/getLoginUrl',
        'getSubject': 'service.iclass30.com/userMgr/basesubject/getSubject',
        'studentClassList': 'service.iclass30.com/thirdpartyinterface/newtencentliveroom/studentClassList',
        'getResourceList': 'service.iclass30.com/resource/center/getResourceList',
        'classList': 'service.iclass30.com/userMgr/baseclass/classList',
        'getGradeClassList': 'service.iclass30.com/userMgr/baseclass/getGradeClassList',
        'studentList': 'service.iclass30.com/userMgr/baselogin/studentList',
        'getGradeListByGroupClassId': 'service.iclass30.com/userMgr/basegrade/getGradeClassList',
        'getSubstitudeList': 'service.iclass30.com/userMgr/baseSubstitude/getSubstitudeList'
    }

    def __init__(self, arg1, arg2):
        if len(arg2) > 16:
            self.user.details["id"] = arg1
            self.user.details["token"] = arg2
        else:
            self.login(arg1, arg2)

    def __getattr__(self, uri):
        return lambda arg: self.get(self.INDEX[uri], params=arg)

    def makeHeaders(self, url):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Access-Control-Allow-Origin": "*",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            "X-Requested-Width": "XMLHttpRequest",
            "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "token": "null"
        }
        headers["Host"] = url.split("/")[0]
        headers["Origin"] = "https://" + url.split("/")[0]
        headers["Referer"] = "https://" + url.split("/")[0]
        if self.user.token:
            headers["token"] = self.user.token
        return headers
    
    def get(self, url, params=...):
        headers = self.makeHeaders(url)
        r = requests.get("https://"+url, headers=headers, params=params)
        data = json.loads(r.text)
        return data["data"] if data["code"] == 1 else data
    
    def post(self, url, data=...):
        headers = self.makeHeaders(url)
        r = requests.post("https://"+url, headers=headers, data=data)
        rsp = json.loads(r.text)
        return rsp["data"] if rsp["code"] == 1 else rsp["msg"]
    
    def login(self, account, password):
        req = self.post("service.iclass30.com/base/baselogin/login",
                data={"account": account, 
                      "passWord": password, 
                      "userType": "", 
                      "logintype": 22, 
                      "terminalType": "web"})
        self.user.details = req


class Reader:
    """这是一个由上帝开发的史山，请不要动它，请使用Reader.tackle来调用"""
    def __init__(self,demand=None):
        self.demand = demand

    def tackle(self, data:dict, demand=None, strict=True, greedy=False):
        """你可以这样做：
        reader = Reader()
        reader.tackle(data, demand)
        也可以：
        reader = Reader(demand)
        reader.tackle(data)
        这会查找data字典下所有的键（包括子字典），如果键存在于demand中，键值对将会被返回
        严格模式下，只有一个字典中包含demand中的所有键，它才会被返回
        贪婪模式下，只要字典中包含demand中的任一键，整个字典都会被返回"""
        cache = []
        _cache = {}
        _greedy = greedy
        if not demand:
            demand = self.demand
        for key, value in data.items():
            if key in demand:
                if _greedy:
                    cache.append(data)
                    _greedy = False
                else:
                    _cache[key] = value
            if isinstance(value, dict):
                cache.extend(self.tackle(value, demand, strict, greedy))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        cache.extend(self.tackle(item, demand, strict, greedy))
        if _cache:
            if strict:
                kl = list(_cache.keys())
                if all(key in kl for key in demand):
                    cache.append(_cache)
            else:
                cache.append(_cache)
        return cache

class IC30(iclass30):
    ARG_INDEX={
    'getLoginUserInfo': ['userId', 'optUserId', 'optRealName', 'regionId', 'serviceVersion'],
    'getUserRoleIdList': ['userId', 'optUserId', 'optRealName', 'regionId'],
    'getCommonCatchListByAppTypes': ['uId', 'appTypes', 'optUserId', 'optRealName', 'regionId'],
    'getAppMenuByUser': ['userId', 'adminType', 'userType', 'optUserId', 'optRealName', 'regionId'],
    'getUserInfo': ['userId', 'serviceVersion'],
    'getPublicConfigBySchoolInfo': ['dictCode', 'userId', 'serviceVersion'],
    'getLoginUserInfo': ['userId', 'serviceVersion', 'schoolId'],
    'getStuWorkList': ['schoolId', 'userId', 'firstType', 'page', 'limit', 'hwType', 'type', 'subjectId', 'serviceVersion'],
    'getUserInfo': ['userId', 'serviceVersion', 'schoolId'],
    'getSchoolYearList': ['schoolId', 'phase', 'serviceVersion'],
    'checkPass': ['serviceVersion', 'schoolId'],
    'getStuWorkList': ['schoolId', 'userId', 'firstType', 'page', 'limit', 'hwType', 'type', 'subjectId', 'serviceVersion'],
    'getLoginUserInfo': ['userId', 'optUserId', 'optRealName', 'regionId'],
    'getPublicConfigBySchoolInfo': ['schoolId', 'dictCode', 'userId', 'optUserId', 'optRealName', 'regionId'],
    'findShareResourceList': ['keyWord', 'schoolId', 'loginId', 'subjectId', 'type', 'page', 'limit', 'optUserId', 'optRealName', 'regionId'],
    'getSubjectListByPhase': ['phase', 'optUserId', 'optRealName', 'regionId'],
    'findShareCourseWaresList': ['wd', 'loginId', 'schoolId', 'subjectId', 'type', 'page', 'limit', 'optUserId', 'optRealName', 'regionId'],
    'getStuWorkList': ['schoolId', 'userId', 'firstType', 'page', 'limit', 'hwType', 'type', 'subjectId', 'serviceVersion'],
    'getHistoryStuHomeWorkList': ['schoolId', 'userId', 'firstType', 'page', 'limit', 'hwType', 'hwTypeCode', 'subjectId', 'startTime', 'endTime', 'type', 'serviceVersion'],
    'getDetails': ['id', 'optUserId', 'optRealName', 'regionId'],
    'recordResViews': ['userId', 'resId', 'resType', 'optUserId', 'optRealName', 'regionId'],
    'getScoreInfo': ['userId', 'shareId', 'optUserId', 'optRealName', 'regionId'],
    'getLoginUrl': ['schoolId', 'userId', 'userType'],
    'getSubject': ['schoolId'],
    'studentClassList': ['schoolId', 'userId', 'keyWord', 'subjectId', 'status', 'page', 'limit'],
    'getGradeClassList': ['schoolId', 'year', 'systemCode', 'optUserId', 'optRealName', 'regionId'],
    'studentList': ['schoolId', 'year', 'classId', 'className', 'classType', 'keyWord', 'systemCode', 'cId', 'page', 'limit', 'optUserId', 'optRealName', 'regionId'],
    'getGradeListByGroupClassId': ['schoolId', 'optUserId', 'optRealName', 'regionId'],
    'getSubstitudeList': ['schoolId', 'classId', 'optUserId', 'optRealName', 'keyWord', 'page', 'limit'],
    }
    def __init__(self, arg):
        if isinstance(arg, list):
            super().__init__(arg[0], arg[1])
        elif isinstance(arg, iclass30):
            super().__init__(arg.user.details["id"], arg.user.details["token"])
            self.user.details = self.getLoginUserInfo({"userId": self.user.details["id"], "serviceVersion": "13.0"})
        elif isinstance(arg, dict):
            self.arg = arg
            if "token" in arg.keys():
                super().__init__(arg["id"], arg["token"])
