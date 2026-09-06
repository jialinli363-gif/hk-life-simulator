import streamlit as st
import random
import pandas as pd
import altair as alt

# 1. 頁面基本配置
st.set_page_config(
    page_title="理財人生重開模擬器", 
    page_icon="🎲", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 安全 CSS 與大 Emoji 貼圖卡片樣式
st.markdown("""
<style>
    div[data-testid="stException"],
    .element-container:has(.stException) {
        display: none !important;
    }
    .stApp {
        background-color: #0e1117;
    }
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #FFD700 !important;
    }
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        padding: 10px 15px;
        font-weight: 600;
    }
    /* 大 Emoji 貼圖卡片 */
    .sticker-box {
        background: linear-gradient(135deg, #1e222d 0%, #2a3040 100%);
        border: 2px solid #3d4455;
        border-radius: 16px;
        padding: 15px;
        text-align: center;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .sticker-icon {
        font-size: 64px;
        line-height: 1.2;
    }
</style>
""", unsafe_allow_html=True)

# 3. 初始化 Session 狀態
if "game_started" not in st.session_state:
    st.session_state.game_started = False
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

def clamp_stats():
    for key in ["wealth", "health", "happiness"]:
        st.session_state.stats[key] = max(0, min(100, st.session_state.stats[key]))

def restart_game():
    st.session_state.stats = {"wealth": 0, "health": 0, "happiness": 0}
    st.session_state.age_index = 0
    st.session_state.inventory = []
    st.session_state.log = []
    st.session_state.modal_info = None
    st.session_state.pending_rand_ev = None
    st.session_state.game_over = False
    st.session_state.game_started = False
    st.rerun()

# --- 數據庫（含精煉通俗的學術科普）---
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
                {"wealth": +35, "health": +0, "happiness": +15, "tag": "幸運兒"},
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

# --- 核心選項處理 ---
def process_option(effects, title_str, opt_str, feedback=None):
    for k, v in effects.items():
        if k in st.session_state.stats:
            st.session_state.stats[k] += v
        elif k == "tag":
            st.session_state.inventory.append(v)
            
    clamp_stats()
    
    clean_title = title_str.split("：")[0]
    clean_opt = opt_str.split("：")[0]
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

# ==================== UI 渲染 ====================
if not st.session_state.game_started:
    st.markdown("<h1 style='text-align: center;'>🎲 理財人生重開模擬器</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sticker-box">
        <div class="sticker-icon">🎲 💼 📊 🏙️</div>
    </div>
    """, unsafe_allow_html=True)
        
    st.divider()
    st.markdown("《理財人生重開模擬器》是一款以香港都市生活為背景的模擬經營遊戲。體驗 MPF 配置、買樓、創業等抉擇！")
    st.write("")
    if st.button("🚀 開始遊玩 (重開人生)", type="primary"):
        st.session_state.game_started = True
        st.rerun()

else:
    st.title("🎲 理財人生重開模擬器")
    stats = st.session_state.stats
    
    # 頂部數值欄
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 財富值", f"{stats['wealth']}/100")
    c2.metric("❤️ 健康值", f"{stats['health']}/100")
    c3.metric("😊 幸福度", f"{stats['happiness']}/100")
    st.divider()

    # 1. 遊戲未結束
    if not st.session_state.game_over:
        if st.session_state.modal_info:
            st.warning("🔔【突發事件結算与理財小課堂】")
            st.markdown(st.session_state.modal_info)
            st.write("")
            if st.button("🙋‍♂️ 我明白這個道理了，繼續人生"):
                st.session_state.modal_info = None
                st.session_state.pending_rand_ev = None
                if st.session_state.age_index + 1 < len(MAIN_EVENTS):
                    st.session_state.age_index += 1
                else:
                    st.session_state.game_over = True
                st.rerun()

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
                if st.button(opt_text, key=f"r_btn_{idx}"):
                    process_option(effects, "突發事件", opt_text, feedback)

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
                if st.button(opt_text, key=f"m_btn_{st.session_state.age_index}_{idx}"):
                    process_option(effects, event["title"], opt_text)

    # 2. 遊戲結算界面
    else:
        st.balloons()
        
        st.header("🏆 終局算帳與深度人生圖鑑")
        
        w, h, p = stats["wealth"], stats["health"], stats["happiness"]

        if h <= 0:
            tag_title = "💀【終局稱號：ICU 裡的富豪榜候補】"
            end_emoji = "🏥💔💀"
            poem = (
                "你透支了最寶貴的健康，去換取那冷冰冰的數字和中環高層寫字樓的虛榮！"
                "你總以為年輕就是資本，熬夜加班、高槓桿博弈、為了財富指標拼盡全力。"
                "結果命運直接給你按下『強制清算』！當你在病床上看著戶口餘額，才發現最昂貴的商品不是半山豪宅，而是私家醫院的 ICU 床位。"
            )
            motto = "『賺盡金山銀山，最後全送給保險公司與私家醫生。下輩子記住：健康才是唯一的槓桿！』"
        elif w >= 70:
            tag_title = "👑【終局稱號：太平山頂地產霸權】"
            end_emoji = "👑💰🏰"
            poem = (
                "你在精明的算計與果斷的加槓桿中一路通關，登上了維港天花板！"
                "你把握住了香港資本市場的每一次脈搏，把強積金、股票、房產和現金流玩得爐火純青。"
                "地產商、券商和基金經理都成了你財富增值的工具。在繁華躁動的都市里，你用絕對的財富實力為自己打造了一座堅不可摧的護城河。"
            )
            motto = "『在香港，唯有資產的複利增長才能抵禦通脹與歲月的侵蝕。』"
        else:
            tag_title = "🌱【終局稱號：獅子山下踏實小市民】"
            end_emoji = "☕🌱🏡"
            poem = (
                "你避開了金融海嘯的致命打擊，也沒有盲目加槓桿成為樓奴。"
                "在急功近利的都市節奏中，你選擇了一條最平穩的道路：按時交 MPF、不沾高風險槓桿、有空去離島散心、偶爾抽一張六合彩。"
                "你沒有登上富豪榜，但也沒落得破產下場。平平淡淡，踏踏實實，你在繁華躁動的都市裡守住了一方屬於自己的寧靜天地。"
            )
            motto = "『做人嘛，最緊要係開心！平平淡淡才是真，煮碗麵大家一齊吃。』"

        st.error(f"{tag_title}")

        st.markdown(f"""
        <div class="sticker-box">
            <div class="sticker-icon">{end_emoji}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📜 人生深度判詞")
        st.markdown(f"{poem}")
        st.write("")

        # 使用 Altair 生成横轴标签水平不旋转（0度）的柱状图
        st.markdown("### 📊 終局數據分析")
        df = pd.DataFrame({
            "屬性": ["財富值 💰", "健康值 ❤️", "幸福度 😊"],
            "數值": [w, h, p]
        })
        chart = alt.Chart(df).mark_bar(color='#83c5be').encode(
            x=alt.X('屬性:N', axis=alt.Axis(labelAngle=0, title=None, labelFontSize=14)),
            y=alt.Y('數值:Q', scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(title="數值")),
            tooltip=['屬性', '數值']
        ).properties(
            height=300
        )
        st.altair_chart(chart, use_container_width=True)

        st.markdown(f"**💬 處世名言**：{motto}")

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
        if st.button("🔄 重新重開人生", type="primary"):
            restart_game()
# ==================== 底部自动二维码生成 ====================
st.divider()
st.markdown("<h3 style='text-align: center;'>📱 扫码手机游玩</h3>", unsafe_allow_html=True)

# 自动获取当前部署后的真实 URL 地址
try:
    current_url = st.context.headers.get("referer", "https://share.streamlit.io")
except Exception:
    current_url = "https://share.streamlit.io"

qr = qrcode.QRCode(version=1, box_size=8, border=2)
qr.add_data(current_url)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")

buf = BytesIO()
img.save(buf, format="PNG")

c1, c2, c3 = st.columns([1, 1, 1])
with c2:
    st.image(buf.getvalue(), caption="手机扫码直接玩", width=180)


        