# RAG-Blockchain

結合 **RAG（Retrieval-Augmented Generation）** 技術的區塊鏈／密碼學知識庫系統，並內嵌使用者行為實驗模組，用於研究使用者在不同搜尋方式（快速搜尋、主題分類瀏覽、新手入口）下尋找正確關鍵字的效率與導航行為。本 repository 涵蓋研究所需的三個部分：**知識庫與 RAG 模型建置**、**可供受試者操作的網站**，以及**實驗過程中產生的原始資料匯出機制**。

## 系統架構

| 元件 | 技術 |
| --- | --- |
| 後端框架 | Django 5.2（Python 3.12） |
| 資料庫 | PostgreSQL 16 |
| 向量檢索 | FAISS（`IndexFlatIP`）+ `BAAI/bge-m3` embedding 模型 |
| 生成式 AI | Google Gemini 2.5 Flash（`google-generativeai`） |
| 部署 | Docker Compose（Nginx + Gunicorn + PostgreSQL），並透過 GitHub Actions self-hosted runner 自動部署 |

專案內含三個 Django app：

- `apps/knowledge`：知識庫核心（關鍵字、文章、Q&A、AI 摘要、引導式搜尋）
- `apps/experiment`：使用者實驗流程（任務、導航紀錄、實驗結果匯出）
- `apps/integrations`：AI 整合層（`RAGService`：FAISS 檢索 + Gemini 生成回答）

## 功能特色

- **知識庫瀏覽**：主題 → 分類 → 關鍵字 → Q&A 的階層式瀏覽（`apps/knowledge`）
- **關鍵字搜尋 / 自動完成**：首頁快速搜尋框，即時比對關鍵字
- **引導式搜尋**：三步驟問答（類型 → 子情境 → 目的）縮小範圍後推薦關鍵字，設定於 `apps/knowledge/guided_search_config.py`
- **AI 摘要生成（RAG）**：針對關鍵字整合站內文章 + FAISS 向量檢索補充內容，交由 Gemini 生成 Markdown 摘要，並快取於 `AISummaryCache`
- **使用者行為實驗**：20 題情境式任務，記錄受試者在三種搜尋入口下尋找正確關鍵字的路徑、正確率與花費時間
- **後台資料匯出**：透過 Django Admin（`django-import-export`）將任務結果與導航路徑匯出為 CSV / Excel，供後續統計分析使用

## 使用者行為實驗設計

實驗題目與規則定義於 `apps/experiment/experiment.py`：

- 共 **20 題**情境式任務（`TASKS`），涵蓋區塊鏈基礎、去中心化、共識機制（PoW/PoS/Paxos 等）、密碼學、私鑰安全、智能合約等主題
- 每題皆定義：
  - `correct_keywords`：判定作答正確的關鍵字（比對資料庫 `keyword_en`，無則 fallback 至 `keyword`）
  - `allowed_search_modes`：該題受試者被允許使用的搜尋入口，三種模式定義於 `SEARCH_MODE_LABELS`：
    | 模式代碼 | 說明 |
    | --- | --- |
    | `quick_search` | 快速搜尋（首頁搜尋框） |
    | `topic_browse` | 主題分類瀏覽（首頁主題卡片逐層瀏覽） |
    | `learning_path` | 新手入口（僅含精選關鍵字的學習路徑頁） |

流程（`apps/experiment/views.py` + `services.py`）：

1. `start_task` 初始化 session、開始計時
2. 受試者依該題 `allowed_search_modes` 在知識庫中瀏覽／搜尋，`NavigationMiddleware` 全程記錄頁面路徑至 `NavigationLog`
3. 選定關鍵字後呼叫 `finish_task`，比對正確性並記錄花費時間
4. 20 題完成後彙整為一筆 `TaskSessionResult`（總花費時間、答對題數、正確率、每題作答 JSON）

資料模型：

- **`NavigationLog`**：`session_key` / `task_id` / `page_type`（topic、keyword、keyword_item、search、search_click）/ `page_id` / `page_name` / `timestamp`
- **`TaskSessionResult`**：`session_key` / `started_at` / `finished_at` / `total_time_seconds` / `correct_count` / `accuracy` / `answers`（JSON）

## RAG 檢索與生成流程（模型建置）

### 1. 建立向量索引

```bash
python manage.py build_faiss_index
```

對應 `apps/knowledge/management/commands/build_faiss_index.py`：

1. 讀取所有 `Article`（標題 + 內容）
2. 以 `BAAI/bge-m3` 的 tokenizer 將長文章切塊（**chunk size = 400 tokens，overlap = 80 tokens**），避免超過語意視窗導致資訊遺失
3. 對每個切塊以 `BAAI/bge-m3`（`max_seq_length=8192`）產生 normalize 過的向量
4. 建立 `faiss.IndexFlatIP`（內積 = cosine similarity），寫入暫存檔後再原子性地取代舊索引，避免服務中途讀到半完成的檔案
5. 輸出：`faiss_data/gitbook_faiss.index`（向量索引）、`faiss_data/gitbook_ids.npy`（每個向量對應的 `Article` ID，一篇文章可能對應多個切塊）

`faiss_data/` 內已附上目前資料庫內容建立好的索引，可直接使用；知識庫文章內容更新後需重新執行上述指令。

### 2. 線上檢索與生成（`apps/integrations/ai.py`）

- `RAGService` 為 process 內的 singleton（`get_rag()` 延遲載入模型，`reset()` 可強制重載，用於索引更新後刷新記憶體內容）
- `retrieve(query, k=5)`：查詢向量與索引中「所有」向量計算內積後排序，依切塊對應的 `Article` ID 去重，回傳前 k 篇不重複文章
- `generate(keyword, contexts)`：將檢索到的文章內容組成 prompt，要求 Gemini 以繁體中文摘要說明該關鍵字；若站內內容不足，允許 AI 補充自身知識，但需標註警語區塊，避免摘要內容真偽不分
- 呼叫端 `apps/knowledge/services.py::get_or_generate_summary()`：優先取最多 5 篇標記該關鍵字的文章，不足時用 FAISS 檢索補足，結果快取於 `AISummaryCache`（含 `sources` 來源清單）

## 環境需求

- Python 3.12
- PostgreSQL 16（本機安裝，或使用下方 Docker Compose 一併啟動）
- Google Gemini API 金鑰（[取得方式](https://ai.google.dev/)）
- （選用）NVIDIA GPU + CUDA 12.1：`requirements.txt` 預設安裝 `torch==2.5.1+cu121`；若只在 CPU 環境開發，請改安裝 CPU 版 PyTorch（見下方安裝步驟）

## 安裝與執行（本機開發）

### 1. 取得原始碼並建立虛擬環境

```bash
git clone <本專案 repository URL>
cd RAG-Blockchain

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 2. 安裝套件

```bash
pip install -r requirements.txt
```

> `requirements.txt` 中的 `torch==2.5.1+cu121` 為 CUDA 12.1 專用版本，需搭配 `--extra-index-url https://download.pytorch.org/whl/cu121` 安裝（詳見 `Dockerfile`）：
> ```bash
> pip install --extra-index-url https://download.pytorch.org/whl/cu121 -r requirements.txt
> ```
> 若本機沒有 NVIDIA GPU，請先安裝 CPU 版 PyTorch，再安裝其餘套件：
> ```bash
> pip install torch==2.5.1
> pip install -r requirements.txt
> ```

### 3. 設定環境變數

複製範例檔並依實際環境修改：

```bash
cp .env.example .env
```

`.env` 內容說明：

| 變數 | 說明 |
| --- | --- |
| `DEBUG` | 是否啟用開發模式（本機開發建議設為 `True`） |
| `DJANGO_SECRET_KEY` | Django 密鑰，自行產生一組隨機字串 |
| `GOOGLE_API_KEY` | Gemini API 金鑰，用於 RAG 問答生成 |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` | PostgreSQL 連線資訊 |
| `DB_HOST` / `DB_PORT` | 資料庫主機與埠號（本機開發通常為 `localhost` / `5432`） |
| `ALLOWED_HOSTS` | Django 允許的 Host，本機開發可設為 `localhost,127.0.0.1` |

### 4. 建立資料庫並執行 migration

先在 PostgreSQL 建立對應的資料庫與使用者（名稱需與 `.env` 一致），接着執行：

```bash
python manage.py migrate
python manage.py createsuperuser   # 建立後台管理帳號
```

### 5.（選用）建立 FAISS 向量索引

`faiss_data/` 目錄下已附上預先建立好的索引檔（`gitbook_faiss.index`、`gitbook_ids.npy`），可直接使用。若知識庫文章（`Article`）內容有更新，需重新建立索引：

```bash
python manage.py build_faiss_index
```

### 6. 啟動開發伺服器

```bash
python manage.py runserver
```

開啟瀏覽器造訪 `http://127.0.0.1:8000/`，管理後台位於 `http://127.0.0.1:8000/manage-rag/`。

## 使用 Docker Compose 執行（近似正式環境）

本專案提供 `Dockerfile` 與 `docker-compose.yml`，可一次啟動 Django（Gunicorn）、PostgreSQL、Nginx：

```bash
cp .env.example .env   # 並填入實際的金鑰與密碼
docker compose up --build
```

啟動後透過 `http://localhost:8080/` 存取（對應 `docker-compose.yml` 中 Nginx 對外的 `8080` port）。首次啟動時 `entrypoint.sh` 會自動執行 `migrate` 與 `collectstatic`，仍需另外進入容器建立後台帳號：

```bash
docker compose exec web python manage.py createsuperuser
```

> `docker-compose.yml` 預設會請求 NVIDIA GPU 資源（`deploy.resources.reservations.devices`），若本機無 GPU 請自行移除該區塊後再啟動。

## 部署（CI/CD）

`.github/workflows/deploy.yml` 定義了推送至 `main` 分支後的自動部署流程：

1. 由 self-hosted runner 在部署主機上 `git pull origin main`
2. 依 GitHub Secrets（`DJANGO_SECRET_KEY`、`GOOGLE_API_KEY`、`DB_PASSWORD`）產生正式環境的 `.env`
3. 執行 `docker compose up --build -d` 重新建置並啟動服務

## 實驗資料匯出

受試者完成實驗後的資料儲存在 `TaskSessionResult` / `NavigationLog`，可於 Django Admin（`/manage-rag/`）的「實驗結果」列表使用 **Export**（`django-import-export`）功能匯出為 CSV / Excel，欄位包含：

- 基本資訊：`session_key`、開始/結束時間、總花費時間、答對題數、正確率
- `answers`：每題作答明細（JSON，含選擇的關鍵字、對錯、花費時間）
- `navigation_paths`：依 `task_id` 分組、依時間排序的瀏覽路徑純文字描述（`apps/experiment/admin.py::_build_navigation_paths_text`）

> 目前 repository 僅提供「原始資料匯出」，尚未包含統計檢定 / 圖表分析腳本；後續可依匯出的 CSV，比較不同 `allowed_search_modes` 下的正確率、花費時間與導航路徑長度差異。

## 專案結構

```
apps/
  knowledge/       # 知識庫：關鍵字、文章、Q&A、引導式搜尋、AI 摘要
  experiment/      # 使用者任務實驗、導航紀錄、結果匯出
  integrations/    # RAGService：FAISS 檢索 + Gemini 生成
config/            # Django 專案設定（settings、urls）
faiss_data/        # FAISS 索引檔（gitbook_faiss.index、gitbook_ids.npy）
static/js/         # 前端互動腳本（搜尋、引導式搜尋、任務面板等）
templates/         # HTML 樣板
Dockerfile、docker-compose.yml、nginx.conf、entrypoint.sh  # 部署設定
.github/workflows/deploy.yml                                # CI/CD 自動部署
```
