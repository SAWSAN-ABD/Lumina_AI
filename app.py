import streamlit as st
from google import genai
from PIL import Image
import json
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. إعدادات الصفحة والتصميم الفاتح واللطيف ---
st.set_page_config(
    page_title="Lumina AI | Your Smart Content Assistant",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص الألوان والتنسيقات (Bright & Warm Nude Pink Light Theme)
st.markdown("""
    <style>
    /* خلفية الصفحة العامة - أوف وايت دافئ ومريح */
    .stApp {
        background-color: #fcf8f8 !important;
        color: #2d2424 !important;
    }
    
    /* القائمة الجانبية Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f7eded !important;
        border-left: 1px solid #ebd4d6 !important;
    }
    
    /* الهيدر الأنيق */
    .main-header {
        background: linear-gradient(135deg, #ffffff 0%, #fbf0f2 100%);
        padding: 30px 20px;
        border-radius: 20px;
        border: 2px solid #e8c5c8;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(216, 140, 154, 0.12);
    }
    .main-title {
        color: #d8707c;
        font-size: 40px;
        font-weight: 800;
        margin: 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .sub-title-1 {
        color: #4a3b3c;
        font-size: 19px;
        margin-top: 8px;
        font-weight: 600;
    }
    .sub-title-2 {
        color: #c05c67;
        font-size: 15px;
        margin-top: 4px;
        font-weight: 500;
        letter-spacing: 0.5px;
    }

    /* الأزرار العادية والتنزيل */
    .stButton>button, .stDownloadButton>button {
        background: linear-gradient(135deg, #e8a7b0 0%, #d88c9a 100%) !important;
        color: #ffffff !important;
        font-weight: bold !important;
        font-size: 15px !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 10px rgba(216, 140, 154, 0.25) !important;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #d88c9a 0%, #c87483 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(216, 140, 154, 0.4) !important;
    }

    /* البطاقات والأقسام المنفصلة */
    .custom-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 16px;
        border-right: 5px solid #d88c9a;
        border-top: 1px solid #f2e2e4;
        border-bottom: 1px solid #f2e2e4;
        border-left: 1px solid #f2e2e4;
        margin-bottom: 22px;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.04);
        color: #2d2424 !important;
    }
    
    /* تغيير ألوان التبويبات Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f2e4e5;
        border-radius: 10px;
        color: #5c484a;
        padding: 10px 22px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #d88c9a !important;
        color: #ffffff !important;
        font-weight: bold;
    }

    /* تحسين نصوص الإدخال والقوائم */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        background-color: #ffffff !important;
        color: #2d2424 !important;
        border: 1px solid #e2c2c5 !important;
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# إعداد محرك الذكاء الاصطناعي
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=API_KEY)

# إعداد اتصال Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_feedbacks():
    try:
        df = conn.read(ttl="0d")
        return df.dropna(how="all")
    except Exception:
        return pd.DataFrame(columns=["Timestamp", "Rating", "Category", "Comment"])

# --- 2. الهيدر المطور ---
st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🌸 Lumina AI</h1>
        <div class="sub-title-1">Your Smart Content Assistant | مساعدك الذكي للمحتوى</div>
        <div class="sub-title-2">Analyze • Improve • Create &nbsp;|&nbsp; حلّل • حسّن • أنشئ</div>
    </div>
""", unsafe_allow_html=True)

# --- 3. التبويبات الأساسية ---
tab_workspace, tab_analytics = st.tabs(["🚀 منصة التحليل والإنشاء", "📊 تقييمات المستخدمين (Analytics)"])

# ==========================================
# TAB 1: LUMINA WORKSPACE
# ==========================================
with tab_workspace:
    st.sidebar.header("🌸 رفع الأصل البصري")
    
    st.sidebar.markdown("""
        <div style="background-color: #ffffff; padding: 14px; border-radius: 12px; border-right: 4px solid #d88c9a; margin-bottom: 15px; font-size: 13.5px; color: #4a3b3c; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
            🌟 <b>نحن هنا لمساعدتك...</b><br>
            ارفع صورتك، ولنبدأ رحلتنا معًا 🕊️.
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.sidebar.file_uploader("اختر صورة للتحليل", type=["jpg", "jpeg", "png", "webp"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.sidebar.image(image, caption="الصورة المرفوعة", use_container_width=True)

        if st.sidebar.button("⚡ تشغيل التحليل الموحد", type="primary", use_container_width=True):
            with st.spinner("جاري معالجة الصورة وإعداد المقترحات بذكاء..."):
                try:
                    unified_prompt = (
                        "You are Lumina AI — an advanced Expert System for image analysis and content creation.\n"
                        "Analyze the provided image in detail and return a STRICTLY VALID JSON object (NO MARKDOWN, NO CODEBLOCKS).\n"
                        "JSON structure MUST be as follows:\n"
                        "{\n"
                        '  "category": "Product OR Portrait OR Food OR Resume OR General",\n'
                        '  "authenticity_score": "95%",\n'
                        '  "status": "Authentic OR AI-Generated",\n'
                        '  "readiness_score": 92,\n'
                        '  "readiness_status": "READY TO PUBLISH",\n'
                        '  "lumina_insight": "اكتب انطباعاً ذكياً ومختصراً جداً عن جودة الصورة والتكوين والمنصة الأنسب للنشر بالعربية",\n'
                        '  "readiness_breakdown": [\n'
                        '     "✔ جودة الصورة: ممتازة وعالية الدقة",\n'
                        '     "✔ الأصالة: عالية وغير خاضعة للتزييف",\n'
                        '     "⚠ نصيحة تحسين: ينصح بتعديل الإضاءة في الزوايا"\n'
                        '  ],\n'
                        '  "reasoning": ["دليل بصري 1 على الأصالة أو التكوين", "دليل بصري 2"],\n'
                        '  "smart_actions": [\n'
                        '     {"title": "📝 الكابشن والهاشتاغات", "content": "اكتب هنا الكابشن الفعلي المصاغ خصيصاً لهذه الصورة مع 8 إلى 10 هاشتاغات قوية ومناسبة لها"},\n'
                        '     {"title": "👔 النسخة الرسمية (Professional)", "content": "اكتب هنا صياغة احترافية ورسمية للمحتوى مناسبة لمنصة LinkedIn بناءً على الصورة"},\n'
                        '     {"title": "🎯 الخطة التسويقية والجمهور", "content": "حدد هنا الجمهور المستهدف بدقة والاستراتيجية الأنسب لترويج هذه الصورة"},\n'
                        '     {"title": "🎨 نصائح التعديل البصري", "content": "اعطِ نصائح تقنية سريعة لتحسين الإضاءة والألوان والتأثيرات البصرية لهذه الصورة"}\n'
                        '  ]\n'
                        "}\n"
                        "CRITICAL: Replace all action contents with REAL generated text specific to the uploaded image in Arabic language."
                    )

                    response = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=[image, unified_prompt]
                    )

                    raw = response.text.strip().replace("```json", "").replace("
