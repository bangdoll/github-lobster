# GitHub Lobster

這是一個專門拿來「在 GitHub 養龍蝦」的最小可用專案。

核心目標只有三件事：

1. 用 GitHub 收件
2. 用白名單做任務分流
3. 用執行摘要與任務包保留每次任務痕跡

## 專案結構

```text
.github/
  ISSUE_TEMPLATE/
  workflows/

01.Docs/
  github-lobster-playbook.md
  GitHub_Lobster_快速上手教學.md
  Telegram_指揮_GitHub_Lobster_教學.md

lobster/
  inbox/
  runs/
  registry.json

scripts/
  lobster_router.py
```

## 快速開始

1. 到 GitHub Actions 執行 `Lobster Task Router`
2. 填入任務名稱 `mission`
3. 選擇工作線 `lane`
4. 先用 `dry-run` 驗證分流是否正確
5. 到 `lobster/runs/` 查看 `summary.md`、`packet.md`
6. 若要讓 `knowledge` 線真正寫入，使用 `safe-run` 並設 `LOBSTER_ALLOW_LOCAL_EXECUTION=1`

教學入口在 [GitHub_Lobster_快速上手教學.md](/Users/aios/Projects/00.AI-Notes_Local/github-lobster/01.Docs/GitHub_Lobster_快速上手教學.md)。
Telegram 橋接教學在 [Telegram_指揮_GitHub_Lobster_教學.md](/Users/aios/Projects/00.AI-Notes_Local/github-lobster/01.Docs/Telegram_指揮_GitHub_Lobster_教學.md)。

## 自動排程

目前已設定自動排程：

1. 每天 `00:00 UTC`
2. 對應台灣時間是每天 `08:00`（UTC+8）
3. 預設任務是 `research + dry-run`
4. 任務名稱是 `每日 AI 趨勢晨報`
5. 內容來源之一固定包含：
   `https://ai-digest.liziran.com`
   `https://ai-brief.liziran.com/zh/`

## 預設工作線

1. `research`：產出研究任務包
2. `knowledge`：產出知識整理包
3. `publish`：產出發布準備包
4. `ops`：產出運維巡檢包

## Knowledge 線安全寫入

`knowledge` 線現在可以把整理後筆記安全寫到 [knowledge-vault/README.md](/Users/aios/Projects/00.AI-Notes_Local/github-lobster/knowledge-vault/README.md) 所描述的區域。

建議在 `details` 裡補這些欄位：

```md
### 目標資料夾
Inbox

### 預期輸出
輸出整理後大綱

### 風險邊界
不要覆寫原始內容
```

## 安全原則

1. 預設只做 `dry-run`
2. 只有白名單工作線可以進入 `safe-run`
3. 執行結果會寫入 `lobster/runs/`
