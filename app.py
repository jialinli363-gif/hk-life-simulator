"""
理財人生重開模擬器 (Wealth Life Reboot Simulator)
基於 Streamlit 的互動式理財人生模擬小遊戲
特色：深色高飽和主題 + 突發事件 + 財經小課堂 + 6 種結局
"""

import streamlit as st
import random
import pandas as pd
import altair as alt

# ==================== 頁面基本配置 ====================
st.set_page_config(
    page_title="理財人生重開模擬器",
    page_icon="🎲",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==================== 全局 CSS — 深色主題 ====================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #ffffff;
    }
    .stApp p, .stApp span, .stApp div, .stApp label, .stApp li {
        color: #e8e8e8 !important;
    }
    .big-title {
        font-size: 36px !important;
        font-weight: 900 !important;
        color: #FFD700 !important;
        text-shadow: 0 0 15px rgba(255,215,0,0.6), 0 0 40px rgba(255,215,0,0.3);
        letter-spacing: 2px;
    }
    .sub-title {
        font-size: 24px !important;
        font-weight: 800 !important;
        color: #00D4FF !important;
        text-shadow: 0 0 10px rgba(0,212,255,0.4);
    }
    .core-rule {
        font-size: 22px !important;
        font-weight: 800 !important;
        color: #FFD700 !important;
        text-align: center !important;
        text-shadow: 0 0 20px rgba(255,215,0,0.5);
        padding: 15px 0;
    }
    .gold-card {
        background: linear-gradient(135deg, rgba(255,215,0,0.15) 0%, rgba(255,165,0,0.08) 100%);
        border: 2px solid #FFD700;
        border-radius: 18px;
        padding: 25px;
        text-align: center;
        margin: 15px 0;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.25), inset 0 0 30px rgba(255,215,0,0.05);
    }
    .blue-card {
        background: linear-gradient(135deg, rgba(59,130,246,0.15) 0%, rgba(15,23,42,0.8) 100%);
        border: 2px solid #3b82f6;
        border-radius: 14px;
        padding: 18px 22px;
        margin: 12px 0;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.25);
    }
    .red-card {
        background: linear-gradient(135deg, rgba(239,68,68,0.15) 0%, rgba(15,23,42,0.8) 100%);
        border: 2px solid #ef4444;
        border-radius: 14px;
        padding: 18px 22px;
        margin: 12px 0;
        box-shadow: 0 4px 20px rgba(239, 68, 68, 0.25);
    }
    .sticker-box {
        background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%);
        border: 2px solid rgba(255,255,255,0.2);
        border-radius: 16px;
        padding: 15px;
        text-align: center;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .sticker-icon { font-size: 64px; line-height: 1.2; }

    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 14px 24px;
        font-size: 20px;
        font-weight: 800;
        background: linear-gradient(135deg, #FFD700 0%, #FF8C00 100%);
        color: #1a1a2e !important;
        border: none;
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
        transition: all 0.3s;
        text-shadow: none;
    }
    div.stButton > button:hover {
        box-shadow: 0 8px 30px rgba(255, 215, 0, 0.6);
        transform: translateY(-3px);
    }

    div[data-testid="metric-container"] {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 10px;
    }
    div[data-testid="metric-container"] label,
    div[data-testid="metric-container"] div { color: #ffffff !important; }

    .champagne-banner {
        text-align: center;
        margin: 20px 0;
        padding: 20px;
        border-radius: 20px;
        background: rgba(255, 215, 0, 0.1);
        border: 2px solid #FFD700;
        box-shadow: 0 0 50px rgba(255,215,0,0.4);
    }
    .champagne-emoji { font-size: 56px; }
    .champagne-title {
        font-size: 28px !important;
        font-weight: 900 !important;
        color: #FFD700 !important;
        text-shadow: 0 0 20px rgba(255,215,0,0.8);
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 全局工具函數 ====================
def clamp_stats():
    for key in ["wealth", "health", "happiness"]:
        st.session_state.stats[key] = max(0, min(100, st.session_state.stats[key]))

def go_page(page):
    st.session_state.page = page
    st.rerun()

def restart_game():
    st.session_state.stats = {"wealth": 0, "health": 0, "happiness": 0}
    st.session_state.age_index = 0
    st.session_state.inventory = []
    st.session_state.log = []
    st.session_state.modal_info = None
    st.session_state.pending_rand_ev = None
    st.session_state.game_over = False
    st.session_state.ending_type = None
    go_page("intro")

# ==================== 事件數據庫 ====================
RANDOM_EVENTS = [
    {
        "title": "⚡ 💥 突發事件：港股跳水遭槓桿追繳！",
        "desc": "受外圍市場衝擊，你高槓桿炒作的港股大幅下跌，券商催促你補足保證金！",
        "emoji": "📉💸😱",
        "options": [
            (
                "🔴 斬倉止損：忍痛割肉落袋",
                {"wealth": -20, "health": -5, "happiness": -10, "tag": "止損勇士"},
                "💡 **平民學術小課堂【處置效應：為甚麼割肉比挨打還難？】**\n\n"
                "行為金融學發現，人在**割肉（止損）**時肉疼的感覺，是拿到同等收益喜悅感的 **2 倍**！這叫『損失厭惡』。很多人就是因為不想承認虧損，死扛到底，結果把小傷口拖成了重症ICU。**止損不是認輸，而是給本金買一封保險**！"
            ),
            (
                "🎲 借錢加碼：賭一把 V 型反彈",
                {"wealth": +30 if random.random() > 0.7 else -35, "health": -20, "happiness": -20, "tag": "激進賭徒"},
                "💡 **平民學術小課堂【槓桿與過度自信：別把運氣當實力】**：\n\n"
                "借錢炒股（加槓桿）就像在跑車上裝火箭推進器——路況好時飛快，稍微碰到一粒沙子（市場波動）就會粉身碎骨。心理學上的『過度自信偏差』會讓人誤以為自己是股神，但金融學告訴我們：**在極端行情面前，死掉的往往都是膽子最大的那批人**。"
            )
        ]
    },
    {
        "title": "⚡ 🎁 突發事件：觀塘投注站驚喜！",
        "desc": "下班路過投注站，你用剩餘的零錢買了一張六合彩，居然幸運中獎！",
        "emoji": "🎉🎰💰",
        "options": [
            (
                "💰 穩健存入：配置高息定存與指數基金",
                {"wealth": +35, "health": 0, "happiness": +15, "tag": "幸運兒"},
                "💡 **平民學術小課堂【資產配置：把運氣變成底氣】**：\n\n"
                "現代投資組合理論（MPT）聽起來高大上，大白話就是**『不要把雞蛋放在一個籃子裡』**。意外中獎叫『偏財』，如果不趕緊把它存成能生利息的『硬通貨』，人的『心理帳戶』就會覺得这錢是白來的，很快就會揮霍光。"
            ),
            (
                "🎉 狂歡揮霍：請全公司吃大餐買奢品",
                {"wealth": +5, "health": +10, "happiness": +40, "tag": "揮金如土"},
                "💡 **平民學術小課堂【享樂跑步機：為甚麼爽感總是那麼短暫？】**：\n\n"
                "經濟學叫『邊際效用遞減』，心理學叫『享樂跑步機』——第一口龍蝦最美味，吃完一整桌也就那麼回事了。買奢侈品的快樂往往只能維持三天，但空掉的銀行帳戶卻需要你打工三個月來補。"
            )
        ]
    }
]

MAIN_EVENTS = [
    {
        "age": 18,
        "title": "📍 第一關：【18歲】出身背景與人生起跑線",
        "desc": "人生重開！你的初始數值均為 0。請選擇你的出生背景：",
        "emoji": "🎓📚🎒",
        "options": [
            ("🏠 公屋學霸：憑努力考上大學，兼職賺取學費", {"wealth": +10, "health": +40, "happiness": +30, "tag": "自立自強"}),
            ("💼 中產家庭：父母給了一筆啟動資金与創業資源", {"wealth": +45, "health": +30, "happiness": +20, "tag": "含金鑰匙"}),
            ("🎨 離島野孩子：熱愛自由與戶外運動，知足常樂", {"wealth": +0, "health": +65, "happiness": +45, "tag": "野性生長"}),
            ("💻 電競少年：迷戀網絡與直播，尋求新興賽道", {"wealth": +20, "health": -10, "happiness": +50, "tag": "網紅先鋒"})
        ]
    },
    {
        "age": 25,
        "title": "📍 第二關：【25歲】第一份工作與 MPF 配置",
        "desc": "入職打工，面對強積金（MPF）配置與僅存的薄薪：",
        "emoji": "👩‍💻💼📊",
        "options": [
            ("🔴 極度拼命：入職投行 996 拿命換高薪", {"wealth": +45, "health": -20, "happiness": -10, "tag": "中環社畜"}),
            ("🟡 穩紮穩打：配置保守型基金與高息定存", {"wealth": +20, "health": +10, "happiness": +15, "tag": "穩陣派"}),
            ("🟢 徹底躺平：人工全拿去旅遊活在當下", {"wealth": -10, "health": +20, "happiness": +35, "tag": "享樂主義"})
        ]
    },
    {
        "age": 35,
        "title": "📍 第三關：【35歲】置業抉擇：買樓定大灣區創業？",
        "desc": "積累了一定資金，面對香港高昂的樓價：",
        "emoji": "🏙️🗝️🏠",
        "options": [
            ("🔴 加槓桿買私樓：九成按揭做『樓奴』", {"wealth": -30, "health": -25, "happiness": -20, "tag": "樓奴"}),
            ("🟡 抽中居屋：買資助房屋，生活壓力適中", {"wealth": +25, "health": +10, "happiness": +20, "tag": "居屋業主"}),
            ("🎲 灣區創業大賭局：開連鎖港式茶餐廳", {"wealth": +55 if random.random() > 0.5 else -45, "health": -20, "happiness": -10, "tag": "灣區大亨"})
        ]
    },
    {
        "age": 50,
        "title": "📍 第四關：【50歲】唐樓收購與中年命運轉折",
        "desc": "繼承或買入的舊唐樓接到了強拍收購通知！",
        "emoji": "🏗️📜💵",
        "options": [
            ("💰 爽快簽字：拿一筆巨額現金徹底退休", {"wealth": +45, "health": +15, "happiness": +25, "tag": "拆遷暴發戶"}),
            ("🛑 極限當『釘子戶』：索要天價賠償", {"wealth": +75 if random.random() > 0.3 else -40, "health": -30, "happiness": -25, "tag": "釘子戶"}),
            ("🏠 換樓方案：直接換一套一手海景豪宅", {"wealth": +30, "health": +15, "happiness": +25, "tag": "豪宅業主"})
        ]
    },
    {
        "age": 65,
        "title": "📍 終極關卡：【65歲】提取 MPF 與退休告別",
        "desc": "65 歲正式退休！提取所有 MPF 強積金，迎接收盤...",
        "emoji": "🥂🌴🍵",
        "options": [
            ("🎉 盛大告別：舉辦派對宣告退休！", {"wealth": -5, "health": +15, "happiness": +25, "tag": "退休玩家"})
        ]
    }
]

# ==================== 核心選項處理 ====================
def process_option(effects, title_str, opt_str, feedback=None):
    for k, v in effects.items():
        if k in st.session_state.stats:
            st.session_state.stats[k] += v
        elif k == "tag":
            st.session_state.inventory.append(v)

    clamp_stats()

    clean_title = title_str.split("：")[0] if "：" in title_str else title_str
    clean_opt = opt_str.split("：")[0] if "：" in opt_str else opt_str
    st.session_state.log.append(f"{clean_title}：{clean_opt}")

    if feedback:
        st.session_state.modal_info = feedback
    else:
        if st.session_state.age_index + 1 < len(MAIN_EVENTS):
            st.session_state.age_index += 1
            if random.random() < 0.3:
                st.session_state.pending_rand_ev = random.choice(RANDOM_EVENTS)
        else:
            st.session_state.game_over = True

    if st.session_state.stats["health"] <= 0:
        st.session_state.game_over = True
        st.session_state.modal_info = None

    st.rerun()

# ==================== 結尾評估邏輯 ====================
def get_ending_type(w, h, p):
    """根據三大指標決定結局類型"""
    if h <= 0:
        return "bad"
    elif w >= 70 and h >= 50:
        return "legend"
    elif w >= 50 and h >= 30:
        return "good"
    else:
        return "normal"

def get_ending_info(ending_type, w, h, p):
    if ending_type == "bad":
        return {
            "tag_title": "💀【終局稱號：ICU 裡的富豪榜候補】",
            "end_emoji": "🏥💔💀",
            "poem": (
                "你透支了最寶貴的健康，去換取那冷冰冰的數字和中環高層寫字樓的虛榮！"
                "你總以為年輕就是資本，熬夜加班、高槓桿博弈、為了財富指標拼盡全力。"
                "結果命運直接給你按下『強制清算』！當你在病床上看著戶口餘額，才發現最昂貴的商品不是半山豪宅，而是私家醫院的 ICU 床位。"
            ),
            "motto": "『賺盡金山銀山，最後全送給保險公司與私家醫生。下輩子記住：健康才是唯一的槓桿！』",
            "effect": "sad",
            "color": "#ef4444"
        }
    elif ending_type == "legend":
        return {
            "tag_title": "👑【終局稱號：太平山頂地產霸權】",
            "end_emoji": "👑💰🏰",
            "poem": (
                "你在精明的算計與果斷的加槓桿中一路通關，登上了維港天花板！"
                "你把握住了香港資本市場的每一次脈搏，把強積金、股票、房產和現金流玩得爐火純青。"
                "地產商、券商和基金經理都成了你財富增值的工具。在繁華躁動的都市里，你用絕對的財富實力為自己打造了一座堅不可摧的護城河。"
            ),
            "motto": "『在香港，唯有資產的複利增長才能抵禦通脹與歲月的侵蝕。慶祝吧，傳奇的人生！』",
            "effect": "champagne",
            "color": "#FFD700"
        }
    elif ending_type == "good":
        return {
            "tag_title": "🥂【終局稱號：人生贏家】",
            "end_emoji": "🥂🌴🏖️",
            "poem": (
                "你在精明的算計與果斷的加槓桿中一路通關，收穨了豐碩的果實！"
                "你把握住了香港資本市場的每一次脈搏，把強積金、股票、房產和現金流玩得爐火純青。"
                "在繁華躁動的都市里，你用絕對的財富實力為自己打造了一座堅不可摧的護城河。"
            ),
            "motto": "『在香港，唯有資產的複利增長才能抵禦通脹與歲月的侵蝕。慶祝吧，人生贏家！』",
            "effect": "champagne",
            "color": "#22c55e"
        }
    else:
        return {
            "tag_title": "🌱【終局稱號：獅子山下踏實小市民】",
            "end_emoji": "☕🌱🏡",
            "poem": (
                "你避開了金融海嘯的致命打擊，也沒有盲目加槓桿成為樓奴。"
                "在急功近利的都市節奏中，你選擇了一條最平穩的道路：按時交 MPF、不沾高風險槓桿、有空去離島散心、偶爾抽一張六合彩。"
                "你沒有登上富豪榜，但也沒落得破產下場。平平淡淡，踏踏實實，你在繁華躁動的都市裡守住了一方屬於自己的寧靜天地。"
            ),
            "motto": "『做人嘛，最緊要係開心！平平淡淡才是真，煮碗麵大家一齊吃。』",
            "effect": "champagne",
            "color": "#83c5be"
        }

# ==================== 頁面渲染 ====================

# ---------- PAGE 1: 首頁 ----------
def page_intro():
    st.markdown("<h1 class='big-title' style='text-align: center;'>🎲 理財人生重開模擬器</h1>", unsafe_allow_html=True)

    st.markdown("""
    <div class="gold-card">
        <div class="sticker-icon" style="font-size:80px;">🎲 💼 📊 🏙️</div>
        <p style="font-size:20px; color:#FFD700; font-weight:700; margin-top:10px;">點擊不同文字選項，選擇不同人生軌跡<br>看看你是否可以成為人生贏家！</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 二维码區域
    st.markdown("<h3 style='text-align: center; color: #FFD700;'>📱 掃碼手機遊玩</h3>", unsafe_allow_html=True)
    game_url = "https://hk-life-simulator.streamlit.app"
    qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={game_url}"
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.image(qr_api_url, caption="手機掃碼直接玩", width=180)

    st.divider()
    if st.button("🚀 開始遊玩（重開人生）", use_container_width=True):
        go_page("rules")


# ---------- PAGE 2: 規則說明 ----------
def page_rules():
    st.markdown("<h1 class='big-title' style='text-align: center;'>📖 遊戲規則</h1>", unsafe_allow_html=True)
    st.divider()

    st.markdown("""
    <div class="gold-card">
        <p class="core-rule">👉 點擊不同文字選項，選擇不同人生軌跡<br>看看你是否可以成為人生贏家！</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="blue-card">
        <h3 style="color: #FFD700; margin-bottom: 10px;">🎯 遊戲目標</h3>
        <p>從 18 歲開始，一路走到 65 歲退休。在過程中你需要不斷做出選擇，每一個抉擇都會影響你的財富、健康與幸福，最終走向截然不同的結局。</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="blue-card">
        <h3 style="color: #FFD700; margin-bottom: 10px;">📊 三大核心數值</h3>
        <p><b style="color: #FFD700;">💰 財富值（0-100）</b>：你的資產累積程度，從打工薪水到投資回報，每一個決定都影響深淺。</p>
        <p><b style="color: #00D4FF;">❤️ 健康值（0-100）</b>：拼命工作、高槓桿投機、通宵加班都可能讓它驟降。<b style="color:#ef4444;">歸零即人生結束！</b></p>
        <p><b style="color: #FF8C00;">😊 幸福度（0-100）</b>：揮霍、躺平、收租、創業……不同選擇帶來不同的快樂指數。</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="blue-card">
        <h3 style="color: #FFD700; margin-bottom: 10px;">⚙️ 玩法說明</h3>
        <p>① 每關會出現 3-4 個選項，<b>點擊即可做出選擇</b>，數值即時變化</p>
        <p>② 旅途中可能隨機觸發 <b>突發事件</b>（如港股跳水、六合彩中獎），考驗你的應變能力</p>
        <p>③ 健康值歸零，或走完所有關卡即為結局</p>
        <p>④ 不同結局會有不同的稱號與故事結局，探索你的最優人生！</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    if st.button("✅ 準備開始", use_container_width=True):
        go_page("guide")


# ---------- PAGE 3: 引導語 ----------
def page_guide():
    st.markdown("<h1 class='sub-title' style='text-align: center;'>✨ 即將開始你的財富之旅 ✨</h1>", unsafe_allow_html=True)
    st.divider()

    st.markdown("""
    <div class="gold-card" style="box-shadow: 0 0 50px rgba(255,215,0,0.35);">
        <div class="sticker-icon" style="font-size:80px;">🎲 💼 📊 🏙️</div>
        <h2 style="color: #FFD700; margin-top: 15px;">開啟你的財富之旅吧！</h2>
        <p style="font-size: 18px; color: #e8e8e8;">從這一刻起，你的每一個選擇都將改寫人生軌跡</p>
        <p style="font-size: 16px; color: #aaa;">準備好接受挑戰了嗎？</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    with st.spinner("正在準備人生模擬器..."):
        st.write("")
        st.write("⏳ 正在初始化遊戲引擎...")
        st.write("⏳ 正在加載香港經濟數據...")
        st.write("⏳ 正在生成你的獨特人生軌跡...")

    if st.button("🎉 開始人生模擬！", use_container_width=True):
        # 初始化遊戲狀態
        st.session_state.stats = {"wealth": 0, "health": 0, "happiness": 0}
        st.session_state.age_index = 0
        st.session_state.inventory = []
        st.session_state.log = []
        st.session_state.modal_info = None
        st.session_state.pending_rand_ev = None
        st.session_state.game_over = False
        st.session_state.ending_type = None
        go_page("playing")


# ---------- PAGE 4: 核心遊戲 ----------
def page_playing():
    st.title("🎲 理財人生重開模擬器")
    stats = st.session_state.stats

    # 頂部數值欄
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 財富值", f"{stats['wealth']}/100")
    c2.metric("❤️ 健康值", f"{stats['health']}/100")
    c3.metric("😊 幸福度", f"{stats['happiness']}/100")
    st.divider()

    if not st.session_state.game_over:
        # 突發事件結算
        if st.session_state.modal_info:
            st.warning("🔔【突發事件結算與理財小課堂】")
            st.markdown(st.session_state.modal_info)
            st.write("")
            if st.button("🙋‍♂️ 我明白這個道理了，繼續人生", use_container_width=True, type="primary"):
                st.session_state.modal_info = None
                st.session_state.pending_rand_ev = None
                if st.session_state.age_index + 1 < len(MAIN_EVENTS):
                    st.session_state.age_index += 1
                else:
                    st.session_state.game_over = True
                st.rerun()

        # 突發事件
        elif st.session_state.pending_rand_ev:
            ev = st.session_state.pending_rand_ev
            st.error(ev['title'])
            st.write(ev["desc"])
            if "emoji" in ev:
                st.markdown(f"""
                <div class="sticker-box">
                    <div class="sticker-icon">{ev["emoji"]}</div>
                </div>
                """, unsafe_allow_html=True)
            st.write("")
            for idx, (opt_text, effects, feedback) in enumerate(ev["options"]):
                if st.button(opt_text, key=f"r_btn_{idx}", use_container_width=True):
                    process_option(effects, "突發事件", opt_text, feedback)

        # 主事件
        else:
            event = MAIN_EVENTS[st.session_state.age_index]
            st.subheader(event["title"])
            st.write(event["desc"])
            if "emoji" in event:
                st.markdown(f"""
                <div class="sticker-box">
                    <div class="sticker-icon">{event["emoji"]}</div>
                </div>
                """, unsafe_allow_html=True)
            st.write("")
            for idx, (opt_text, effects) in enumerate(event["options"]):
                if st.button(opt_text, key=f"m_btn_{st.session_state.age_index}_{idx}", use_container_width=True):
                    process_option(effects, event["title"], opt_text)

    # 遊戲結算
    else:
        ending_type = get_ending_type(
            st.session_state.stats["wealth"],
            st.session_state.stats["health"],
            st.session_state.stats["happiness"]
        )
        ending = get_ending_info(ending_type,
            st.session_state.stats["wealth"],
            st.session_state.stats["health"],
            st.session_state.stats["happiness"])

        # ========== 🎉 用戶要求的 champagne 慶祝特效 ==========
        if ending["effect"] == "champagne":
            st.balloons()
            st.markdown("""
            <div style='text-align:center; margin: 15px 0;'>
                <span style='font-size: 56px;'>🎆🍾🎇🥂🎉👑</span>
            </div>
            <h2 style='text-align:center; color:#FFD700; text-shadow: 0 0 20px rgba(255,215,0,0.8);'>
                🎊 傳奇人生達成！🎊
            </h2>
            """, unsafe_allow_html=True)
        elif ending["effect"] == "sad":
            st.snow()
        # ========== /champagne 慶祝特效 ==========

        st.header("🏆 終局算帳與深度人生圖鑑")

        w, h, p = st.session_state.stats["wealth"], st.session_state.stats["health"], st.session_state.stats["happiness"]

        # 結局卡片（HTML 完整閉合）
        st.markdown(f"""
        <div class="gold-card" style="border-color: {ending['color']}; box-shadow: 0 0 40px {ending['color']}60;">
            <div class="sticker-icon" style="font-size:80px;">{ending['end_emoji']}</div>
            <h2 style="color: {ending['color']}; margin-top: 15px;">{ending['tag_title']}</h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📜 人生深度判詞")
        st.markdown(ending["poem"])
        st.write("")

        # 柱狀圖
        st.markdown("### 📊 終局數據分析")
        df = pd.DataFrame({
            "屬性": ["財富值 💰", "健康值 ❤️", "幸福度 😊"],
            "數值": [w, h, p]
        })
        chart = alt.Chart(df).mark_bar(color=ending['color']).encode(
            x=alt.X('屬性:N', axis=alt.Axis(labelAngle=0, title=None, labelFontSize=14)),
            y=alt.Y('數值:Q', scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(title="數值")),
            tooltip=['屬性', '數值']
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)

        st.markdown(f"**💬 處世名言**：{ending['motto']}")

        st.markdown("---")
        st.markdown("#### 🏷️ 解鎖的人生成就標籤")
        if st.session_state.inventory:
            tags_html = " ".join([f"`{tag}`" for tag in set(st.session_state.inventory)])
            st.markdown(tags_html)
        else:
            st.caption("未獲得特殊標籤")

        st.markdown("---")
        st.markdown("#### 📜 人生重要抉擇軌跡")
        for idx, item in enumerate(st.session_state.log, 1):
            st.caption(f"{idx}. {item}")

        st.divider()
        if st.button("🔄 重新重開人生", use_container_width=True, type="primary"):
            restart_game()


# ==================== 主流程路由 ====================
# 統一兜底初始化：防止直接訪問 playing 頁面時缺少 key 報 AttributeError
if "stats" not in st.session_state:
    st.session_state.stats = {"wealth": 0, "health": 0, "happiness": 0}
if "age_index" not in st.session_state:
    st.session_state.age_index = 0
if "inventory" not in st.session_state:
    st.session_state.inventory = []
if "log" not in st.session_state:
    st.session_state.log = []
if "modal_info" not in st.session_state:
    st.session_state.modal_info = None
if "pending_rand_ev" not in st.session_state:
    st.session_state.pending_rand_ev = None
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "ending_type" not in st.session_state:
    st.session_state.ending_type = None
if "page" not in st.session_state:
    st.session_state.page = "intro"

# 確保 stats 內部字段完整
for attr in ("wealth", "health", "happiness"):
    st.session_state.stats.setdefault(attr, 0)

page = st.session_state.page
if page == "intro":
    page_intro()
elif page == "rules":
    page_rules()
elif page == "guide":
    page_guide()
elif page == "playing":
    page_playing()
else:
    page_intro()

# ==================== 底部 ====================
st.divider()
st.markdown("<p style='text-align: center; font-size: 12px; color: rgba(255,255,255,0.3);'>理財人生重開模擬器 © 2025 | 僅供娛樂與教育用途</p>", unsafe_allow_html=True)
