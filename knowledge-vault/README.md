# Knowledge Vault

這裡是 `knowledge` 工作線的安全落檔區。

## 原則

1. 只允許由 `knowledge` 線在 `safe-run` 模式寫入。
2. 只允許寫入此 repo 內部，不外連、不覆寫 repo 外部路徑。
3. 預設目標資料夾為 `Inbox/`。

## 建議用法

在 Issue 或 Actions 的 `details` 裡加入：

```md
### 目標資料夾
Inbox

### 預期輸出
輸出整理後大綱

### 風險邊界
不要覆寫原始內容
```
