from django.db.models import Q


GUIDED_SEARCH_STEPS = [
    {
        "step": 1,
        "field": "type",
        "question": "你大概想找哪一類區塊鏈概念？",
        "options": [
            "幣種或資產",
            "平台或專案",
            "技術機制",
            "錢包或安全",
            "市場與投資",
            "法規與政策",
            "不確定",
        ],
    },
    {
        "step": 2,
        "field": "context",
        "question": "你比較想了解哪一個子情境？",
        "options_by_type": {
            "幣種或資產": [
                "加密貨幣",
                "代幣",
                "穩定幣",
                "非同質化代幣",
                "數位收藏品",
                "不確定",
            ],
            "平台或專案": [
                "以太坊",
                "Polkadot",
                "Cosmos",
                "Fabric",
                "去中心化金融",
                "不確定",
            ],
            "技術機制": [
                "共識機制",
                "智能合約",
                "節點與帳本",
                "密碼學與雜湊",
                "擴容",
                "不確定",
            ],
            "錢包或安全": [
                "私鑰",
                "錢包",
                "數位簽章",
                "釣魚攻擊",
                "冷錢包",
                "不確定",
            ],
            "市場與投資": [
                "交易",
                "投資",
                "風險",
                "指標",
                "現貨交易所買賣基金",
                "不確定",
            ],
            "法規與政策": [
                "監管",
                "合法性",
                "風險管理",
                "金融科技",
                "中央銀行數位貨幣",
                "不確定",
            ],
            "不確定": [
                "交易",
                "開發",
                "錢包",
                "非同質化代幣",
                "監管",
                "區塊鏈",
                "不確定",
            ],
        },
    },
    {
        "step": 3,
        "field": "goal",
        "question": "你現在最想先理解哪一種內容？",
        "options": [
            "我想先知道它是什麼",
            "我想知道它怎麼運作或怎麼使用",
            "我想知道它有什麼風險",
            "我想知道它和其他概念的差異",
            "顯示這一類的全部關鍵詞",
        ],
    },
]


GUIDED_SEARCH_RULES = {
    "type": {
        "幣種或資產": (
            Q(keyword__icontains="加密貨幣")
            | Q(keyword__icontains="幣種")
            | Q(keyword__icontains="代幣")
            | Q(keyword__icontains="穩定幣")
            | Q(keyword__icontains="非同質化代幣")
            | Q(keyword__icontains="Meme幣")
            | Q(keyword__icontains="比特幣")
            | Q(keyword__icontains="以太幣")
        ),
        "平台或專案": (
            Q(keyword__icontains="以太坊")
            | Q(keyword__icontains="Polkadot")
            | Q(keyword__icontains="Cosmos")
            | Q(keyword__icontains="Fabric")
            | Q(keyword__icontains="Hyperledger")
            | Q(keyword__icontains="Corda")
            | Q(keyword__icontains="區塊鏈即服務")
            | Q(keyword__icontains="去中心化金融")
            | Q(keyword__icontains="去中心化應用程式")
        ),
        "技術機制": (
            Q(keyword__icontains="共識")
            | Q(keyword__icontains="共識機制")
            | Q(keyword__icontains="智能合約")
            | Q(keyword__icontains="節點")
            | Q(keyword__icontains="帳本")
            | Q(keyword__icontains="區塊")
            | Q(keyword__icontains="雜湊")
            | Q(keyword__icontains="擴容")
            | Q(keyword__icontains="分片")
        ),
        "錢包或安全": (
            Q(keyword__icontains="錢包")
            | Q(keyword__icontains="私鑰")
            | Q(keyword__icontains="公鑰")
            | Q(keyword__icontains="密鑰")
            | Q(keyword__icontains="數位簽章")
            | Q(keyword__icontains="私鑰安全")
            | Q(keyword__icontains="釣魚攻擊")
            | Q(keyword__icontains="駭客攻擊")
            | Q(keyword__icontains="雙花攻擊")
        ),
        "市場與投資": (
            Q(keyword__icontains="交易")
            | Q(keyword__icontains="投資")
            | Q(keyword__icontains="風險")
            | Q(keyword__icontains="風險管理")
            | Q(keyword__icontains="指標")
            | Q(keyword__icontains="指數")
            | Q(keyword__icontains="市值")
            | Q(keyword__icontains="現貨交易所買賣基金")
            | Q(keyword__icontains="期貨")
        ),
        "法規與政策": (
            Q(keyword__icontains="監管")
            | Q(keyword__icontains="合法性")
            | Q(keyword__icontains="金融科技")
            | Q(keyword__icontains="中央銀行數位貨幣")
            | Q(keyword__icontains="徵信管理")
            | Q(keyword__icontains="風險管理")
        ),
        "不確定": Q(),
    },

    "context": {
        "加密貨幣": (
            Q(keyword__icontains="加密貨幣")
            | Q(keyword__icontains="比特幣")
            | Q(keyword__icontains="以太幣")
            | Q(keyword__icontains="幣種")
            | Q(keyword__icontains="貨幣")
        ),
        "代幣": (
            Q(keyword__icontains="代幣")
            | Q(keyword__icontains="Token")
            | Q(keyword__icontains="雙幣")
            | Q(keyword__icontains="遊戲代幣")
        ),
        "穩定幣": (
            Q(keyword__icontains="穩定幣")
            | Q(keyword__icontains="USDT")
            | Q(keyword__icontains="DAI")
        ),
        "非同質化代幣": (
            Q(keyword__icontains="非同質化代幣")
            | Q(keyword__icontains="NFT")
            | Q(keyword__icontains="NFT交易市場")
            | Q(keyword__icontains="NFT鑄造")
        ),
        "數位收藏品": (
            Q(keyword__icontains="數位收藏品")
            | Q(keyword__icontains="Doodles")
            | Q(keyword__icontains="OpenSea")
        ),

        "以太坊": (
            Q(keyword__icontains="以太坊")
            | Q(keyword__icontains="以太幣")
            | Q(keyword__icontains="以太坊域名服務")
            | Q(keyword__icontains="ENS")
        ),
        "Polkadot": Q(keyword__icontains="Polkadot"),
        "Cosmos": Q(keyword__icontains="Cosmos"),
        "Fabric": (
            Q(keyword__icontains="Fabric")
            | Q(keyword__icontains="Hyperledger")
            | Q(keyword__icontains="鏈碼")
            | Q(keyword__icontains="成員服務提供者")
        ),
        "去中心化金融": (
            Q(keyword__icontains="去中心化金融")
            | Q(keyword__icontains="DeFi")
            | Q(keyword__icontains="DEX")
            | Q(keyword__icontains="Uniswap")
            | Q(keyword__icontains="借貸")
            | Q(keyword__icontains="流動性挖礦")
        ),

        "共識機制": (
            Q(keyword__icontains="共識")
            | Q(keyword__icontains="共識機制")
            | Q(keyword__icontains="工作量證明")
            | Q(keyword__icontains="權益證明")
            | Q(keyword__icontains="委託權益證明")
            | Q(keyword__icontains="Paxos")
            | Q(keyword__icontains="Raft")
            | Q(keyword__icontains="PBFT")
        ),
        "智能合約": (
            Q(keyword__icontains="智能合約")
            | Q(keyword__icontains="合約")
            | Q(keyword__icontains="雜湊時間鎖定合約")
            | Q(keyword__icontains="可撤銷序列成熟合約")
        ),
        "節點與帳本": (
            Q(keyword__icontains="節點")
            | Q(keyword__icontains="帳本")
            | Q(keyword__icontains="數位帳本")
            | Q(keyword__icontains="分散式帳本")
            | Q(keyword__icontains="創世區塊")
        ),
        "密碼學與雜湊": (
            Q(keyword__icontains="密碼學")
            | Q(keyword__icontains="加密")
            | Q(keyword__icontains="解密")
            | Q(keyword__icontains="雜湊")
            | Q(keyword__icontains="雜湊演算法")
            | Q(keyword__icontains="雜湊函數")
            | Q(keyword__icontains="SHA-256")
        ),
        "擴容": (
            Q(keyword__icontains="擴容")
            | Q(keyword__icontains="Rollup")
            | Q(keyword__icontains="分片")
            | Q(keyword__icontains="側鏈")
            | Q(keyword__icontains="閃電網路")
            | Q(keyword__icontains="Layer2")
            | Q(keyword__icontains="Layer3")
        ),

        "私鑰": (
            Q(keyword__icontains="私鑰")
            | Q(keyword__icontains="私鑰安全")
            | Q(keyword__icontains="密鑰")
        ),
        "錢包": (
            Q(keyword__icontains="錢包")
            | Q(keyword__icontains="冷錢包")
            | Q(keyword__icontains="硬體錢包")
        ),
        "數位簽章": (
            Q(keyword__icontains="數位簽章")
            | Q(keyword__icontains="簽名")
            | Q(keyword__icontains="盲簽名")
            | Q(keyword__icontains="環簽名")
            | Q(keyword__icontains="群簽名")
            | Q(keyword__icontains="多重簽名")
        ),
        "釣魚攻擊": (
            Q(keyword__icontains="釣魚攻擊")
            | Q(keyword__icontains="詐騙識別")
            | Q(keyword__icontains="社交工程學")
        ),
        "冷錢包": (
            Q(keyword__icontains="冷錢包")
            | Q(keyword__icontains="硬體錢包")
            | Q(keyword__icontains="資金")
        ),

        "交易": (
            Q(keyword__icontains="交易")
            | Q(keyword__icontains="交易量")
            | Q(keyword__icontains="交易者")
            | Q(keyword__icontains="金融交易")
            | Q(keyword__icontains="中心化交易所")
            | Q(keyword__icontains="去中心化交易所")
        ),
        "投資": (
            Q(keyword__icontains="投資")
            | Q(keyword__icontains="基本面分析")
            | Q(keyword__icontains="技術分析")
            | Q(keyword__icontains="策略")
        ),
        "風險": (
            Q(keyword__icontains="風險")
            | Q(keyword__icontains="潛在風險")
            | Q(keyword__icontains="風險管理")
            | Q(keyword__icontains="駭客攻擊")
        ),
        "指標": (
            Q(keyword__icontains="指標")
            | Q(keyword__icontains="指數")
            | Q(keyword__icontains="市值")
            | Q(keyword__icontains="總鎖倉價值")
            | Q(keyword__icontains="歷史最高價")
        ),
        "現貨交易所買賣基金": (
            Q(keyword__icontains="現貨交易所買賣基金")
            | Q(keyword__icontains="ETF")
            | Q(keyword__icontains="金融科技")
        ),

        "監管": (
            Q(keyword__icontains="監管")
            | Q(keyword__icontains="合法性")
        ),
        "合法性": Q(keyword__icontains="合法性"),
        "金融科技": (
            Q(keyword__icontains="金融科技")
            | Q(keyword__icontains="中央銀行數位貨幣")
        ),
        "中央銀行數位貨幣": Q(keyword__icontains="中央銀行數位貨幣"),
        "徵信管理": Q(keyword__icontains="徵信管理"),

        "開發": (
            Q(keyword__icontains="開發")
            | Q(keyword__icontains="編程")
            | Q(keyword__icontains="部署")
            | Q(keyword__icontains="API3")
            | Q(keyword__icontains="Golang")
        ),
        "區塊鏈": Q(keyword__icontains="區塊鏈"),

        "不確定": Q(),
    },

    "goal": {
        "我想先知道它是什麼": Q(),
        "我想知道它怎麼運作或怎麼使用": (
            Q(keyword__icontains="運作")
            | Q(keyword__icontains="操作")
            | Q(keyword__icontains="應用")
            | Q(keyword__icontains="部署")
            | Q(keyword__icontains="開發")
            | Q(keyword__icontains="交易")
        ),
        "我想知道它有什麼風險": (
            Q(keyword__icontains="風險")
            | Q(keyword__icontains="潛在風險")
            | Q(keyword__icontains="風險管理")
            | Q(keyword__icontains="攻擊")
            | Q(keyword__icontains="漏洞")
            | Q(keyword__icontains="詐騙識別")
        ),
        "我想知道它和其他概念的差異": (
            Q(keyword__icontains="比較")
            | Q(keyword__icontains="差異")
            | Q(keyword__icontains="機制")
            | Q(keyword__icontains="架構")
            | Q(keyword__icontains="結構")
        ),
        "顯示這一類的全部關鍵詞": Q(),
    },
}


BEGINNER_GUIDE_QUERY = (
    Q(keyword__icontains="區塊鏈")
    | Q(keyword__icontains="分散式帳本")
    | Q(keyword__icontains="區塊")
    | Q(keyword__icontains="節點")
    | Q(keyword__icontains="交易")
    | Q(keyword__icontains="錢包")
    | Q(keyword__icontains="私鑰")
    | Q(keyword__icontains="公鑰")
    | Q(keyword__icontains="雜湊")
    | Q(keyword__icontains="共識")
    | Q(keyword__icontains="智能合約")
    | Q(keyword__icontains="比特幣")
    | Q(keyword__icontains="以太坊")
)


def get_step2_options(type_choice):
    step2 = GUIDED_SEARCH_STEPS[1]
    return step2["options_by_type"].get(
        type_choice,
        step2["options_by_type"]["不確定"]
    )


def build_guided_query(type_choice="", context_choice="", goal_choice=""):
    """
    將使用者三題答案轉成 Django Q 查詢條件。

    若 Step 1 與 Step 2 都選「不確定」，
    視為初學者探索模式，回傳基礎區塊鏈入門關鍵詞。
    """
    if type_choice == "不確定" and context_choice == "不確定":
        return BEGINNER_GUIDE_QUERY

    q_filter = Q()

    selected = {
        "type": type_choice,
        "context": context_choice,
        "goal": goal_choice,
    }

    for field, value in selected.items():
        rule = GUIDED_SEARCH_RULES.get(field, {}).get(value)
        if rule:
            q_filter |= rule

    return q_filter


def get_guided_result_message(type_choice="", context_choice="", goal_choice="", count=0):
    """
    依照使用者選擇產生結果說明文字。
    """
    if type_choice == "不確定" and context_choice == "不確定":
        return (
            f"你目前尚未指定明確方向，因此系統提供 {count} 個適合初學者的"
            "基礎區塊鏈關鍵詞，協助你先建立第一層理解。"
        )

    return (
        f"你選擇了「{type_choice or '不確定'} / "
        f"{context_choice or '不確定'} / "
        f"{goal_choice or '不確定'}」，"
        f"系統為你篩選出 {count} 個可能相關的關鍵詞。"
    )