# IClass30

这个项目旨在提供C30 API的快捷实现，项目内封装了常用的C30 API，方便用户快速调用。

## iclass30
大多数功能的基类，兼具快速调用和易于扩展的特点

### iclass30(arg1, arg2)
该方法有两种重载形式，分别为
```python
c = iclass30(account, password)
c = iclass30(userId, token)
```
前者主要应用于初始启动，需要获取用户id和token以进行下一步API调用，后者主要应用于获取用户id列表但未知token时的批量调用。

### iclass30.apiName(params)
这是API的快捷调用方法，它将自动将参数封装为字典，然后调用apiName方法，例如：
```python
c.get("service.iclass30.com/userMgr/baselogin/getLoginUserInfo", {"serviceVersion": "13.0", "userId": c.user.id})
```
这等价于：
```python
c.getLoginUserInfo({"serviceVersion": "13.0", "userId": c.user.id})
```

### iclass30.get(url, params)/iclass30.post(url, data)
当你使用不常用API时，你可能会用到此方法，其中url为API的路径，params为GET请求的参数，data为POST请求的内容。  
请求时，请求头已经被自动生成，生成来源是你先前登录的账号或填入的信息，请注意，url参数内不要填入请求协议https://，例如：
```python
c.get("service.iclass30.com/xxx", params={"xxx": "xxx"})  # 正确
c.get("https://service.iclass30.com/xxx", params={"xxx": "xxx"})  # 错误
```
返回值已经经过处理，若请求成功，返回值为原始响应中的data字段，若请求失败，返回值为原始响应中的msg字段，这通常可以指明错误的原因。

### iclass30.makeHeaders(url)
通常而言，你不需要用到此方法，除非你需要在别的地方快速生成请求头，比如进行调试，你可以：
```python
c.makeHeaders("service.iclass30.com/xxx")
```
url参数内，你仍然不能填入请求协议https://

### iclass30.user
这是当前登录用户的封装，类型是User，你可以通过这些方式直接获取用户信息：
```python
c.user.id
c.user.realname
c.user.token
```
很遗憾的是，如果你采用了第二种重载形式，直接提供userId和token，此时你将只拥有id和token两条属性，你可以这样覆盖它以获得更多信息：
```python
c.user.details = c.get("service.iclass30.com/userMgr/baselogin/getLoginUserInfo",{"userId": c.user.id, "serviceVersion": "13.0"})
```
或是使用简化写法：
```python
c.user.details = c.getLoginUserInfo({"userId": c.user.id, "serviceVersion": "13.0"})
```
在后面，这条语句还会更加精简。


## Reader
这个类旨在帮助你快速提取响应数据的核心内容，它的核心是Reader.tackle方法，你可以这样构造：
```python
r = Reader()  #处理数据时填写需求
r = Reader(damand)  #立即填写需求
```

### Reader.tackle(data, damand, strict, greedy)
data参数接受一个字典作为待处理数据，tackle会遍历整个字典  
demand参数接受一个列表作为需求，当遍历到字典的某个键时，若该键在demand中，则该键会被返回  
strict参数表示是否严格匹配，若为True，则demand中的每一个元素都必须包含在data的键中，否则不会被返回，默认为True
greedy参数表示是否贪婪匹配，若为True，则只要某个字典的键中出现了demand中的任意一个元素，整个子字典就会被返回，否则只会返回demand中包含的键，默认为False  
返回值为一个列表，列表中的每一个元素为一个字典，其中包含了所有匹配项，并且总是包含尽可能多的匹配项
### 如何使用
这是一个示例字典：
```python
test = {
    "name": "张三",
    "age": 30,
    "address": {
        "city": "北京",
        "street": "朝阳路",
        "building": {
            "text": "阳光大厦",
            "floors": 20
        }
    },
    "hobbies": [
        {"name": "阅读", "frequency": "每天", "since": "2010"},
        {"name": "游泳", "frequency": "每周一次"}
    ]
}
```
首先，你应该创建一个Reader对象：`r = Reader()`  
如果你想要获取他所有的hobbies名字，你可以这样：`r.tackle(test, ["name"])`  
返回值：`[{"name": "阅读"}, {"name": "游泳"}]`  
如果你不仅希望获取名字，还希望获取所有有关信息，你可以这样：`r.tackle(test, ["name"], greedy=True)`  
返回值：`[{"name": "阅读", "frequency": "每天", "since": "2010"}, {"name": "游泳", "frequency": "每周一次"}]`  
如果你只想获取hobbies名字和since，但有无since无关紧要，你可以这样：`r.tackle(test, ["name", "since"], strict=False)`  
返回值：`[{"name": "阅读", "since": "2010"}, {"name": "游泳"}]`


## IC30
### ！该模块尚在开发中 ！
这是一个简化到极点的类，构造时，你可以填入任何可以证明身份的信息，比如
```python
c = IC30([userId, token])
c = IC30([account, password])
c = IC30(c) #c是一个iclass30对象
```
你可以传入一个字典，字典内的所有信息都会被自动记录


## 对比
### 使用了iclass30后的简化代码，如何从头获取全校用户信息
```python
from iclass30 import *
c = iclass30("教师账号", "对应密码")
r = Reader()
data = r.tackle(c.getGradeListByGroupClassId({"regionId": "", "optUserId": "optRealName": c.user.realname, "schoolId": c.user.schoolId}), ["year", "system_code"])
for i in data:
    dat = r.tackle(c.getGradeClassList({"regionId": "", "optUserId": c.user.id, "optRealName": c.user.realname, "schoolId": c.user.schoolId, "year": i["year"], "systemCode": i["system_code"]}), ["id", "class_name"])
    for j in dat:
        da = r.tackle(c.studentList({"schoolId": c.user.schoolId, "year": i["year"], "systemCode": i["system_code"], "classId": j["id"], "className": j["class_name"], "classType": "3", "keyWord":"", "cid":"", "page":"1", "optUserId": c.user.id, "optRealName": c.user.realname, "regionId": ""}),["id", "user_name", "realname"],True,True)
        for k in da:
            print(k)
```
