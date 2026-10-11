# Cloud IP Troubleshooting

在雲端伺服器（OVH、DigitalOcean、AWS / GCP / Azure 等）執行時，YouTube 會封鎖 datacenter IP。本文件記錄已知問題與除錯路徑。

**建議做法：** 雲端上用 `--backend gemini`（需 `GEMINI_API_KEY`）。Gemini 由 Google 端抓影片轉錄，不經本機 IP，有無字幕都適用；`auto` 模式在本地路徑失敗時也會自動改走 Gemini。

## 問題總覽

| # | 問題 | 根因 | 狀態 |
|---|------|------|------|
| 1 | Bot 偵測：`Sign in to confirm you're not a bot` | YouTube 封鎖無 cookie 的雲端 IP | 已解決 — `YT_COOKIES` 環境變數 |
| 2 | JS runtime 警告：`No supported JavaScript runtime` | yt-dlp 需要 deno 解 n challenge | 已解決 — 安裝 deno |
| 3 | n challenge 失敗：`found 0 n function possibilities` | YouTube 對雲端 IP 回傳 TV player JS（`tv-player-ias.js`），該版本不含標準 n function | **未解決** |
| 4 | `youtube-transcript-api` IP 封鎖：`RequestBlocked` | 雲端 IP 被完全封鎖，cookies 無法繞過 | **未解決** |
| 5 | 字幕下載 429：`HTTP Error 429: Too Many Requests` | 短時間內請求過多觸發 rate limit | 部分解決 — 需等待冷卻 |
| 6 | 無 cookies 時 PO token 也無法通過 bot 偵測 | bot 偵測發生在 player request 階段，早於 PO token 介入 | 繞道 — `--backend gemini` |

## 問題 1：Bot 偵測（已解決）

**症狀：**
```
ERROR: [youtube] ...: Sign in to confirm you're not a bot.
```

**解法：** 設定 `YT_COOKIES` 環境變數指向 Netscape 格式的 cookies 檔案。程式碼已在 `downloader.py` 和 `metadata.py` 中讀取此變數。

**注意事項：**
- Cookies 會被瀏覽器自動 rotate — 匯出後不要再用該瀏覽器瀏覽 YouTube
- 建議使用無痕模式登入 YouTube 後匯出 cookies

## 問題 2：JS Runtime（已解決）

**症狀：**
```
WARNING: [youtube] No supported JavaScript runtime could be found.
```

**解法：**
```bash
curl -fsSL https://deno.land/install.sh | sh
# 確認 ~/.deno/bin 在 PATH 中
```

## 問題 3：n Challenge 失敗（未解決）

**症狀：**
```
WARNING: [youtube] [jsc] Error solving n challenge request using "deno" provider:
  "found 0 n function possibilities"
```

**根因：** YouTube 對雲端 IP 回傳 `tv-player-ias.vflset/tv-player-ias.js`（TV 版 player），此版本不含標準 n function。所有 player client 變體（`web`, `mweb`, `web_creator`, `web_safari`）最終都使用同一個 TV player。

**已嘗試但無效的路徑：**

| 嘗試 | 結果 |
|------|------|
| 升級 yt-dlp 至最新版（2026.3.17） | 同樣失敗 |
| 安裝 yt-dlp nightly（git master） | 同樣失敗 |
| `yt-dlp-ejs==0.4.0`（匹配 yt-dlp 期望版本） | 同樣失敗 — TV player 本身不含 n function |
| `yt-dlp-ejs==0.8.0`（最新） | 版本不匹配警告 + 同樣失敗 |
| `--remote-components ejs:github` | 下載了 solver script 但 TV player 無 n function |
| `--extractor-args "youtube:player_client=web"` | YouTube 仍回傳 TV player |
| `--extractor-args "youtube:player_client=mweb"` | 同上 + 需要 PO Token |
| `--extractor-args "youtube:player_client=web_creator"` | 同上 |
| `--extractor-args "youtube:player_url=.../base.js"` 強制指定 web player URL | YouTube 忽略，仍回傳 TV player |
| `--extractor-args "youtube:player_skip=js"` | `The page needs to be reloaded` 錯誤 |
| 安裝 `curl_cffi` + `--impersonate chrome` | 無法繞過 TV player 問題 |

**可能的解決方向：**
- 使用住宅 IP 代理（residential proxy）（未驗證）
- 在本機（非雲端 IP）執行
- 改用 `--backend gemini`

## 問題 6：PO token 無法取代 cookies

`bgutil-ytdlp-pot-provider`（HTTP server 模式）+ deno 已能被 yt-dlp 偵測為可用 provider，但無 cookies 時仍在第一個 player request 回 `Sign in to confirm you're not a bot`。換到另一家 datacenter（DigitalOcean）出口結果相同。PO token 只有在 cookies 已通過 bot 偵測後才可能有用。

## 問題 4：youtube-transcript-api IP 封鎖（未解決）

**症狀：**
```
RequestBlocked: YouTube is blocking requests from your IP.
```

**根因：** `youtube-transcript-api` 的 HTTP 請求被 YouTube 基於 IP 封鎖，即使透過 `http_client` 參數傳入 cookies 也無法繞過。

**可能的解決方向：**
- 使用住宅代理（`ProxyConfig` 參數）；datacenter 出口（DigitalOcean SOCKS）同樣被封
- 在本機執行

## 問題 5：字幕下載 429（部分解決）

**症狀：**
```
ERROR: Unable to download video subtitles: HTTP Error 429: Too Many Requests
```

**背景：** yt-dlp 的 `--write-auto-sub` 成功識別到字幕（`zh-Hant`, `en`），但下載時被 rate limit。

**解法：**
- 等待數分鐘後重試
- 使用 `--sleep-subtitles N` 參數
- 減少對同一影片的重複請求

## 結論

| 執行環境 | 有字幕 | 無字幕 |
|---|---|---|
| 本機／住宅 IP | `--backend local`（原文字幕，免費） | `--backend local`（yt-dlp + Whisper） |
| 雲端 IP | `--backend gemini` | `--backend gemini` |
| 雲端 IP + 有效 cookies | 可試 `local`；Whisper 路徑可能仍卡問題 3 | 同左 |
