# RAG-Blockchain

結合 **RAG（Retrieval-Augmented Generation）** 技術的區塊鏈／密碼學知識庫系統，並內嵌使用者行為實驗模組，用於研究使用者在不同搜尋方式（關鍵字瀏覽、關鍵字搜尋、引導式搜尋）下尋找正確關鍵字的效率與導航行為。

## 系統架構

| 元件 | 技術 |
| --- | --- |
| 後端框架 | Django 5.2（Python 3.12） |
| 資料庫 | PostgreSQL 16 |
| 向量檢索 | FAISS + `BAAI/bge-m3` embedding 模型 |
| 生成式 AI | Google Gemini 2.5 Flash（`google-generativeai`） |
| 部署 | Docker Compose（Nginx + Gunicorn + PostgreSQL） |

專案內含三個 Django app：

- `apps/knowledge`：知識庫核心（關鍵字、文章、Q&A、AI 摘要、引導式搜尋）
- `apps/experiment`：使用者實驗流程（任務、導航紀錄、實驗結果匯出）
- `apps/integrations`：AI 整合層（`RAGService`：FAISS 檢索 + Gemini 生成回答）

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

## 專案結構

```
apps/
  knowledge/      # 知識庫：關鍵字、文章、Q&A、引導式搜尋
  experiment/      # 使用者任務實驗、導航紀錄、結果匯出
  integrations/    # RAGService：FAISS 檢索 + Gemini 生成
config/            # Django 專案設定（settings、urls）
faiss_data/        # FAISS 索引檔
static/、templates/ # 前端靜態資源與樣板
Dockerfile、docker-compose.yml、nginx.conf、entrypoint.sh  # 部署設定
```
