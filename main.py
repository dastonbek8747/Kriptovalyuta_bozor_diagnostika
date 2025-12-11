import streamlit as st
import ccxt
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Streamlit sahifa konfiguratsiyasi
st.set_page_config(page_title="Kripto Savdo Paneli", layout="wide", page_icon="📈")

# Stil va CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 20px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Asosiy sarlavha
st.markdown('<div class="main-header">🚀 Kriptovalyuta Savdo Platformasi</div>', unsafe_allow_html=True)

# Sidebar - Sozlamalar
st.sidebar.title("⚙️ Sozlamalar")

# Birja tanlash
exchanges_list = ['binance', 'bybit', 'okx', 'kraken', 'coinbase', 'kucoin']
selected_exchange = st.sidebar.selectbox("Birjani tanlang:", exchanges_list)


# CCXT birja obyektini yaratish
@st.cache_resource
def get_exchange(exchange_name):
    try:
        exchange_class = getattr(ccxt, exchange_name)
        return exchange_class({'enableRateLimit': True})
    except Exception as e:
        st.error(f"Birja yuklanmadi: {e}")
        return None


exchange = get_exchange(selected_exchange)

# Savdo juftligini tanlash
if exchange:
    try:
        markets = exchange.load_markets()
        popular_pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
                         'ADA/USDT', 'DOGE/USDT', 'MATIC/USDT', 'DOT/USDT', 'AVAX/USDT']
        available_pairs = [p for p in popular_pairs if p in markets]

        if not available_pairs:
            available_pairs = list(markets.keys())[:20]

        trading_pair = st.sidebar.selectbox("Savdo juftligini tanlang:", available_pairs)
    except Exception as e:
        st.error(f"Bozorlar yuklanmadi: {e}")
        trading_pair = 'BTC/USDT'
else:
    trading_pair = 'BTC/USDT'

# Vaqt oralig'i
timeframe = st.sidebar.selectbox("Vaqt oralig'i:",
                                 ['1m', '5m', '15m', '1h', '4h', '1d'])

# Tab'lar yaratish
tab1, tab2, tab3, tab4 = st.tabs(["📊 Bozor Ma'lumotlari", "📈 Tahlil", "🤖 Bot Sozlamalari", "📚 Strategiyalar"])

# TAB 1: Bozor Ma'lumotlari
with tab1:
    if exchange:
        try:
            # Joriy narx
            ticker = exchange.fetch_ticker(trading_pair)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Joriy Narx", f"${ticker['last']:,.2f}",
                          f"{ticker['percentage']:.2f}%")
            with col2:
                st.metric("24h Yuqori", f"${ticker['high']:,.2f}")
            with col3:
                st.metric("24h Past", f"${ticker['low']:,.2f}")
            with col4:
                st.metric("24h Hajm", f"${ticker['quoteVolume']:,.0f}")

            # OHLCV ma'lumotlari
            st.subheader("📊 Narx Grafigi")

            try:
                ohlcv = exchange.fetch_ohlcv(trading_pair, timeframe, limit=100)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

                # Candlestick grafik
                fig = go.Figure(data=[go.Candlestick(
                    x=df['timestamp'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Narx'
                )])

                fig.update_layout(
                    title=f'{trading_pair} Narx Grafigi ({timeframe})',
                    yaxis_title='Narx (USDT)',
                    xaxis_title='Vaqt',
                    height=500,
                    template='plotly_dark'
                )

                st.plotly_chart(fig, use_container_width=True)

                # Hajm grafigi
                fig_volume = go.Figure(data=[go.Bar(
                    x=df['timestamp'],
                    y=df['volume'],
                    name='Hajm',
                    marker_color='lightblue'
                )])

                fig_volume.update_layout(
                    title='Savdo Hajmi',
                    yaxis_title='Hajm',
                    xaxis_title='Vaqt',
                    height=300,
                    template='plotly_dark'
                )

                st.plotly_chart(fig_volume, use_container_width=True)

            except Exception as e:
                st.error(f"Grafik ma'lumotlari yuklanmadi: {e}")

            # Order Book
            st.subheader("📖 Order Book")
            try:
                orderbook = exchange.fetch_order_book(trading_pair, limit=10)

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Sotib olish buyurtmalari (Bids)**")
                    bids_df = pd.DataFrame(orderbook['bids'][:10], columns=['Narx', 'Miqdor'])
                    bids_df['Jami'] = bids_df['Narx'] * bids_df['Miqdor']
                    st.dataframe(bids_df, use_container_width=True)

                with col2:
                    st.write("**Sotish buyurtmalari (Asks)**")
                    asks_df = pd.DataFrame(orderbook['asks'][:10], columns=['Narx', 'Miqdor'])
                    asks_df['Jami'] = asks_df['Narx'] * asks_df['Miqdor']
                    st.dataframe(asks_df, use_container_width=True)

            except Exception as e:
                st.error(f"Order Book yuklanmadi: {e}")

        except Exception as e:
            st.error(f"Ma'lumotlar yuklanmadi: {e}")

# TAB 2: Tahlil
with tab2:
    st.subheader("📈 Texnik Tahlil")

    if exchange:
        try:
            ohlcv = exchange.fetch_ohlcv(trading_pair, timeframe, limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

            # Moving Averages
            df['MA_20'] = df['close'].rolling(window=20).mean()
            df['MA_50'] = df['close'].rolling(window=50).mean()

            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

            col1, col2, col3 = st.columns(3)

            with col1:
                current_price = df['close'].iloc[-1]
                ma20 = df['MA_20'].iloc[-1]
                st.metric("Joriy Narx", f"${current_price:.2f}")
                st.metric("MA(20)", f"${ma20:.2f}",
                          f"{((current_price - ma20) / ma20 * 100):.2f}%")

            with col2:
                ma50 = df['MA_50'].iloc[-1]
                st.metric("MA(50)", f"${ma50:.2f}",
                          f"{((current_price - ma50) / ma50 * 100):.2f}%")

            with col3:
                rsi = df['RSI'].iloc[-1]
                rsi_status = "Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral"
                st.metric("RSI(14)", f"{rsi:.2f}", rsi_status)

            # Signal
            st.subheader("🎯 Savdo Signali")

            if current_price > ma20 and current_price > ma50 and rsi < 70:
                st.success("✅ SOTIB OLISH SIGNALI: Narx MA ustida, RSI normal")
            elif current_price < ma20 and current_price < ma50 and rsi > 30:
                st.error("❌ SOTISH SIGNALI: Narx MA ostida, RSI normal")
            else:
                st.info("⏸️ KUTISH: Aniq signal yo'q")

        except Exception as e:
            st.error(f"Tahlil amalga oshmadi: {e}")

# TAB 3: Bot Sozlamalari
with tab3:
    st.subheader("🤖 Savdo Bot Sozlamalari")

    strategy = st.selectbox("Strategiyani tanlang:",
                            ["Grid Trading", "DCA Bot", "Simple MA Crossover", "RSI Strategy"])

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Asosiy Sozlamalar**")
        investment = st.number_input("Investitsiya miqdori (USDT):", min_value=10.0, value=100.0)
        risk_level = st.slider("Risk darajasi:", 1, 10, 5)
        take_profit = st.number_input("Take Profit (%):", min_value=0.1, value=2.0, step=0.1)
        stop_loss = st.number_input("Stop Loss (%):", min_value=0.1, value=1.0, step=0.1)

    with col2:
        st.write("**Strategiya Parametrlari**")
        if strategy == "Grid Trading":
            grid_levels = st.number_input("Grid darajalari:", min_value=3, value=10)
            price_range = st.slider("Narx oralig'i (%):", 1, 20, 5)
        elif strategy == "DCA Bot":
            buy_interval = st.selectbox("Sotib olish intervali:", ["1 soat", "4 soat", "1 kun"])
            amount_per_buy = st.number_input("Har bir sotib olish (USDT):", min_value=5.0, value=10.0)
        elif strategy == "Simple MA Crossover":
            fast_ma = st.number_input("Tez MA:", min_value=5, value=20)
            slow_ma = st.number_input("Sekin MA:", min_value=10, value=50)

    st.warning("⚠️ Diqqat: Bu demo versiya. Haqiqiy savdo uchun API kalitlarini sozlang.")

    if st.button("🚀 Botni Ishga Tushirish", type="primary"):
        st.success("✅ Bot muvaffaqiyatli ishga tushirildi!")
        st.info(f"Strategiya: {strategy}\nInvestitsiya: ${investment:.2f}")

# TAB 4: Strategiyalar
with tab4:
    st.subheader("📚 Savdo Strategiyalari")

    strategies_info = {
        "Grid Trading": {
            "tavsif": "Narx oralig'ida avtomatik ravishda sotib olish va sotish",
            "afzalliklar": "• Sideways bozorda yaxshi ishlaydi\n• Avtomatik foyda olish\n• Past riskli",
            "kamchiliklar": "• Trend bozorda past samaradorlik\n• Ko'p savdo komissiyalari",
            "ideal": "O'rtacha volatilitli bozorlar uchun"
        },
        "DCA (Dollar-Cost Averaging)": {
            "tavsif": "Ma'lum vaqt oralig'ida doimiy investitsiya qilish",
            "afzalliklar": "• Narx tebranishlarini kamaytiradi\n• Oddiy strategiya\n• Uzoq muddatli o'sish",
            "kamchiliklar": "• Sekin foyda\n• Tushuvchi bozorda zarar",
            "ideal": "Uzoq muddatli investorlar uchun"
        },
        "MA Crossover": {
            "tavsif": "Moving Average kesishishlarini kuzatish",
            "afzalliklar": "• Trend boshlanishini aniqlaydi\n• Oddiy signal\n• Keng qo'llaniladi",
            "kamchiliklar": "• Kechikish mavjud\n• Noto'g'ri signallar (whipsaws)",
            "ideal": "Trendli bozorlar uchun"
        },
        "RSI Strategy": {
            "tavsif": "Relative Strength Index asosida savdo",
            "afzalliklar": "• Oversold/Overbought aniqlash\n• Momentum o'lchash\n• Yaxshi timing",
            "kamchiliklar": "• Kuchli trendda zaif\n• Qo'shimcha tahlil kerak",
            "ideal": "Range-bound bozorlar uchun"
        }
    }

    for strategy_name, info in strategies_info.items():
        with st.expander(f"📌 {strategy_name}"):
            st.write(f"**Tavsif:** {info['tavsif']}")
            st.write(f"**Afzalliklar:**\n{info['afzalliklar']}")
            st.write(f"**Kamchiliklar:**\n{info['kamchiliklar']}")
            st.info(f"**Ideal:** {info['ideal']}")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("""
**O'quv maqsadida yaratilgan**

⚠️ Moliyaviy maslahat emas
📚 CCXT + Streamlit
🔒 Ma'lumotlaringiz xavfsiz
""")

# Auto-refresh
if st.sidebar.checkbox("Avtomatik yangilanish (30s)"):
    time.sleep(30)
    st.rerun()