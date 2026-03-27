# GitHub Lobster 快速上手教學

這份文件是給第一次使用 `github-lobster` 的人看的實作教學。目標不是講架構，而是讓你 10 分鐘內真的跑出第一隻龍蝦任務。

## 你會學到什麼

1. 怎麼用 GitHub Actions 派一個龍蝦任務
2. 怎麼看任務摘要與任務包
3. 怎麼讓 `knowledge` 線安全寫入知識區
4. 怎麼避免一開始就把龍蝦養歪

## 先理解 3 個核心概念

### 1. `lane`

`lane` 就是工作線，也就是這次任務要交給哪一種龍蝦處理。

目前有 4 條：

1. `research`
研究線，適合整理趨勢、蒐集資料、產出摘要。
2. `knowledge`
知識線，適合整理筆記、歸檔內容、寫入知識區。
3. `publish`
發布線，適合做發布前檢查與整理。
4. `ops`
運維線，適合做巡檢、日常報告、交班摘要。

### 2. `dry-run`

`dry-run` 是演習模式。

它會：

1. 接收任務
2. 判斷工作線
3. 產出任務摘要
4. 產出任務包

但它不會真的動手寫入或執行外部動作。

### 3. `safe-run`

`safe-run` 是受控執行模式。

目前這個 repo 只有 `knowledge` 線支援真正安全寫入，而且還要同時滿足：

1. 任務模式是 `safe-run`
2. 環境變數 `LOBSTER_ALLOW_LOCAL_EXECUTION=1`

## 方法一：用 GitHub Actions 直接派工

這是最推薦的新手入口。

### 步驟

1. 打開 repo 的 `Actions`
2. 選 `Lobster Task Router`
3. 點 `Run workflow`
4. 填入 `mission`
5. 選 `lane`
6. 模式先選 `dry-run`
7. 送出工作流

### 範例

如果你要先測試研究線，可以這樣填：

- `mission`：整理本週 AI 趨勢
- `lane`：`research`
- `mode`：`dry-run`
- `details`：輸出五點摘要與三條後續建議

## 方法二：用 Issue 收件

如果你想讓團隊成員都能丟任務給龍蝦，Issue 模式會比較方便。

### 步驟

1. 到 `Issues`
2. 建立 `龍蝦任務`
3. 填寫表單
4. 建立 Issue

只要這張 Issue 帶有 `lobster` 標籤，workflow 就會接手處理。

## 任務跑完之後要看哪裡

每次任務會留下兩組主要成果。

### 1. `lobster/runs/<run_id>/summary.md`

這是任務摘要，適合快速看：

1. 任務名稱
2. 工作線
3. 執行模式
4. 驗證 Log
5. 執行結果

### 2. `lobster/runs/<run_id>/packet.md`

這是任務包，適合真的拿去做事。

內容通常會有：

1. 任務定位
2. 補充說明
3. 預期輸出
4. 風險邊界
5. 執行清單
6. 建議下一步

## 教學實戰 1：先跑一個研究任務

這是最無痛的入門方式。

### 建議輸入

- `mission`：整理本週 AI 趨勢
- `lane`：`research`
- `mode`：`dry-run`
- `details`：請整理 5 點摘要、3 個風險、3 個下一步

### 你會得到什麼

龍蝦會產出一份研究任務包，內容會把這次研究拆成：

1. 問題定義
2. 蒐集方向
3. 輸出要求
4. 下一步建議

這很適合拿去交給真人、子代理人，或未來接真正的資料抓取器。

## 教學實戰 2：讓知識線真的寫入

這是目前最像「真的在工作」的一條線。

### 你要準備的內容

在 `details` 裡建議寫成這樣：

```md
### 目標資料夾
Inbox

### 預期輸出
輸出整理後大綱

### 風險邊界
不要覆寫原始內容
```

### 執行條件

要讓這條線真正寫入，必須用：

1. `lane=knowledge`
2. `mode=safe-run`
3. `LOBSTER_ALLOW_LOCAL_EXECUTION=1`

### 成功後會發生什麼

系統會把整理後的內容寫到：

`knowledge-vault/<你的目標資料夾>/`

例如：

`knowledge-vault/Inbox/20260327T063807899780Z-整理-Obsidian-筆記結構.md`

## 建議養法

如果你是第一次養龍蝦，建議順序如下：

1. 先從 `research + dry-run` 開始
2. 再用 `knowledge + dry-run` 熟悉任務包格式
3. 確認流程穩定後，再開 `knowledge + safe-run`
4. 最後才考慮接真正的發布或外部系統

## 常見錯誤

### 1. 一開始就想讓龍蝦直接發布

這很容易把風險放太大。建議先讓它做摘要、整理、檢查。

### 2. 任務描述太空泛

不要只寫「幫我整理一下」。

比較好的寫法是：

1. 整理什麼
2. 要輸出成什麼
3. 不能做什麼

### 3. 直接給任意命令執行權

目前這個 repo 的設計原則就是白名單工作線，先不要破壞它。

## 你現在最值得做的第一個測試

如果你要我給一個最實用的新手測試，我會推薦這個：

### 任務

- `mission`：整理今天的 AI 學習筆記
- `lane`：`knowledge`
- `mode`：`dry-run`

### details

```md
### 目標資料夾
Inbox

### 預期輸出
輸出整理後大綱與後續待辦

### 風險邊界
不要覆寫原始內容
```

這樣你可以先看到任務包長什麼樣，再決定要不要切到 `safe-run`。

## 延伸閱讀

1. [github-lobster-playbook.md](/Users/aios/Projects/00.AI-Notes_Local/github-lobster/01.Docs/github-lobster-playbook.md)
2. [knowledge-vault/README.md](/Users/aios/Projects/00.AI-Notes_Local/github-lobster/knowledge-vault/README.md)
3. [README.md](/Users/aios/Projects/00.AI-Notes_Local/github-lobster/README.md)
