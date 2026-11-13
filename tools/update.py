#!/usr/bin/env python3
"""从上游 GitHub Release 刷新 apps.json。

用法：
    python3 tools/update.py

配置在 repos.json 里：每加一个项目就加一行 {"repo": "owner/name"}，
再跑一遍这个脚本，apps.json 就会自动跟到最新版。
脚本会下载 IPA 读出包名 / 版本 / 最低系统版本，所以不用手填。
"""
import json
import plistlib
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPOS_FILE = ROOT / "repos.json"
OUT_FILE = ROOT / "apps.json"


def gh(path):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "ios-source-updater"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def ipa_info(url):
    """下载 IPA，读出 Info.plist 里的关键字段。"""
    with tempfile.NamedTemporaryFile(suffix=".ipa", delete=False) as f:
        with urllib.request.urlopen(url, timeout=120) as r:
            f.write(r.read())
        tmp = f.name
    with zipfile.ZipFile(tmp) as z:
        candidates = [n for n in z.namelist()
                      if n.startswith("Payload/") and n.count("/") == 2
                      and n.endswith(".app/Info.plist")]
        if not candidates:
            raise RuntimeError("IPA 里找不到 Info.plist")
        pl = plistlib.loads(z.read(candidates[0]))
    return {
        "bundleIdentifier": pl["CFBundleIdentifier"],
        "version": pl.get("CFBundleShortVersionString", ""),
        "buildVersion": pl.get("CFBundleVersion", ""),
        "name": pl.get("CFBundleDisplayName") or pl.get("CFBundleName", ""),
        "minOSVersion": pl.get("MinimumOSVersion", ""),
    }


def build_app(cfg):
    owner_repo = cfg["repo"]
    print(f"== {owner_repo}")
    rel = gh(f"/repos/{owner_repo}/releases/latest")
    ipa_assets = [a for a in rel.get("assets", [])
                  if a["name"].lower().endswith(".ipa")]
    include = cfg.get("asset_include", "")
    exclude = cfg.get("asset_exclude", "")
    if include:
        ipa_assets = [a for a in ipa_assets if include in a["name"]]
    if exclude:
        ipa_assets = [a for a in ipa_assets if exclude not in a["name"]]
    if not ipa_assets:
        raise RuntimeError(f"{owner_repo} 的最新 Release 里没有符合条件的 .ipa")
    asset = ipa_assets[0]
    print(f"   最新版 {rel['tag_name']}，{asset['name']} ({asset['size']} bytes)")
    info = ipa_info(asset["browser_download_url"])
    desc = (rel.get("body") or "").strip()
    version_entry = {
        "version": info["version"] or rel["tag_name"].lstrip("v"),
        "date": rel["published_at"][:10],
        "publishedAt": rel["published_at"],
        "buildVersion": info["buildVersion"],
        "downloadURL": asset["browser_download_url"],
        "size": asset["size"],
        "minOSVersion": info["minOSVersion"],
        "localizedDescription": desc[:2000],
    }
    app = {
        "name": cfg.get("name") or info["name"],
        "bundleIdentifier": info["bundleIdentifier"],
        "developerName": cfg.get("developerName") or owner_repo.split("/")[0],
        "subtitle": cfg.get("subtitle", ""),
        "localizedDescription": cfg.get("description", desc[:2000]),
        "iconURL": cfg.get("iconURL", ""),
        "tintColor": cfg.get("tintColor", "#0A84FF"),
        "category": cfg.get("category", "utilities"),
        "appPermissions": {"entitlements": [], "privacy": {}},
        "version": version_entry["version"],
        "versionDate": version_entry["date"],
        "versionDescription": desc[:2000],
        "downloadURL": version_entry["downloadURL"],
        "size": version_entry["size"],
        "minOSVersion": version_entry["minOSVersion"],
        "versions": [version_entry],
        "releaseChannels": [{"track": "stable", "releases": [version_entry]}],
    }
    # 图标：没填就用 jsDelivr 读仓库里的 AppIcon（有就用，没有就留空）
    if not app["iconURL"]:
        app["iconURL"] = ""
    return app


def main():
    repos = json.loads(REPOS_FILE.read_text())
    apps = [build_app(cfg) for cfg in repos]
    apps.sort(key=lambda a: a["name"].lower())
    existing = {}
    if OUT_FILE.exists():
        existing = json.loads(OUT_FILE.read_text())
    source = {
        "name": existing.get("name", "养乐多的源"),
        "identifier": existing.get("identifier", "dev.yakult00.source"),
        "subtitle": existing.get("subtitle", "自己收录的 iOS 应用"),
        "description": existing.get(
            "description",
            "自用的 AltStore / SideStore / LiveContainer 软件源，收录需要的开源 iOS 应用，跟随上游 GitHub Release 更新。"),
        "iconURL": existing.get("iconURL", "https://github.com/Yakult00.png"),
        "website": existing.get("website", "https://github.com/Yakult00/ios-source"),
        "apps": apps,
    }
    OUT_FILE.write_text(json.dumps(source, ensure_ascii=False, indent=2) + "\n")
    print(f"\n已写入 {OUT_FILE}，共 {len(apps)} 个应用")
    # 清一下 jsDelivr 的缓存，让手机上能尽快刷到新内容（失败也不影响）
    try:
        req = urllib.request.Request(
            "https://purge.jsdelivr.net/gh/Yakult00/ios-source@main/apps.json",
            headers={"User-Agent": "ios-source-updater"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            print("jsDelivr 缓存已清：", r.status)
    except Exception as e:
        print("jsDelivr 清缓存失败（可忽略）：", e)


if __name__ == "__main__":
    sys.exit(main())
