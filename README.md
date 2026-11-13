# 养乐多的源

自用的 AltStore / SideStore / LiveContainer 软件源，收录需要的开源 iOS 应用，跟随上游 GitHub Release 更新。

## 添加到手机

**LiveContainer**：底部 `源` → 右上角 `+` → 粘贴下面的地址 → 确认。

**SideStore / AltStore**：`Sources（源）` → 右上角 `+` → 粘贴同一地址。

```
https://raw.githubusercontent.com/Yakult00/ios-source/main/apps.json
```

也可以用一键链接（在手机上点开）：

```
livecontainer://source?url=https%3A%2F%2Fraw.githubusercontent.com%2FYakult00%2Fios-source%2Fmain%2Fapps.json
```

> 注意：`raw.githubusercontent.com` 在大陆有时很慢或打不开。如果加不上，可以把 `apps.json` 部署到国内能访问的地方（比如自己的服务器、cnb.cool），再把地址换成那个。

## 已收录

| 应用 | 版本 | 上游 |
|---|---|---|
| GestaltX | 1.0.7 | [huamidev/GestaltX](https://github.com/huamidev/GestaltX) |
| WQ Files | 0.9.5 | [kolbicz/WQFiles](https://github.com/kolbicz/WQFiles) |
| AirCard | 1.3.2 | [Mak5er/AirCard-iOS](https://github.com/Mak5er/AirCard-iOS) |
| iPadn | 2.0.0 | [mengangs/ipadn](https://github.com/mengangs/ipadn) |

## 加新应用

1. 在 `repos.json` 里加一行，例如：
   ```json
   {"repo": "作者/仓库名", "subtitle": "一句话介绍"}
   ```
2. 跑 `python3 tools/update.py`，它会自动抓最新 Release 里的 `.ipa`，读出包名、版本、最低系统版本，更新 `apps.json`。
3. 提交推送，手机上刷新源就能看到。

要求：上游仓库的 Release 里要有 `.ipa` 文件。
