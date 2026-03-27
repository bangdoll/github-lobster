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

## 預設工作線

1. `research`：產出研究任務包
2. `knowledge`：產出知識整理包
3. `publish`：產出發布準備包
4. `ops`：產出運維巡檢包

## 安全原則

1. 預設只做 `dry-run`
2. 只有白名單工作線可以進入 `safe-run`
3. 執行結果會寫入 `lobster/runs/`
