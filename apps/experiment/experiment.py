# correct_keywords 與資料庫 keyword_en 欄位比對（無 keyword_en 者 fallback 至 keyword）

# 測驗期間可使用的搜尋入口：
#   - "quick_search"   快速搜尋（首頁搜尋框）
#   - "topic_browse"   主題分類瀏覽（首頁主題卡片）
#   - "learning_path"  新手入口（學習路徑頁，僅含精選關鍵字，注意答案需落在該頁可見範圍內）
SEARCH_MODE_LABELS = {
    "quick_search": "快速搜尋",
    "topic_browse": "主題分類瀏覽",
    "learning_path": "新手入口",
}
ALL_SEARCH_MODES = list(SEARCH_MODE_LABELS)

TASKS = [
    {
        "task_id": "Q1",
        "description": "1.\t區塊鏈核心定義理解：你剛開始學習「區塊鏈」，聽說它是一種分散式帳本，並具備不可竄改與可追溯的特性。為了確認自己的理解，你希望找到相關資訊來驗證區塊鏈的定義與其核心特徵。",
        "correct_keywords": ["Distributed Ledger", "Immutability", "Blockchain"],
        "allowed_search_modes": ["learning_path"],
    },
    {
        "task_id": "Q2",
        "description": "2.\t去中心化概念理解：在閱讀區塊鏈相關資料時，你發現「去中心化」是一個關鍵概念。你希望了解其與傳統中心化系統的差異，以及去中心化如何影響系統運作。",
        "correct_keywords": ["Decentralization"],
        "allowed_search_modes": ["learning_path"],
    },
    {
        "task_id": "Q3",
        "description": "3.\t分散式帳本概念：你在進一步閱讀區塊鏈技術時，發現「分散式帳本」是其核心基礎之一。然而你對於其具體運作方式仍不清楚，尤其是在資料如何被多個節點共同維護，以及其與傳統集中式資料庫之間的差異。為了釐清這些疑問，你希望透過系統查找相關內容，以理解分散式帳本的架構、資料同步方式與其優勢。",
        "correct_keywords": ["Distributed Ledger"],
        "allowed_search_modes": ["quick_search"],
    },
    {
        "task_id": "Q4",
        "description": "4.\t私鑰安全的重要性：你在學習區塊鏈的資產管理時，發現每位使用者都擁有一組唯一的「私鑰」，一旦遺失或外洩，鏈上資產將無法復原且可能遭竊。你開始思考：為何私鑰如此關鍵？有哪些常見的洩漏風險與保管方式？因此，你希望透過系統查詢相關內容，以理解「私鑰安全」的重要性及防護策略。",
        "correct_keywords": ["Private Key Security", "Private Key"],
        "allowed_search_modes": ["quick_search"],
    },
    {
        "task_id": "Q5",
        "description": "5.\t聯盟鏈概念：你在深入了解區塊鏈類型時，發現除了完全開放的公有鏈之外，還存在一種由多個組織共同維護的「聯盟鏈」架構。你希望理解聯盟鏈如何在多個機構之間共享帳本，並在維持去中心化的同時兼顧隱私與效率。因此，你希望透過系統查找相關說明，以掌握聯盟鏈的運作方式與適用場景。",
        "correct_keywords": ["Consortium Blockchain"],
        "allowed_search_modes": ["learning_path"],
    },
    {
        "task_id": "Q6",
        "description": "6.\t共識機制的目的：在學習區塊鏈運作流程時，你發現系統中並沒有中心管理者，但卻仍能維持資料一致性。這讓你對「共識機制」產生興趣，並想了解：在沒有中央控制的情況下，節點之間是如何達成一致決策的？因此你希望查詢相關內容，以理解共識機制的核心目的與功能。",
        "correct_keywords": ["Consensus Mechanism"],
        "allowed_search_modes": ["quick_search"],
    },
    {
        "task_id": "Q7",
        "description": "7.\tPoW運作原理：你在閱讀比特幣相關資料時，發現其採用「工作量證明（PoW）」機制，並了解到這種方法需要大量運算資源與電力消耗。你開始思考這樣的設計是否合理，以及其具體運作流程為何。因此，你希望查詢相關資訊，以理解PoW如何透過計算競賽來達成共識。",
        "correct_keywords": ["Proof of Work"],
        "allowed_search_modes": ["learning_path"],
    },
    {
        "task_id": "Q8",
        "description": "8.\tPoS機制理解：在比較不同區塊鏈系統時，你發現部分新興平台改採「權益證明（PoS）」機制，以降低能源消耗。你希望進一步了解PoS是如何透過質押機制來選出驗證者，並與PoW進行比較。因此，你希望透過系統查找相關內容，以掌握其運作邏輯與優缺點。",
        "correct_keywords": ["Proof of Stake"],
        "allowed_search_modes": ["quick_search"],
    },
    {
        "task_id": "Q9",
        "description": "9.\tBFT容錯機制：你在研究分散式系統時，接觸到「拜占庭容錯（BFT）」概念，並了解到其可在節點不完全可信的情況下維持系統正確運作。你希望理解在存在惡意節點時，系統如何仍能達成正確決策，因此你希望查詢相關資料以掌握BFT的基本原理與應用。",
        "correct_keywords": ["Byzantine Fault Tolerance"],
        "allowed_search_modes": ["learning_path"],
    },
    {
        "task_id": "Q10",
        "description": "10.\tPaxos與Raft比較：在進一步研究共識演算法時，你發現「Paxos」與「Raft」都是常見的分散式共識機制，但兩者在設計理念與實作難度上有所差異。你希望透過系統查找相關說明，以比較這兩種演算法在可理解性、實務應用與系統設計上的不同。",
        "correct_keywords": ["Paxos Consensus Algorithm", "Raft Consensus Algorithm"],
        "allowed_search_modes": ["topic_browse"],
    },
    {
        "task_id": "Q11",
        "description": "11.\t你在閱讀區塊鏈結構時，發現每個區塊都包含雜湊值，並與前一區塊相連。你開始思考「雜湊函數」在其中扮演什麼角色，以及為何能確保資料安全。因此，你希望查詢相關內容，以理解雜湊函數的特性與其在區塊鏈中的應用。",
        "correct_keywords": ["Hash Function"],
        "allowed_search_modes": ["quick_search"],
    },
    {
        "task_id": "Q12",
        "description": "12.\tMerkle Tree結構：你在學習區塊鏈資料驗證機制時，接觸到「Merkle Tree（默克爾樹）」結構，並了解到它可以提升驗證效率。然而你對其運作方式仍不清楚，因此希望透過系統查詢相關說明，以理解其如何透過樹狀結構進行資料驗證與壓縮。",
        "correct_keywords": ["Merkle Tree"],
        "allowed_search_modes": ["topic_browse"],
    },
    {
        "task_id": "Q13",
        "description": "13.\t密碼學應用：你發現區塊鏈系統中大量使用「密碼學」技術來確保安全性，但你對這些技術的整體角色仍不夠清楚。因此，你希望查詢相關資料，以了解密碼學在區塊鏈中的應用範圍，例如資料加密、驗證與身份識別等。",
        "correct_keywords": ["Cryptography"],
        "allowed_search_modes": ["learning_path"],
    },
    {
        "task_id": "Q14",
        "description": "14.\t公私鑰機制：你在進行區塊鏈交易時，發現每個使用者都擁有一組「公鑰」與「私鑰」。你希望了解這兩者之間的關係，以及如何用於交易驗證與身份識別。因此，你希望透過系統查找相關內容，以掌握其運作原理。",
        "correct_keywords": ["Public Key", "Private Key"],
        "allowed_search_modes": ["quick_search"],
    },
    {
        "task_id": "Q15",
        "description": "15.\t公開金鑰基礎建設(PKI)架構：你在延伸學習資訊安全時，接觸到「公開金鑰基礎建設（PKI）」，並了解到其中包含憑證機構（CA）與註冊機構（RA）等角色。你希望理解這些角色的功能與運作流程，因此希望查詢相關資料，以建立完整的PKI架構概念。",
        "correct_keywords": ["Public Key Infrastructure", "Certificate Authority", "Registration Authority"],
        "allowed_search_modes": ["topic_browse"],
    },
    {
        "task_id": "Q16",
        "description": "16.\t數位簽章：你在研究電子交易安全時，發現「數位簽章」可以確保資料不可否認性。你希望理解其運作方式，以及如何證明資料確實由特定使用者所產生。因此，你希望透過系統查詢相關說明。",
        "correct_keywords": ["Digital Signature"],
        "allowed_search_modes": ["learning_path"],
    },
    {
        "task_id": "Q17",
        "description": "17.\t可擴展性問題：你在比較不同區塊鏈平台時，注意到「可擴展性」是一個重要指標，但許多區塊鏈系統存在效能瓶頸。你希望了解這些限制的來源，以及其對實際應用的影響，因此希望查詢相關內容。",
        "correct_keywords": ["Scalability"],
        "allowed_search_modes": ["topic_browse"],
    },
    {
        "task_id": "Q18",
        "description": "18.\tLayer 2技術：在了解區塊鏈效能問題後，你發現「Layer 2」技術被提出作為解決方案。你希望進一步了解其運作方式，例如如何將部分交易移至鏈外處理，因此希望透過系統查找相關資訊。",
        "correct_keywords": ["Layer2"],
        "allowed_search_modes": ["topic_browse"],
    },
    {
        "task_id": "Q19",
        "description": "19.\t智能合約：你在接觸區塊鏈應用時，經常看到「智能合約」的概念，但你對其實際運作方式仍不清楚。你希望了解其如何自動執行條件邏輯，以及在區塊鏈上的部署方式，因此希望查詢相關內容。",
        "correct_keywords": ["Smart Contract"],
        "allowed_search_modes": ["quick_search"],
    },
    {
        "task_id": "Q20",
        "description": "20.\t區塊鏈應用場景：除了金融領域之外，你發現區塊鏈也被「應用」於學歷驗證、公證、供應鏈等場景。你希望了解這些應用如何利用區塊鏈特性來解決實務問題，因此希望透過系統查找相關案例與說明。",
        "correct_keywords": ["Application"],
        "allowed_search_modes": ["topic_browse"],
    },
]
