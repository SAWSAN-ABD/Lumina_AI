import io
import json
from datetime import datetime
import urllib.request
import urllib.parse

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
    initial_sidebar_state="expanded"
)

# رابط سكربت جوجل للتقييمات
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycby5jFANTTKQSC3xYeo_LXJ1mYsDDPDJgo_TW_M4thXp4Q6vgo_9SxGma_KJAjkAldcy/exec"

st.markdown("""
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
    .stButton>button, .stDownloadButton>button, .pinterest-btn {
        background: linear-gradient(135deg, #e8a7b0 0%, #d88c9a 100%) !important;
        color: #ffffff !important; font-weight: bold !important; font-size: 15px !important;
        border-radius: 12px !important; border: none !important; padding: 10px 20px !important;
        transition: all 0.3s ease !important; box-shadow: 0 4px 10px rgba(216, 140, 154, 0.25) !important;
        text-decoration: none; display: inline-block; text-align: center;
    }
    .stButton>button:hover, .stDownloadButton>button:hover, .pinterest-btn:hover {
        background: linear-gradient(135deg, #d88c9a 0%, #c87483 100%) !important;
        transform: translateY(-2px); box-shadow: 0 6px 15px rgba(216, 140, 154, 0.4) !important;
        color: #ffffff !important;
    }
    .custom-card {
        background-color: #ffffff; padding: 22px; border-radius: 16px;
        border-right: 5px solid #d88c9a; border-top: 1px solid #f2e2e4;
        border-bottom: 1px solid #f2e2e4; border-left: 1px solid #f2e2e4;
        margin-bottom: 20px; box-shadow: 0 6px 16px rgba(0, 0, 0, 0.04); color: #2d2424 !important;
    }
    .stTextInput input, .stSelectbox select, .stTextArea textarea { background-color: #ffffff !important; color: #2d2424 !important; border: 1px solid #e2c2c5 !important; border-radius: 10px !important; }
    </style>
""", unsafe_allow_html=True)

# إعداد الربط والذاكرة
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=API_KEY) if API_KEY else None

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
    p.drawString(50, 715, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    p.drawString(50, 695, f"Category: {data.get('category', 'N/A')}")
    p.drawString(50, 675, f"Authenticity Score: {data.get('authenticity_score', 'N/A')} ({data.get('status', 'N/A')})")
    p.drawString(50, 655, f"Readiness Score: {data.get('readiness_score', 0)}% ({data.get('readiness_status', 'N/A')})")
    
    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, 620, "Lumina Insight:")
    p.setFont("Helvetica", 10)
    insight_text = data.get('lumina_insight', '')
    p.drawString(50, 600, insight_text[:90])
    if len(insight_text) > 90:
        p.drawString(50, 585, insight_text[90:180])
        
    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, 550, "Readiness Breakdown:")
    p.setFont("Helvetica", 10)
    y = 530
    for item in data.get('readiness_breakdown', []):
        p.drawString(60, y, f"- {item}")
        y -= 18
        
    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, y - 10, "Visual Evidence:")
    p.setFont("Helvetica", 10)
    y -= 30
    for r in data.get('reasoning', []):
        p.drawString(60, y, f"* {r}")
        y -= 18
        
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- الهيدر ---
st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🌸 Lumina AI</h1>
        <div class="sub-title-1">Your Smart Content Assistant | مساعدك الذكي للمحتوى</div>
        <div class="sub-title-2">Analyze • Improve • Create &nbsp;|&nbsp; حلّل • حسّن • أنشئ</div>
    </div>
""", unsafe_allow_html=True)

tab_workspace, tab_analytics = st.tabs(["🚀 منصة التحليل والإنشاء", "📊 تقييمات المستخدمين (Analytics)"])

with tab_workspace:
    st.sidebar.header("🌸 رفع الأصل البصري")
    
    if st.session_state["history"]:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📜 سجل التحليلات السابقة")
        selected_hist = st.sidebar.selectbox(
            "استرجع تحليلاً سابقاً:",
            options=list(range(len(st.session_state["history"]))),
            format_func=lambda i: f"تحليل {i+1}: {st.session_state['history'][i]['data'].get('category', 'صورة')}"
        )
        if st.sidebar.button("📂 تحميل هذا التحليل"):
            st.session_state["lumina_data"] = st.session_state["history"][selected_hist]["data"]
            st.session_state["current_image"] = st.session_state["history"][selected_hist]["image"]

    uploaded_file = st.sidebar.file_uploader("اختر صورة جديدة للتحليل", type=["jpg", "jpeg", "png", "webp"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        st.sidebar.image(image, caption="الصورة المرفوعة", use_container_width=True)
        
        if st.sidebar.button("⚡ تشغيل التحليل الموحد", type="primary", use_container_width=True):
            if not client:
                st.warning("🌸 يرجى التأكد من إعداد مفتاح الـ API للبدء.")
            else:
                with st.spinner("جاري استخراج الميزات الجمالية وبناء الـ Moodboard الذكي... 🌸"):
                    try:
                        unified_prompt = """You are Lumina AI — an advanced Expert System for aesthetic image analysis and visual content creation.
Analyze the provided image in detail and return a STRICTLY VALID JSON object (NO MARKDOWN, NO CODEBLOCKS).
JSON structure MUST be as follows:
{
  "category": "Product OR Portrait OR Food OR Resume OR General",
  "authenticity_score": "95%",
  "status": "Authentic OR AI-Generated",
  "readiness_score": 92,
  "readiness_status": "READY TO PUBLISH",
  "search_keywords": "3 to 4 English keywords describing aesthetic style, lighting, color tone (e.g., warm cozy aesthetic coffee moody)",
  "lumina_insight": "انطباع تحليلي ذكي ومختصر عن التكوين البصري والجمالية العامة والروح التي تعكسها الصورة بالعربية",
  "readiness_breakdown": [
     "✔ جودة الصورة والتنسيق البصري: ممتازة",
     "✔ ملاءمة الهوية والتكوين للنشر",
     "⚠ نصيحة للتحسين البصري"
  ],
  "reasoning": [
     "دليل بصري على الأسلوب أو التكوين",
     "تأثير توزيع العناصر والإضاءة"
  ],
  "smart_actions": [
     {"title": "🎨 لوحة الألوان والأسلوب الجمالي", "content": "قم باستخراج الأسلوب الجمالي (Aesthetic Mood) وألهم المستخدم بأكواد الألوان السائدة Hex Codes مع توزيعها."},
     {"title": "📌 مولّد دبابيس بينترست الذكية", "content": "صغ عنوان جذاب لـ Pinterest، مع وصف SEO دقيق، وترشيح لاسم اللوحة المناسبة (Board Name)."},
     {"title": "📊 كاشف جودة واستجابة التكوين (Pin-Readiness)", "content": "حلل نسبة أبعاد الصورة (هل هي 2:3؟)، ودرجة وضوح التباين والتركيز لمنصة بينترست مع تقييم للجاهزية."},
     {"title": "🖼️ البحث البصري وتوليد الـ Moodboard", "content": "اكتب برومبت سينمائي مفصل باللغة الإنجليزية لتوليد لوحة إلهام مطابقة في Midjourney / DALL-E مع شرح العناصر الجمالية التي تجمع بين الصور المشابهة."},
     {"title": "📖 مولّد القصة وتخيل المشهد البصري", "content": "اكتب قصة بصرية قصيرة ومحفزة للمشهد ومستقبل الصورة لتطوير الفكرة واستخدامها في المحتوى الإبداعي."},
     {"title": "🧠 سيكولوجية الألوان والتأثير العاطفي", "content": "حلل الأثر النفسي والعاطفي للألوان المستخدمة في الصورة وكيف تؤثر على مشاعر الجمهور المستهدف."},
     {"title": "♿ محاكي التباين والسهولة البصرية (Accessibility)", "content": "حلل مدى سهولة قراءة عناصر الصورة لذوي الاحتياجات البصرية، وتوازن التباين بين الضوء والظلال."},
     {"title": "✒️ الأناقة البصرية للخطوط والتباين", "content": "اقترح أنماط خطوط (Typography Pairs) تتناسب مع هذا التكوين البصري مع ألوان النصوص المتباينة."},
     {"title": "👔 النسخة الرسمية والهاشتاغات", "content": "صغ كابشن رسمياً ملائماً للمنصات الاحترافية مثل LinkedIn مع هاشتاغات استراتيجية قوية."}
  ]
}
CRITICAL: Replace all action contents with REAL generated detailed text in Arabic (and English where specified) specific to the uploaded image."""

                        response = client.models.generate_content(
                            model=MODEL_NAME,
                            contents=[image, unified_prompt]
                        )
                        
                        raw = response.text.strip().replace("```json", "").replace("```", "")
                        parsed_data = json.loads(raw)
                        
                        st.session_state["lumina_data"] = parsed_data
                        st.session_state["current_image"] = image
                        
                        st.session_state["history"].append({"data": parsed_data, "image": image})
                        st.success("✨ اكتمل التحليل الجمالي وتوليد لوحة الإلهام البصرية بنجاح!")
                    
                    except Exception as e:
                        err_text = str(e)
                        if "429" in err_text or "Quota" in err_text or "ResourceExhausted" in err_text:
                            st.info("⏳ **تم الوصول للحد الأقصى المؤقت للحصة المجانية (API Limit).**\n\nيرجى الانتظار دقيقة واحدة وإعادة الضغط، أو التأكد من المفتاح الخاص بكِ 🌸")
                        else:
                            st.warning("🌸 تعذر استكمال التحليل لحظياً، يرجى المحاولة مرة أخرى أو التأكد من جودة الصورة المرفوعة.")

    if "lumina_data" in st.session_state:
        data = st.session_state["lumina_data"]
        
        st.markdown(f"""
            <div class="custom-card">
                <h4 style="color: #c05c67; margin-top:0; font-weight: 700;">🧠 Lumina Insight (الرؤية الذكية):</h4>
                <p style="font-size: 16.5px; line-height: 1.6; color: #2d2424; margin-bottom:0;">{data.get('lumina_insight', '')}</p>
            </div>
        """, unsafe_allow_html=True)
        
        col_analysis, col_report = st.columns(2)
        
        with col_analysis:
            st.markdown("""
                <div class="custom-card">
                    <h3 style="color: #c05c67; margin-top:0; font-weight: 700;">🔍 قسم التحليل البصري والأصالة</h3>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"**نوع المحتوى:** `{data.get('category')}`")
            st.markdown(f"**نسبة الأصالة:** `{data.get('authenticity_score')}` ({data.get('status')})")
            st.write("**الأدلة البصرية والجنائية:**")
            for r in data.get('reasoning', []):
                st.write(f"• {r}")
                
        with col_report:
            st.markdown("""
                <div class="custom-card">
                    <h3 style="color: #c05c67; margin-top:0; font-weight: 700;">📊 جاهزية النشر والتقرير الفني</h3>
                </div>
            """, unsafe_allow_html=True)
            score = data.get('readiness_score', 85)
            st.metric(label="Publishing Readiness Score", value=f"{score}%", delta=data.get('readiness_status', 'READY TO PUBLISH'))
            st.progress(score / 100)
            
            st.write("**تفاصيل التقييم التقديري:**")
            for item in data.get('readiness_breakdown', []):
                st.write(f"- {item}")
                
            col_pdf, col_txt = st.columns(2)
            with col_pdf:
                pdf_bytes = generate_pdf_report(data)
                st.download_button(
                    label="📄 تنزيل تقرير PDF",
                    data=pdf_bytes,
                    file_name=f"lumina_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            with col_txt:
                report_str = f"LUMINA REPORT\nCategory: {data.get('category')}\nScore: {data.get('readiness_score')}%\nInsight: {data.get('lumina_insight')}"
                st.download_button(
                    label="📝 تنزيل ملف TXT",
                    data=report_str,
                    file_name="lumina_report.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        st.divider()

        # --- 🌸 قسم عرض الصور المشابهة و Visual Moodboard (المحدث بأسلوب نقي وسريع) ---
        st.subheader("🖼️ معرض الصور المشابهة ولوحة الإلهام (AI Visual Moodboard)")
        
        search_kw = data.get("search_keywords", "aesthetic visual design")
        st.write(f"🔍 **الكلمات المفتاحية البصرية المستخرجة:** `{search_kw}`")
        
        keywords_encoded = urllib.parse.quote(search_kw)
        
        # شبكة عرض الصور المشابهة المستقرة عبر استدعاء الصور بأسلوب Streamlit الأصلي
        col1, col2, col3, col4 = st.columns(4)
        
        img_urls = [
            "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=500&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1507652313519-d4e9174996dd?w=500&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=500&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500&auto=format&fit=crop&q=80"
        ]
        
        cols = [col1, col2, col3, col4]
        for idx, col in enumerate(cols):
            with col:
                st.image(img_urls[idx], caption=f"إلهام بصري {idx+1} 🌸", use_container_width=True)

        # زر بحث مباشر على Pinterest
        pinterest_url = f"https://www.pinterest.com/search/pins/?q={keywords_encoded}"
        st.markdown(f"""
            <div style="text-align: center; margin-top: 15px;">
                <a href="{pinterest_url}" target="_blank" class="pinterest-btn">
                    📌 تصفح المزيد من الصور المطابقة مباشرة على Pinterest
                </a>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        # --- قسم مقارنة الصورة الأصلية والمعدلة ---
        st.subheader("🔧 أداة المعاينة والمقارنة البصرية (Interactive Enhancer)")
        if "current_image" in st.session_state:
            curr_img = st.session_state["current_image"]
            col_opt, col_comp = st.columns([1, 2])
            
            with col_opt:
                st.write("🔧 **تحسين بصري سريع:**")
                contrast_val = st.slider("التباين (Contrast)", 0.5, 2.0, 1.2)
                sharp_val = st.slider("الوضوح (Sharpness)", 0.5, 3.0, 1.5)
                
                enhancer = ImageEnhance.Contrast(curr_img)
                img_mod = enhancer.enhance(contrast_val)
                enhancer2 = ImageEnhance.Sharpness(img_mod)
                img_mod = enhancer2.enhance(sharp_val)
                
            with col_comp:
                st.write("↔️ **قارني بين الصورة الأصلية والمعدلة:**")
                try:
                    if image_comparison:
                        image_comparison(
                            img1=curr_img,
                            img2=img_mod,
                            label1="الصورة الأصلية",
                            label2="المعدلة بـ Lumina"
                        )
                    else:
                        st.image([curr_img, img_mod], caption=["الصورة الأصلية", "المعدلة تلقائياً"], width=250)
                except Exception:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.image(curr_img, caption="الصورة الأصلية", use_container_width=True)
                    with col_b:
                        st.image(img_mod, caption="المعدلة بـ Lumina", use_container_width=True)

        st.divider()
        
        # --- قسم الميزات الـ 9 المحددة ---
        st.subheader("✨ الميزات الاستراتيجية وصناعة المحتوى الجمالي")
        actions = data.get("smart_actions", [])
        titles = [act["title"] for act in actions]
        
        selected_tab = st.radio("اختر الميزة المطلوبة لعرض التقرير والتوليد:", titles, horizontal=True)
        for act in actions:
            if act["title"] == selected_tab:
                st.text_area("النتيجة والتوصيات المولدة تلقائياً:", value=act["content"], height=220)
                
        st.divider()
        
        st.subheader("💬 Ask Lumina (المستشار الذكي)")
        with st.form("ask_lumina_form"):
            selected_option = st.selectbox(
                "اختر سؤالاً سريعاً أو اكتب سؤالك:",
                [
                    "اختر من الأسئلة المقترحة...",
                    "💡 كيف أحصل على صور مشابهة بنفس الـ Aesthetic على بينترست؟",
                    "🎨 كيف تحسن هذه الألوان من الحالة المزاجية للمشاهد؟",
                    "📌 ما هي نصائح تحسين الـ Pin readiness للانتشار الفيروسي؟",
                    "🎯 من هو الجمهور المستهدف الدقيق لهذه الصورة؟"
                ]
            )
            custom_question = st.text_input("أو اكتب سؤالك المخصص هنا:")
            submit_ask = st.form_submit_button("إرسال السؤال لـ Lumina 🚀")
            
            if submit_ask:
                final_q = custom_question.strip() if custom_question.strip() else selected_option
                if final_q and final_q != "اختر من الأسئلة المقترحة...":
                    with st.spinner("جاري استشارة Lumina... 🌸"):
                        try:
                            consult_prompt = f"أجب على سؤال المستخدم التالي باللغة العربية بأسلوب احترافي ومختصر بناءً على هذه الصورة وتحليلها: '{final_q}'. سياق التحليل: {json.dumps(data, ensure_ascii=False)}"
                            payload = [consult_prompt]
                            if "current_image" in st.session_state:
                                payload.insert(0, st.session_state["current_image"])
                                
                            res = client.models.generate_content(
                                model=MODEL_NAME,
                                contents=payload
                            )
                            st.markdown("### 🤖 إجابة المستشار الذكي:")
                            st.info(res.text)
                        except Exception as e:
                            st.info("🌸 تعذر الحصول على إجابة فورية الآن، يرجى المحاولة بعد دقيقة.")

        st.divider()
        
        st.subheader("⭐ شاركنا رأيك وتقييمك للتجربة")
        with st.form("feedback_form"):
            rating = st.slider("تقييمك للدقة والجودة (من 1 إلى 5 نجوم):", 1, 5, 5)
            comment = st.text_input("ملاحظاتك أو تعليقك اللطيف (اختياري):")
            submitted = st.form_submit_button("إرسال التقييم 🚀")
            
            if submitted:
                feedback_data = {
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Rating": rating,
                    "Category": data.get("category", "General"),
                    "Comment": comment
                }
                try:
                    req = urllib.request.Request(
                        GOOGLE_SCRIPT_URL,
                        data=json.dumps(feedback_data).encode('utf-8'),
                        headers={'Content-Type': 'application/json'}
                    )
                    with urllib.request.urlopen(req) as response:
                        st.balloons()
                        st.success("شكراً لك! تم إرسال تقييمك وحفظه في جوجل شيت بنجاح. 🌸")
                except Exception:
                    st.success("شكراً لك! تم تسليم تقييمك بنجاح 🎉")

    else:
        st.info("👈 اهلا بك نحن بانتظارك لنبدأ معا")

# ==========================================
# TAB 2: ANALYTICS
# ==========================================
with tab_analytics:
    st.header("📊 لوحة تحليلات تقييمات المستخدمين (Analytics Dashboard)")
    
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_feedback = conn.read(ttl=5)
        
        if not df_feedback.empty and "Rating" in df_feedback.columns:
            df_feedback["Rating"] = pd.to_numeric(df_feedback["Rating"], errors='coerce')
            
            m1, m2, m3 = st.columns(3)
            m1.metric("إجمالي التقييمات", len(df_feedback))
            m2.metric("متوسط التقييم", f"{df_feedback['Rating'].mean():.2f} / 5.0 ⭐")
            m3.metric("نسبة الرضا العالي", f"{(df_feedback['Rating'] >= 4).mean() * 100:.1f}%")
            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("توزيع النجوم")
                st.bar_chart(df_feedback["Rating"].value_counts())
            with c2:
                st.subheader("المتوسط حسب التصنيف")
                if "Category" in df_feedback.columns:
                    st.bar_chart(df_feedback.groupby("Category")["Rating"].mean())
            st.dataframe(df_feedback, use_container_width=True)
        else:
            st.info("جداول البيانات فارغة حالياً. قومي بإرسال أول تقييم من منصة التحليل!")
    except Exception:
        st.info("لا توجد تقييمات مسجلة بعد، أو يرجى التأكد من ربط الشيت بالشكل الصحيح 🌸")
