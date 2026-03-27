# Telegram 指揮 GitHub Lobster 教學

這份教學是 `Telegram Bot -> GitHub Actions` 的最小可用版本。

目標很簡單：

1. 你在 Telegram 傳指令
2. 本地橋接器收到訊息
3. 橋接器呼叫 GitHub workflow_dispatch
4. `github-lobster` 開始執行任務

## 架構

```text
Telegram
  -> telegram_bridge.py
  -> GitHub Actions: Lobster Task Router
  -> github-lobster workflow
```

## 需要的環境變數

1. `TELEGRAM_BOT_TOKEN`
Telegram Bot Token
2. `TELEGRAM_ALLOWED_CHAT_IDS`
允許下指令的 chat id，支援逗號分隔
3. `GITHUB_TOKEN`
可呼叫 GitHub Actions workflow dispatch 的 token
4. `GITHUB_REPO`
預設是 `bangdoll/github-lobster`
5. `GITHUB_WORKFLOW`
預設是 `Lobster Task Router`
6. `LOBSTER_TELEGRAM_DEFAULT_MODE`
預設是 `dry-run`

## 支援指令

1. `/research <任務內容>`
2. `/knowledge <任務內容>`
3. `/publish <任務內容>`
4. `/ops <任務內容>`
5. `/status`
6. `/help`

## 範例

### 研究線

```text
/research 今天 AI 論文簡報重點
```

### 知識線

```text
/knowledge 整理今天學到的 AI 筆記
```

### 查最近一次執行狀態

```text
/status
```

## 啟動方式

在 repo 根目錄執行：

```bash
export TELEGRAM_BOT_TOKEN="你的 bot token"
export TELEGRAM_ALLOWED_CHAT_IDS="你的 chat id"
export GITHUB_TOKEN="你的 github token"
export GITHUB_REPO="bangdoll/github-lobster"
python3 scripts/telegram_bridge.py
```

## 安全原則

1. 預設模式是 `dry-run`
2. 只有白名單 chat id 可派工
3. 知識線若要真正寫入，仍要由 workflow 那邊滿足 `safe-run` 條件
4. Telegram 入口只負責派工，不直接在本機執行高風險命令

## 產物

橋接器本地會寫一份 offset 狀態檔：

`runtime/telegram-bridge-state.json`

這個檔案只是記錄 Telegram 更新 offset，避免重複吃訊息。
