# UJShealthChecker-UJS健康打卡助手
![GitHub](https://img.shields.io/github/license/iconteral/UJShealthChecker)
### 描述
专为江苏大学建康打卡系统设计的自动化打卡工具，目前处于早期开发~~（弃坑）~~阶段
其功能包括
- [x] 每天定时自动打卡
- [x] 微信推送打卡结果
- [ ] ~~自动获得位置信息~~
- [ ] ~~自动获得体温~~

### 使用方法
#### 安装依赖
```bash
pip install beautifulsoup4 requests
```

#### 配置
本工具的配置文件为```conf.ini```

| 项目 | 说明 | 取值 |
| ------------ | ------------ | ------------ |
| checkTime | 设定的签到时间| 0 - 23整数 |
| temperatureSource | 体温来源\* | randomNomral 随机生成正常体温；manual 人工设定；~~sensorSource 从温度传感器取得温度~~（暂不支持） |
| enableServerChan | 是否开启微信推送\*\* | Bool : False/True |
| serverChanKEY | Server酱 KEY | n/a |
| cloud_sessionID | Cookie : cloud_sessionID | n/a |

### 许可

![WTFPL](http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-1.png)

© 2020 WTFPL – Do What the Fuck You Want to Public License.