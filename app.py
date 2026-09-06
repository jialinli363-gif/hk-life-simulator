"""
HK Life Simulator —— 香港人生模拟器
基于 Streamlit 的交互式人生模拟小游戏
"""

import streamlit as st
import random
import time

# ==================== 页面基础设置 ====================
st.set_page_config(page_title="香港人生模擬器", page_icon="🧭", layout="centered")

# ==================== 结局配置 ====================
# 每个结局决定玩家最终的命运和评语
ENDINGS = {
    "legend": {
        "type": "legend",
        "end_emoji": "🏅",
        "tag_title": "人生大贏家",
        "color": "#FFD700",
        "description": "你的人生堪稱傳奇：事業有成、家庭美滿、身心康泰，是典型的香港 success story。",
        "life_comment": "傳說級別的人生。你在事業、健康與家庭之間找到了完美的平衡，是無數港人夢寐以求的樣子。保持下去，這份光榮將延續下去。"
    },
    "rich_tired": {
        "type": "legend",
        "end_emoji": "💼",
        "tag_title": "錢王械巢",
        "color": "#4A90D9",
        "description": "你富可敵國，但健康告警，提醒你錢不是一切。",
        "life_comment": "金錢是你最好的朋友，也是最大的敵人。事業成就驚人，但别忘了健康纔是真正的財富。適度放慢腳步吧。"
    },
    "family_first": {
        "type": "tragic",
        "end_emoji": "👨‍👩‍👧‍👦",
        "tag_title": "幸福家人",
        "color": "#E91E63",
        "description": "你過著平凡但溫暖的家庭生活，人生圓滿。",
        "life_comment": "簡單就是幸福。你不富裕，但家人彼此相愛、健康平安，這份溫暖比任何物質都珍貴。你已經贏了。"
    },
    "street_smart": {
        "type": "tragic",
        "end_emoji": "🧧",
        "tag_title": "街頭傳奇",
        "color": "#9C27B0",
        "description": "你混得風生水起，但健康和家都已經失去。",
        "life_comment": "你在街頭贏得了尊重，但回首一看，健康與家庭都已不在。成功是有代價的，下次記得留點時間給自己。"
    },
    "quiet_life": {
        "type": "tragic",
        "end_emoji": "🍵",
        "tag_title": "從此平靜",
        "color": "#607D8B",
        "description": "你選擇了平淡而從容的人生，與世無爭。",
        "life_comment": "不爭不搶，逍遙自在。雖然沒有轟轟烈烈，但平靜本身就是一種成功。人生何必都是奔跑？"
    },
    "fallen": {
        "type": "tragic",
        "end_emoji": "📉",
        "tag_title": "跌入深淵",
        "color": "#F44336",
        "description": "一切都很糟糕，事業失敗、健康透支、幸福歸零。",
        "life_comment": "低谷不可怕，可怕的是不再想爬起來。人生總有重新開始的機會，下一次，會不一樣的。"
    },
}


def get_ending_info():
    """根據當前 stats 決定結局"""
    w, h, p = st.session_state.stats["wealth"], st.session_state.stats["health"], st.session_state.stats["happiness"]

    if w >= 80 and h >= 70 and p >= 70:
        return ENDINGS["legend"]
    elif w >= 80 and h < 50:
        return ENDINGS["rich_tired"]
    elif h >= 70 and p >= 70 and w < 50:
        return ENDINGS["family_first"]
    elif w >= 70 and h < 40 and p < 40:
        return ENDINGS["street_smart"]
    elif w < 35 and h >= 60 and p >= 50:
        return ENDINGS["quiet_life"]
    else:
        return ENDINGS["fallen"]


# ==================== 遊戲事件庫 ====================
# 每個事件：title 標題、text 描述、choices 選項列表（每個含 label 和效果）
EVENTS = [
    {
        "title": "🏢 大灣區商機",
        "text": "朋友圈傳來消息：深圳灣那邊有一個超級大單，把握住就能財富自由。但要跑去深圳跑一週，你的健康要付出代價。",
        "choices": [
            {"label": "🚀 衝！拿大單要緊（財富+15，健康-10，快樂-5）",
             "effect": {"wealth": 15, "health": -10, "happiness": -5}},
            {"label": "🤝 慢慢談，健康第一（財富+5，健康+0，快樂+5）",
             "effect": {"wealth": 5, "health": 0, "happiness": 5}},
        ],
    },
    {
        "title": "🍜 食飯難題",
        "text": "中午餓了。外賣十七塊牛肉麵很方便但偏鹹，回家煮個煲仔飯要一個鐘頭但較健康。",
        "choices": [
            {"label": "🍜 外賣牛肉麵（快樂+8，健康-6）",
             "effect": {"wealth": -5, "health": -6, "happiness": 8}},
            {"label": "🍚 回家煲仔飯（健康+8，快樂+3，花費+10）",
             "effect": {"wealth": -10, "health": 8, "happiness": 3}},
        ],
    },
    {
        "title": "💊 最後一餐",
        "text": "你突然沒胃口，身體又開始報警。家人逼你去看醫生，但看醫生要排隊好久。",
        "choices": [
            {"label": "🏥 去看醫生（健康+12，快樂-5，財富-8）",
             "effect": {"wealth": -8, "health": 12, "happiness": -5}},
            {"label": "💊 自行吃藥硬撐（健康+3，快樂-3）",
             "effect": {"wealth": 0, "health": 3, "happiness": -3}},
        ],
    },
    {
        "title": "🎮 通宵打機",
        "text": "週末終於可以放棄。朋友邀請你通宵開黑，還有奶茶。爽！但明早要上班。",
        "choices": [
            {"label": "🎮 通宵開黑（快樂+15，健康-8，財富-3）",
             "effect": {"wealth": -3, "health": -8, "happiness": 15}},
            {"label": "😴 老實睡覺（健康+6，快樂+4）",
             "effect": {"wealth": 0, "health": 6, "happiness": 4}},
        ],
    },
    {
        "title": "📈 基金漲了",
        "text": "戶口裡的股票基金突然大漲，賺了一筆。要不拿去投資更好項目？",
        "choices": [
            {"label": "💰 落袋為安（財富+10，快樂+5）",
             "effect": {"wealth": 10, "health": 0, "happiness": 5}},
            {"label": "📊 再投資衝更高（財富+20，健康-3，快樂-3）",
             "effect": {"wealth": 20, "health": -3, "happiness": -3}},
        ],
    },
    {
        "title": "👨‍👩‍👧‍👦 家人約飯",
        "text": "老媽突然約你週日晚飯，說是為了看看你。一家人團聚的機會不多了。",
        "choices": [
            {"label": "🍲 回家吃飯（健康+5，快樂+12，財富-5）",
             "effect": {"wealth": -5, "health": 5, "happiness": 12}},
            {"label": "📱 忙，改天（快樂-8，健康+0）",
             "effect": {"wealth": 0, "health": 0, "happiness": -8}},
        ],
    },
    {
        "title": "🧹 租約到期",
        "text": "租的唐樓租約快到期了。老闆說可以續租，但要加租兩成。住還是走？",
        "choices": [
            {"label": "🏠 續租（財富-12，快樂+3，健康+3）",
             "effect": {"wealth": -12, "health": 3, "happiness": 3}},
            {"label": "🚶 搬去內地城市（財富+15，快樂-5，健康+5）",
             "effect": {"wealth": 15, "health": 5, "happiness": -5}},
        ],
    },
    {
        "title": "🧧 大獎降臨",
        "text": "老闆突然宣佈今年分紅破紀錄，大家都有獎金！你猜幾率如何？",
        "choices": [
            {"label": "🤞 領獎金爽一晚（財富+12，快樂+10，健康-4）",
             "effect": {"wealth": 12, "health": -4, "happiness": 10}},
            {"label": "💹 拿獎金投資（財富+20，快樂+2）",
             "effect": {"wealth": 20, "health": 0, "happiness": 2}},
        ],
    },
    {
        "title": "🏋️ 健身卡",
        "text": "朋友勸你辦健身卡，說運動是長壽秘訣。但健身月費不便宜。",
        "choices": [
            {"label": "💪 辦卡鍛鍊（健康+12，快樂+5，財富-10）",
             "effect": {"wealth": -10, "health": 12, "happiness": 5}},
            {"label": "🚶 散步就算了（健康+3，快樂+0）",
             "effect": {"wealth": 0, "health": 3, "happiness": 0}},
        ],
    },
    {
        "title": "🐶 寵物困擾",
        "text": "家人要給你買隻狗，但照顧狗狗又要時間又要錢，你不一定答應得了。",
        "choices": [
            {"label": "🐕 收下！超開心（快樂+12，健康+3，財富-5）",
             "effect": {"wealth": -5, "health": 3, "happiness": 12}},
            {"label": "🙅 沒空照顧（快樂-3，財富+0）",
             "effect": {"wealth": 0, "health": 0, "happiness": -3}},
        ],
    },
    {
        "title": "📜 中年危機",
        "text": "刷到同事升級、自己原地踏步的新聞，突然很不安全。要不要換跑道？",
        "choices": [
            {"label": "🚀 去考個證書進修（財富-15，健康-3，快樂-5，長期+10）",
             "effect": {"wealth": -15, "health": -3, "happiness": -5}},
            {"label": "🧘 想開點，做好本職（快樂+5，健康+2）",
             "effect": {"wealth": 0, "health": 2, "happiness": 5}},
        ],
    },
    {
        "title": "🛒 雙11剁手",
        "text": "雙十一來了， shopping 網站滿減轟炸。理性還是衝動？",
        "choices": [
            {"label": "🛍️ 該買的都買（財富-18，快樂+10）",
             "effect": {"wealth": -18, "health": 0, "happiness": 10}},
            {"label": "🧊 只買生活必需品（財富-3，快樂+2）",
             "effect": {"wealth": -3, "health": 0, "happiness": 2}},
        ],
    },
]


# ==================== 頁面渲染 ====================
def page_intro():
    st.title("🧭 香港人生模擬器")
    st.subheader("HK Life Simulator")
    st.write("""
    歡迎來到 **香港人生模擬器**！🇭🇰

    這是一個簡單有趣的人生模擬小遊戲。你將扮演一位香港年輕人，
    從 **25 歲**開始，經歷 **30 年 / 30 次人生抉擇**。

    ### 🎯 遊戲目標
    在 **財富、健康、幸福** 三個維度上，追求你心中最理想的人生平衡。

    每一個選擇都會影響你的命運，30 年後，等待你的會是什麼結局呢？
    """)

    st.info("💡 提示：每個選項都會改變你的財富、健康和幸福指數，量力而行！")

    if st.button("🚀 開始我的人生", use_container_width=True):
        st.session_state.page = "playing"
        st.session_state.year = 25
        st.session_state.stats = {"wealth": 50, "health": 50, "happiness": 50}
        st.session_state.event_idx = 0
        st.rerun()


def page_playing():
    # 頂部狀態欄
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📅 年齡", f"{st.session_state.year} 歲")
    col2.metric("💰 財富", st.session_state.stats["wealth"])
    col3.metric("❤️ 健康", st.session_state.stats["health"])
    col4.metric("😊 幸福", st.session_state.stats["happiness"])

    st.markdown("---")

    # 取得當前事件
    idx = st.session_state.event_idx % len(EVENTS)
    event = EVENTS[idx]

    st.markdown(f"### {event['title']}")
    st.write(event["text"])

    st.markdown("---")

    # 選項按鈕
    for i, choice in enumerate(event["choices"]):
        if st.button(choice["label"], key=f"choice_{i}", use_container_width=True):
            # 套用效果
            s = st.session_state.stats
            s["wealth"] = max(0, min(100, s["wealth"] + choice["effect"]["wealth"]))
            s["health"] = max(0, min(100, s["health"] + choice["effect"]["health"]))
            s["happiness"] = max(0, min(100, s["happiness"] + choice["effect"]["happiness"]))
            st.session_state.event_idx += 1
            st.rerun()

    # 若已到第30年，提供結局
    if st.session_state.year >= 55:
        st.markdown("---")
        st.warning("🎉 你的 30 年人生即將走到終點...")
        if st.button("🏁 查看最終結局", use_container_width=True):
            st.session_state.page = "game_over"
            st.rerun()


def page_game_over():
    ending = get_ending_info()
    stats = st.session_state.stats

    # 結局特效
    if ending["type"] == "legend":
        st.balloons()
    elif ending["type"] == "tragic":
        st.snow()

    # 結局卡片
    st.markdown(f"""
    <div class="gold-card" style="border-color: {ending['color']}; box-shadow: 0 0 40px {ending['color']}60;">
        <div class="sticker-icon" style="font-size:80px;">{ending['end_emoji']}</div>
        <h2 style="color: {ending['color']}; margin-top: 15px;">{ending['tag_title']}</h2>
        <p style="font-size:18px; color:#444;">{ending['description']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.header("🏆 終局算帳與深度人生圖鑑")
    w, h, p = stats["wealth"], stats["health"], stats["happiness"]

    st.markdown(f"""
    <div class="gold-card">
        <h3>📊 人生三大維度</h3>
        <p>💰 財富指數：{w}  ❤️ 健康指數：{h}  😊 幸福指數：{p}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="gold-card">
        <h3>📜 人生圖鑑評語</h3>
        <p>{ending['life_comment']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔄 重新開啟財富之旅", use_container_width=True):
        st.session_state.page = "intro"
        st.session_state.stats = {"wealth": 50, "health": 50, "happiness": 50}
        st.session_state.event_idx = 0
        st.rerun()


# ==================== 全局 CSS 樣式 ====================
st.markdown("""
<style>
.gold-card {
    background: linear-gradient(135deg, #fff8e1 0%, #fffde7 100%);
    border: 2px solid #FFD700;
    border-radius: 16px;
    padding: 28px;
    margin: 16px 0;
    text-align: center;
}
.gold-card h2 { font-size: 28px; margin-bottom: 12px; }
.gold-card h3 { font-size: 20px; margin-bottom: 10px; color: #333; }
.gold-card p { font-size: 16px; color: #555; line-height: 1.7; }
.sticker-icon { font-size: 72px; line-height: 1; }
</style>
""", unsafe_allow_html=True)

# ==================== 主流程 ====================
# 初始化 session_state
if "page" not in st.session_state:
    st.session_state.page = "intro"
if "stats" not in st.session_state:
    st.session_state.stats = {"wealth": 50, "health": 50, "happiness": 50}
if "event_idx" not in st.session_state:
    st.session_state.event_idx = 0

if st.session_state.page == "intro":
    page_intro()
elif st.session_state.page == "playing":
    page_playing()
elif st.session_state.page == "game_over":
    page_game_over()

