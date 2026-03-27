# GitHub 養龍蝦藍圖

## 定位

這個 repo 只做一件事：把 GitHub 變成龍蝦的養殖箱。

GitHub 負責：

1. 收件
2. 觸發工作流
3. 保存 Artifact
4. 留下任務軌跡

龍蝦控制層負責：

1. 任務白名單
2. 任務分流
3. 安全模式
4. 執行摘要

## 最小可用流程

1. 用 Issue 或 Actions 建立任務
2. `scripts/lobster_router.py` 解析任務
3. 依 `lane` 分流到對應工作線
4. 產出 `summary.json` 與 `summary.md`
5. 上傳成 GitHub Artifact 或回寫到 Issue

## 先從哪些任務開始

1. 研究摘要
2. 知識整理
3. 發布前檢查
4. 日常巡檢

## 不建議一開始就做的事

1. 自動刪除檔案
2. 直接推正式發布
3. 無白名單的任意命令執行

## 下一步

等這個 starter 穩定後，再逐步接：

1. 真正的內容生產腳本
2. Obsidian 同步
3. 發布工作流
