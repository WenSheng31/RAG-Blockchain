LEARNING_PATH_TOPICS = [
    {
        "id": "what_is_blockchain",
        "title": "什麼是區塊鏈？",
        "subtitle": "分散式帳本、不可篡改、去中心化",
        "difficulty": "基礎",
        "badge_css": "bg-green-50 text-green-700 border border-green-200",
        "border_css": "border-l-green-400",
        "description": (
            "區塊鏈是一種將資料分散儲存在多台電腦上的技術，沒有任何單一機構能夠控制或竄改其中的記錄。"
            "每一筆資料都被打包成「區塊」，依時間順序串接成「鏈」，一旦寫入便幾乎無法更改。"
            "這種設計讓陌生人之間也能在不需要中間人的情況下互相信任。"
        ),
        "core_concepts": ["分散式帳本", "去中心化", "不可篡改", "區塊與鏈"],
        "keyword_ids": [
            40,   # 區塊鏈／Blockchain
            237,  # 分散式帳本／Distributed Ledger
            212,  # 去中心化／Decentralization
            97,   # 不可篡改性／Immutability
            43,   # 公有鏈／Public Blockchain
            48,   # 私有鏈／Private Blockchain
            49,   # 聯盟鏈／Consortium Blockchain
            218,  # 帳本／Ledger
            194,  # 創世區塊／Genesis Block
            203,  # 分散式系統／Distributed System
            214,  # 數據塊／Data Block
            187,  # 鏈／Chain
        ],
    },
    {
        "id": "core_concepts",
        "title": "核心運作概念",
        "subtitle": "節點、共識、公鑰私鑰、錢包",
        "difficulty": "基礎",
        "badge_css": "bg-green-50 text-green-700 border border-green-200",
        "border_css": "border-l-green-400",
        "description": (
            "要讓區塊鏈正常運作，需要一套精密的機制協調網路上所有的參與者。"
            "節點負責儲存與驗證資料，共識機制讓所有人對「哪些交易是真實的」達成一致，"
            "而公鑰與私鑰則確保只有真正的擁有者才能動用自己的資產。"
        ),
        "core_concepts": ["節點", "共識機制", "公鑰與私鑰", "數位簽章"],
        "keyword_ids": [
            186,  # 節點／Node
            89,   # 共識／Consensus
            90,   # 共識機制／Consensus Mechanism
            74,   # 工作量證明／Proof of Work
            68,   # 權益證明／Proof of Stake
            30,   # 公鑰／Public Key
            31,   # 私鑰／Private Key
            47,   # 數位簽章／Digital Signature
            241,  # 交易／Transaction
            242,  # 錢包／Wallet
            36,   # 點對點網路／Peer-to-Peer
            205,  # 礦工／Miner
        ],
    },
    {
        "id": "applications",
        "title": "常見應用領域",
        "subtitle": "加密貨幣、NFT、智能合約、DeFi",
        "difficulty": "進階",
        "badge_css": "bg-orange-50 text-orange-700 border border-orange-200",
        "border_css": "border-l-orange-400",
        "description": (
            "區塊鏈技術已延伸出許多真實世界的應用場景。"
            "加密貨幣讓人們可以在全球範圍內低成本轉帳，NFT 讓數位作品擁有可驗證的所有權，"
            "智能合約能自動執行合約條款，而 DeFi 則試圖打造一套不依賴傳統銀行的金融體系。"
        ),
        "core_concepts": ["加密貨幣", "NFT", "智能合約", "DeFi"],
        "keyword_ids": [
            39,   # 加密貨幣／Cryptocurrency
            42,   # 比特幣／Bitcoin
            26,   # 以太坊／Ethereum
            41,   # 智能合約／Smart Contract
            52,   # 非同質化代幣／NFT
            50,   # 代幣／Token
            180,  # 穩定幣／Stablecoin
            240,  # 去中心化金融／Decentralized Finance
            213,  # 去中心化自治組織／DAO
            259,  # 去中心化應用程式／DApp
            272,  # 去中心化交易所／DEX
            183,  # 質押／Staking
        ],
    },
    {
        "id": "tech_security",
        "title": "技術與安全機制",
        "subtitle": "共識演算法、雜湊函數、攻擊類型",
        "difficulty": "深入",
        "badge_css": "bg-red-50 text-red-700 border border-red-200",
        "border_css": "border-l-red-400",
        "description": (
            "深入了解區塊鏈，需要掌握底層的密碼學基礎與系統可能面臨的攻擊風險。"
            "雜湊函數是讓資料「指紋化」的核心工具，各種共識演算法決定了系統的效率與安全性，"
            "而認識常見攻擊手法則有助於評估一個區塊鏈系統的可靠程度。"
        ),
        "core_concepts": ["雜湊函數", "共識演算法", "密碼學", "攻擊類型"],
        "keyword_ids": [
            251,  # 雜湊函數／Hash Function
            10,   # 密碼學／Cryptography
            69,   # 零知識證明／Zero-Knowledge Proof
            88,   # 實用拜占庭容錯演算法／PBFT
            91,   # 拜占庭容錯／Byzantine Fault Tolerance
            86,   # 擴容方案／Rollup
            196,  # 分片／Sharding
            216,  # 雙花攻擊／Double-Spending Attack
            124,  # 釣魚攻擊／Phishing Attack
            126,  # 駭客攻擊／Hacking Attack
            191,  # 閃電網路／Lightning Network
            276,  # 橋接／Bridge
        ],
    },
]
