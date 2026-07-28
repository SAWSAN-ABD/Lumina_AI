import io
import json
from datetime import datetime

import pandas as pd
from PIL import Image, ImageEnhance
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# استدعاء مكتبة الذكاء الاصطناعي الحديثة
from google import genai

try:
  from streamlit_image_comparison import image_comparison
except ImportError:
  image_comparison = None

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(
    page_title="Lumina AI | Your Smart Content Assistant",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background-color: #fcf8f8 !important; color: #2d2424 !important; }
    [data-testid="stSidebar"] { background-color: #f7eded !important; border-left: 1px solid #ebd4d6 !important; }
    .main-header {
        background: linear-gradient(135deg, #ffffff 0%, #fbf0f2 100%);
        padding: 25px 20px; border-radius: 20px; border: 2px solid #e8c5c8;
        margin-bottom: 25px; text-align: center; box-shadow: 0 8px 20px rgba(216, 140, 154, 0.12);
    }
    .main-title { color: #d8707c; font-size: 38px; font-weight: 800; margin: 0; }
    .sub-title-1 { color: #4a3b3c; font-size: 18px; margin-top: 6px; font-weight: 600; }
    .sub-title-2 { color: #c05c67; font-size: 14px; margin-top: 4px; font-weight: 500; }
    .stButton>button, .stDownloadButton>button {
        background: linear-gradient(135deg, #e8a7b0 0%, #d88c9a 100%) !important;
        color: #ffffff !important; font-weight: bold !important; font-size: 15px !important;
        border-radius: 12px !important; border: none !important; padding: 10px 20px !important;
        transition: all 0.3s ease !important; box-shadow: 0 4px 10px rgba(216, 140, 154, 0.25) !important;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #d88c9a 0%, #c87483 100%) !important;
        transform: translateY(-2px); box-shadow: 0 6px 15px rgba(216, 140, 154, 0.4) !important;
    }
    .custom-card {
        background-color: #ffffff; padding: 22px; border-radius: 16px;
        border-right: 5px solid #d88c9a; border-top: 1px solid #f2e2e4;
        border-bottom: 1px solid #f2e2e4; border-left: 1px solid #f2e2e4;
        margin-bottom: 20px; box-shadow: 0 6px 16px rgba(0, 0, 0, 0.04); color: #2d2424 !important;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f2e4e5; border-radius: 10px; color: #5c484a; padding: 10px 22px; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #d88c9a !important; color: #ffffff !important; font-weight: bold; }
    .stTextInput input, .stSelectbox select, .stTextArea textarea { background-color: #ffffff !important; color: #2d2424 !important; border: 1px solid #e2c2c5 !important; border-radius: 10px !important; }
    </style>
""",
    unsafe_allow_html=True,
)

# إعداد الربط والذاكرة
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=API_KEY)
conn = st.connection("gsheets", type=GSheetsConnection)

# استخدام موديل ذو توافقية عالية مع المكتبة
MODEL_NAME = "gemini-2.5-flash"

if "history" not in st.session_state:
  st.session_state["history"] = []


# دالة توليد PDF
def generate_pdf_report(data):
  buffer = io.BytesIO()
  p = canvas.Canvas(buffer, pagesize=letter)
  p.setTitle("Lumina AI Audit Report")

  p.setFont("Helvetica-Bold", 18)
  p.drawString(50, 750, "Lumina AI - Image Analysis Report")
  p.setLineWidth(1)
  p.line(50, 740, 550, 740)

  p.setFont("Helvetica", 11)
  p.drawString(
      50, 715, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
  )
  p.drawString(50, 695, f"Category: {data.get('category', 'N/A')}")
  p.drawString(
      50,
      675,
      f"Authenticity Score: {data.get('authenticity_score', 'N/A')} ("
      f"{data.get('status', 'N/A')})",
  )
  p.drawString(
      50,
      655,
      f"Readiness Score: {data.get('readiness_score', 0)}% ("
      f"{data.get('readiness_status', 'N/A')})",
  )

  p.setFont("Helvetica-Bold", 13)
  p.drawString(50, 620, "Lumina Insight:")
  p.setFont("Helvetica", 10)
  insight_text = data.get("lumina_insight", "")
  p.drawString(50, 600, insight_text[:90])
  if len(insight_text) > 90:
    p.drawString(50, 585, insight_text[90:180])

  p.setFont("Helvetica-Bold", 13)
  p.drawString(50, 550, "Readiness Breakdown:")
  p.setFont("Helvetica", 10)
  y = 530
  for item in data.get("readiness_breakdown", []):
    p.drawString(60, y, f"- {item}")
    y -= 18

  p.setFont("Helvetica-Bold", 13)
  p.drawString(50, y - 10, "Visual Evidence:")
  p.setFont("Helvetica", 10)
  y -= 30
  for r in data.get("reasoning", []):
    p.drawString(60, y, f"* {r}")
    y -= 18

  p.showPage()
  p.save()
  buffer.seek(0)
  return buffer


def load_feedbacks():
  try:
    df = conn.read(ttl="0d")
    return df.dropna(how="all")
  except Exception:
    return pd.DataFrame(columns=["Timestamp", "Rating", "Category", "Comment"])


# --- الهيدر ---
st.markdown(
    """
    <div class="main-header">
        <h1 class="main-title">🌸 Lumina AI</h1>
        <div class="sub-title-1">Your Smart Content Assistant | مساعدك الذكي للمحتوى</div>
        <div class="sub-title-2">Analyze • Improve • Create &nbsp;|&nbsp; حلّل • حسّن • أنشئ</div>
    </div>
""",
    unsafe_allow_html=True,
)

tab_workspace, tab_analytics = st.tabs(
    ["🚀 منصة التحليل والإنشاء", "📊 تقييمات المستخدمين (Analytics)"]
)

with tab_workspace:
  st.sidebar.header("🌸 رفع الأصل البصري")

  # --- سجل الجلسة السابقة (History Log) ---
  if st.session_state["history"]:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📜 سجل التحليلات السابقة")
    selected_hist = st.sidebar.selectbox(
        "استرجع تحليلاً سابقاً:",
        options=list(range(len(st.session_state["history"]))),
        format_func=lambda i: (
            f"تحليل {i+1}: {st.session_state['history'][i]['data'].get('category', 'صورة')}"
        ),
    )
    if st.sidebar.button("📂 تحميل هذا التحليل"):
      st.session_state["lumina_data"] = st.session_state["history"][
          selected_hist
      ]["data"]
      st.session_state["current_image"] = st.session_state["history"][
          selected_hist
      ]["image"]

  uploaded_file = st.sidebar.file_uploader(
      "اختر صورة جديدة للتحليل", type=["jpg", "jpeg", "png", "webp"]
  )

  if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.sidebar.image(
        image, caption="الصورة المرفوعة", use_container_width=True
    )

    if st.sidebar.button(
        "⚡ تشغيل التحليل الموحد", type="primary", use_container_width=True
    ):
      with st.spinner("جاري معالجة الصورة وإعداد المقترحات بذكاء..."):
        try:
          unified_prompt = (
              "You are Lumina AI — an advanced Expert System for image analysis"
              " and content creation.\nAnalyze the provided image in detail and"
              " return a STRICTLY VALID JSON object (NO MARKDOWN, NO"
              ' CODEBLOCKS).\nJSON structure MUST be as follows:\n{\n  "category":'
              ' "Product OR Portrait OR Food OR Resume OR General",\n '
              ' "authenticity_score": "95%",\n  "status": "Authentic OR'
              ' AI-Generated",\n  "readiness_score": 92,\n '
              ' "readiness_status": "READY TO PUBLISH",\n  "lumina_insight":'
              ' "اكتب انطباعاً ذكياً ومختصراً جداً عن جودة الصورة والتكوين والمنصة'
              ' الأنسب للنشر بالعربية",\n  "readiness_breakdown": [\n     "✔'
              ' جودة الصورة: ممتازة وعالية الدقة",\n     "✔ الأصالة: عالية وغير'
              ' خاضعة للتزييف",\n     "⚠ نصيحة تحسين: ينصح بتعديل الإضاءة في'
              ' الزوايا"\n  ],\n  "reasoning": ["دليل بصري 1 على الأصالة أو'
              ' التكوين", "دليل بصري 2"],\n  "smart_actions": [\n    '
              ' {"title": "📝 الكابشن والهاشتاغات", "content": "اكتب هنا الكابشن'
              " الفعلي المصاغ خصيصاً لهذه الصورة مع 8 إلى 10 هاشتاغات قوية ومناسبة"
              ' لها"},\n     {"title": "👔 النسخة الرسمية (Professional)",'
              ' "content": "اكتب هنا صياغة احترافية ورسمية للمحتوى مناسبة لمنصة'
              ' LinkedIn بناءً على الصورة"},\n     {"title": "🎯 الخطة'
              ' التسويقية والجمهور", "content": "حدد هنا الجمهور المستهدف بدقة'
              ' والاستراتيجية الأنسب لترويج هذه الصورة"},\n     {"title": "🎨'
              ' نصائح التعديل البصري", "content": "اعطِ نصائح تقنية سريعة لتحسين'
              ' الإضاءة والألوان والتأثيرات البصرية لهذه الصورة"}\n  ]\n}\nCRITICAL:'
              " Replace all action contents with REAL generated text specific to"
              " the uploaded image in Arabic language."
          )

          response = client.models.generate_content(
              model=MODEL_NAME, contents=[image, unified_prompt]
          )

         raw = response.text.strip().replace("```json", "").replace("```", "")
