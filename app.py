import streamlit as st
from google import genai
from PIL import Image
import json
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(
    page_title="Lumina AI | Your Smart Content Assistant",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص الألوان والتنسيقات (Nude Pink & Charcoal Slate Theme)
st.markdown("""
    <style>
    .stApp {
        background-color: #121214;
        color: #f1f1f1;
    }
    .main-header {
        background: linear-gradient(135deg, #2a242a 0%, #1a161b 100%);
        padding: 30px 20px;
        border-radius: 16px;
        border: 1px solid #d8a7b1;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(216, 167, 177, 0.1);
    }
    .main-title {
        color: #e8b4b8;
        font-size: 38px;
        font-weight: bold;
        margin: 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .sub-title-1 {
        color: #ffffff;
        font-size: 18px;
        margin-top: 6px;
        font-weight: 500;
    }
    .sub-title-2 {
        color: #d8a7b1;
        font-size: 14px;
        margin-top: 4px;
        letter-spacing: 1px;
    }
    .stButton>button, .stDownloadButton>button {
        background-color: #d8a7b1 !important;
        color: #1a161b !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        background-color: #e8b4b8 !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(232, 180, 184, 0.3);
    }
    .custom-card {
        background-color: #1e1e24;
        padding: 22px;
        border-radius: 14px;
        border-left: 4px solid #d8a7b1;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e1e24;
        border-radius: 8px;
        color: #cccccc;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #d8a7b1 !important;
        color: #1a161b !important;
        font-weight: bold;
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
        <div style="background-color: #2a242a; padding: 12px; border-radius: 10px; border-right: 3px solid #d8a7b1; margin-bottom: 15px; font-size: 13px;">
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

                    raw = response.text.strip().replace("```json", "").replace("```", "")
                    st.session_state["lumina_data"] = json.loads(raw)
                    st.session_state["current_image"] = image
                    st.success("✅ اكتمل التحليل بنجاح!")

                except Exception as e:
                    st.error(f"حدث خطأ أثناء معالجة الصورة: {e}")

    # عرض النتائج
    if "lumina_data" in st.session_state:
        data = st.session_state["lumina_data"]

        # 🧠 Lumina Insight Box
        st.markdown(f"""
            <div class="custom-card">
                <h4 style="color: #e8b4b8; margin-top:0;">🧠 Lumina Insight (الرؤية الذكية):</h4>
                <p style="font-size: 16px; line-height: 1.6;">{data.get('lumina_insight', '')}</p>
            </div>
        """, unsafe_allow_html=True)

        col_analysis, col_report = st.columns(2)

        with col_analysis:
            st.markdown("""
                <div class="custom-card">
                    <h3 style="color: #e8b4b8; margin-top:0;">🔍 قسم التحليل البصري والأصالة</h3>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**نوع المحتوى:** `{data.get('category')}`")
            st.markdown(f"**نسبة الأصالة:** `{data.get('authenticity_score')}` ({data.get('status')})")

            st.write("**الأدلة البصرية والجنائية:**")
            for r in data.get("reasoning", []):
                st.write(f"• {r}")

        with col_report:
            st.markdown("""
                <div class="custom-card">
                    <h3 style="color: #e8b4b8; margin-top:0;">📊 جاهزية النشر والتقرير الفني</h3>
                </div>
            """, unsafe_allow_html=True)

            score = data.get("readiness_score", 85)
            st.metric(
                label="Publishing Readiness Score",
                value=f"{score}%",
                delta=data.get("readiness_status", "READY TO PUBLISH")
            )
            st.progress(score / 100)

            st.write("**تفاصيل التقييم التقديري:**")
            for item in data.get("readiness_breakdown", []):
                st.write(f"- {item}")

            report_str = f"""=== LUMINA AI AUDIT REPORT ===
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Category: {data.get('category')}
Readiness Score: {data.get('readiness_score')}% ({data.get('readiness_status')})
Authenticity: {data.get('authenticity_score')} ({data.get('status')})

Insight:
{data.get('lumina_insight')}

Breakdown:
""" + "\n".join([f"- {i}" for i in data.get("readiness_breakdown", [])])

            st.download_button(
                label="📥 تنزيل التقرير الفني المباشر (Download Report)",
                data=report_str,
                file_name=f"lumina_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )

        st.divider()

        # ✨ Phase 3: Create
        st.subheader("✨ المقترحات الذكية وصناعة المحتوى (Create)")
        actions = data.get("smart_actions", [])
        titles = [act["title"] for act in actions]
        
        selected_tab = st.radio("اختر الإجراء المباشر المطلوب:", titles, horizontal=True)

        for act in actions:
            if act["title"] == selected_tab:
                st.text_area("المحتوى المولد تلقائياً:", value=act["content"], height=220)

        st.divider()

        # 💬 Ask Lumina Consultant
        st.subheader("💬 Ask Lumina (المستشار الذكي)")
        
        with st.form("ask_lumina_form"):
            selected_option = st.selectbox(
                "اختر سؤالاً سريعاً أو اختر كتابة سؤال مخصص:",
                [
                    "اختر من الأسئلة المقترحة...",
                    "💡 كيف أحسن جودة هذه الصورة؟",
                    "🔍 ما هي أدلة الأصالة التي اعتمدت عليها؟",
                    "👔 صغ لي نصاً رسمياً لهذه الصورة لمنصة LinkedIn",
                    "🎯 من هو الجمهور المستهدف الدقيق لهذه الصورة؟"
                ]
            )
            custom_question = st.text_input("أو اكتب سؤالك المخصص هنا:")
            submit_ask = st.form_submit_button("إرسال السؤال لـ Lumina 🚀")

            if submit_ask:
                final_q = custom_question.strip() if custom_question.strip() else selected_option
                
                if final_q and final_q != "اختر من الأسئلة المقترحة...":
                    with st.spinner("جاري استشارة Lumina..."):
                        try:
                            consult_prompt = (
                                f"أجب على سؤال المستخدم التالي باللغة العربية بأسلوب احترافي ومختصر بناءً على هذه الصورة وتحليلها: '{final_q}'. "
                                f"سياق التحليل السابق: {json.dumps(data, ensure_ascii=False)}"
                            )
                            
                            contents_payload = [consult_prompt]
                            if "current_image" in st.session_state and st.session_state["current_image"] is not None:
                                contents_payload.insert(0, st.session_state["current_image"])

                            res = client.models.generate_content(
                                model='gemini-2.0-flash',
                                contents=contents_payload
                            )
                            
                            st.markdown("### 🤖 إجابة المستشار الذكي:")
                            st.info(res.text)

                        except Exception as e:
                            st.error(f"حدث خطأ أثناء الرد: {e}")
                else:
                    st.warning("يرجى اختيار سؤال أو كتابة سؤال قبل الإرسال.")

        st.divider()

        # ⭐ قسم تقييم التجربة وحفظه المباشر في Google Sheets
        st.subheader("⭐ شاركنا رأيك وتقييمك للتجربة")
        with st.form("feedback_form"):
            rating = st.slider("تقييمك للدقة والجودة (من 1 إلى 5 نجوم):", 1, 5, 5)
            comment = st.text_input("ملاحظاتك أو تعليقك اللطيف (اختياري):")
            submitted = st.form_submit_button("إرسال التقييم 🚀")

            if submitted:
                try:
                    existing_df = load_feedbacks()
                    new_row = pd.DataFrame([{
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Rating": rating,
                        "Category": data.get("category", "General"),
                        "Comment": comment
                    }])
                    updated_df = pd.concat([existing_df, new_row], ignore_index=True)
                    conn.update(data=updated_df)
                    st.balloons()
                    st.success("شكراً لك من القلب! تم تسجيل تقييمك بشكل دائم في السحابة. 🌸")
                except Exception as e:
                    st.error(f"حدث خطأ أثناء الاتصال بقاعدة البيانات: {e}")

    else:
        st.info("👈 يرجى رفع صورة من القائمة الجانبية لبدء التحليل.")

# ==========================================
# TAB 2: USER FEEDBACK & ANALYTICS
# ==========================================
with tab_analytics:
    st.header("📊 لوحة تحليلات تقييمات المستخدمين (Analytics Dashboard)")

    df_feedback = load_feedbacks()

    if not df_feedback.empty and "Rating" in df_feedback.columns:
        # تحويل عمود النجوم إلى أرقام
        df_feedback['Rating'] = pd.to_numeric(df_feedback['Rating'], errors='coerce')
        df_feedback = df_feedback.dropna(subset=['Rating'])

        m1, m2, m3 = st.columns(3)
        m1.metric("إجمالي التقييمات", len(df_feedback))
        m2.metric("متوسط التقييم", f"{df_feedback['Rating'].mean():.2f} / 5.0 ⭐")
        m3.metric("نسبة الرضا العالي", f"{(df_feedback['Rating'] >= 4).mean() * 100:.1f}%")

        st.divider()

        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.subheader("توزيع النجوم والتقييمات")
            st.bar_chart(df_feedback['Rating'].value_counts())

        with col_chart2:
            st.subheader("متوسط التقييم حسب نوع المحتوى")
            if "Category" in df_feedback.columns:
                st.bar_chart(df_feedback.groupby('Category')['Rating'].mean())

        st.subheader("📝 سجل الآراء والتعليقات الحية:")
        st.dataframe(df_feedback, use_container_width=True)
    else:
        st.warning("لا توجد تقييمات مسجلة حتى الآن في السحابة.")
