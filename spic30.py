import sqlite3, os, requests, json
import random, hashlib, datetime, mimetypes

class User:
    def __init__(self, details: dict):
        self.details = details
    def __getattr__(self, name):
        return self.details[name]

class ic30():
    def __init__(self, arg1, arg2):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        api_path = os.path.join(current_dir, 'api.db')
        self.db = sqlite3.connect(api_path)
        self.cursor = self.db.cursor()
        self.runAsWeb()
        if len(arg2) > 16:
            self.user = User({"id":arg1, "token":arg2})
        else:
            self.user = User({})
            self.user.details = self.login(-1, arg1, arg2, 22, "web")["data"]

    def __getattr__(self, name):
        self.cursor.execute('SELECT * FROM api WHERE method = "%s"' % name)
        url = self.cursor.fetchall()
        return lambda index=0, *args, **kwargs: self.get(url[index][1], kwargs if kwargs else dict(zip(url[index][2].split(','), args))) if index >= 0 else self.post(url[abs(index)-1][1], kwargs if kwargs else dict(zip(url[index][2].split(','), args)))

    def help(self, functuon):
        """查阅某个函数的帮助文档，支持%等SQL通配符"""
        self.cursor.execute('SELECT * FROM api WHERE method LIKE "%s"' % functuon)
        result = self.cursor.fetchall()
        if len(result) == 0:
            print('函数%s不存在' % functuon)
        else:
            print("函数%s有%d种重载形式" % (functuon, len(result)))
            print("分别对应URL：\n    %s" % "\n    ".join([i[1] for i in result]))
            print("参数分别如下：\n    %s" % "\n    ".join([i[2] for i in result]))
            print("请记住你所需方法的索引，通过ic30.%s(index,*paras)快速调用，index从0开始" % functuon)
            print("这会默认使用GET方法，如果要使用POST方法，请使用(-index-1)代替index")
    
    def loginById(self, uid):
        self.user.details = self.getLoginUserInfo(0, uid)["data"]
    
    def loginAsAdmin(self, index=0):
        """登录为校管理员身份"""
        adminIds = self.getSchoolById(0, self.user.schoolid)["data"]["adminIds"]
        adminId = adminIds.split(",")[index] if "," in adminIds else adminIds
        self.user.details = self.getLoginUserInfo(0, adminId, self.user.schoolid)["data"]

    def get(self, url, params={}):
        headers = self.makeHeaders(url)
        r = requests.get("https://"+url, headers=headers, params=params)
        data = json.loads(r.text)
        return data
    
    def post(self, url, data={}):
        headers = self.makeHeaders(url)
        r = requests.post("https://"+url, headers=headers, data=data)
        rsp = json.loads(r.text)
        return rsp

    def runAsLM(self):
        self.makeHeaders = self.makeHeadersForLM
    
    def runAsWeb(self):
        self.makeHeaders = self.makeHeadersForWeb
    
    def makeHeadersForWeb(self, url):
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
        if "token" in self.user.details.keys():
            headers["token"] = self.user.token
        return headers
    
    def makeHeadersForLM(self, url):
        headers = {
            'token': 'null',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'learningmachine.iclass30.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'okhttp/3.12.0'
        }
        if "token" in self.user.details.keys():
            headers["token"] = self.user.token
        return headers
    
    def uploadFile(self, filename):
        """上传文件，返回文件路径"""
        import base64
        with open(filename, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return self.post('xxq.iclass30.com/api/online/common/uploadBase64', data={"base64":data,"suffix":filename.split(".")[-1]})["data"]["uploadUrl"]
    
    def getLoginUserInfo(self, index=0, uid="", schoolid=""):
        return self.get("service.iclass30.com/base/baselogin/getLoginUserInfo", {"userId": uid, "schoolId": schoolid})["data"]
    
    def getSchoolById(self, index=0, schoolid=""):
        return self.get("service.iclass30.com/base/school/getSchoolById", {"schoolId": schoolid})["data"]
    
    def getSchoolStudentDataList(self, index=0, schoolid="", name="", mobile="", page=1, limit=10):
        return self.get("service.iclass30.com/base/school/getSchoolStudentDataList", {"schoolId": schoolid, "name": name, "mobile": mobile, "page": page, "limit": limit})["data"]


def loginFromId(uid):
    c = ic30("YS", "YuanShenQiDongYuanShenQiDong")
    c.loginById(uid)
    return c


class userIter:
    def __init__(self, userType, c30:ic30):
        self.c = c30
        self.userType = userType
    def __iter__(self):
        self.index = -1
        if self.userType == "stu":
            self.num = self.c.getSchoolStudentDataList(0, self.c.user.schoolid, "", "", 1, 1)["data"]["total_rows"]
            self.lst = self.c.getSchoolStudentDataList(0, self.c.user.schoolid, "", "", 1, self.num)["data"]["rows"]
        elif self.userType == "tea":
            self.num = self.c.getSchoolTeacherDataList(0, self.c.user.schoolid, "", "", 1, 1)["data"]["total_rows"]
            self.lst = self.c.getSchoolTeacherDataList(0, self.c.user.schoolid, "", "", 1, self.num)["data"]["rows"]
        elif self.userType == "adm":
            self.lst = self.c.getSchoolById(0, self.c.user.schoolid)["data"]["adminIds"].split(",")
            self.num = len(self.lst)
        return self

    def __next__(self):
        if self.index + 2 < self.num:
            self.index += 1
            return self.lst[self.index]
        else:
            raise StopIteration

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


class OSS:
    def __init__(self, c30:ic30, path):
        """path应该是指向文件的字符串，而不是指向目录，如果你打算遵守c30规范，它应该以/f.xxx结尾"""
        self.c30 = c30
        self.signature(path)
    
    def signature(self, path):
        url = "service.iclass30.com/common/oss/signature?path=%s&token=%s" % (path, self.c30.user.token)
        self.oss = self.c30.get(url)["data"]
    
    def upload(self, filename:str, rawdata:bytes, date:str="", filetype:str=""):
        """警告：filename是文件名，不是文件路径，你期望文件下载时使用什么名字，这里就应该填写什么。时间应该遵循的格式举例：1/30/2025, 08:13:06 AM，不填将使用当前时间。不填filetype将会根据filename后缀名推测类型，filetype使用mimetype格式如image/png"""
        url = "https://mk-basefiles.oss-cn-hangzhou.aliyuncs.com/"
        boundary = "---------------------------" + "".join([str(random.randint(0, 9)) for i in range(30)])
        headers = {
            "Host": "mk-basefile.oss-cn-hangzhou.aliyuncs.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "multipart/form-data; boundary=" + boundary[2:],
            "Origin": "https://console.iclass30.com",
            "Connection": "keep-alive",
            "Referer": "https://console.iclass30.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site"
        }
        filetype = filetype or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        data = f'{boundary}\r\nContent-Disposition: form-data; name="OSSAccessKeyId"\r\n\r\n{self.oss["accessid"]}\r\n\
{boundary}\r\nContent-Disposition: form-data; name="policy"\r\n\r\n{self.oss["policy"]}\r\n\
{boundary}\r\nContent-Disposition: form-data; name="signature"\r\n\r\n{self.oss["signature"]}\r\n\
{boundary}\r\nContent-Disposition: form-data; name="key"\r\n\r\n{self.oss["dir"]}\r\n\
{boundary}\r\nContent-Disposition: form-data; name="Content-Disposition"\r\n\r\nattachment;filename={filename}\r\n\
{boundary}\r\nContent-Disposition: form-data; name="id"\r\n\r\nWU_FILE_0\r\n\
{boundary}\r\nContent-Disposition: form-data; name="name"\r\n\r\n{filename}\r\n\
{boundary}\r\nContent-Disposition: form-data; name="type"\r\n\r\n{filetype}\r\n\
{boundary}\r\nContent-Disposition: form-data; name="lastModifiedDate"\r\n\r\n{date or datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S %p")}\r\n\
{boundary}\r\nContent-Disposition: form-data; name="size"\r\n\r\n{len(rawdata)}\r\n\
{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: {filetype}\r\n\r\n'
        data = data.encode("utf-8") + rawdata
        data = data + (f'\r\n{boundary}--\r\n').encode("utf-8")
        r = requests.post(url, headers=headers, data=data)
        return r.status_code,r.text,r.headers
    
    def insertResource(self, filename, rawdata, filetype=""):
        url = "service.iclass30.com/resource/center/batchInsertResource"
        md5 = hashlib.md5()
        md5.update(rawdata)
        md5 = md5.hexdigest()
        data = {
            "schoolId": self.c30.user.schoolid,
            "userId": self.c30.user.id,
            "files": json.dumps([
                {
                    "title": ".".join(filename.split(".")[:-1]),
                    "url": self.oss["dir"],
                    "size": len(rawdata),
                    "ext": filename.split(".")[-1],
                    "fileType": filetype or mimetypes.guess_type(filename)[0] or "application/octet-stream",
                    "md5": md5
                }
            ]),
            "appType": 0,
            "gradeId": "",
            "gradeCode":"",
            "gradeName": "",
            "subjectId": "",
            "subjectCode": "",
            "subjectName": "",
            "isRename": 0,
            "parentId": 0,
            "optUserId": self.c30.user.id,
            "optUserName": self.c30.user.realname,
            "regionId": ""
        }
        return self.c30.post(url, data)
