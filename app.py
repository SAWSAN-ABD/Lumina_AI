import streamlit as st
from google import genai
from PIL import Image
import json
import pandas as pd
import os
from datetime import datetime

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(
    page_title="Lumina AI | Enterprise Cloud",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# إعداد محرك الذكاء الاصطناعي من Secrets
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=API_KEY)

# ملف التقييمات المحلي
FEEDBACK_FILE = "user_feedbacks.csv"

def init_feedback_store():
    if not os.path.exists(FEEDBACK_FILE):
        df = pd.DataFrame(columns=["Timestamp", "Rating", "Category", "Comment"])
        df.to_csv(FEEDBACK_FILE, index=False)

init_feedback_store()

# --- 2. الهيدر العام ---
st.markdown("""
    <div style="background-color: #0f172a; padding: 20px; border-radius: 10px; margin-bottom: 25px; text-align: center;">
        <h1 style="color: #ffffff; margin: 0; font-family: sans-serif;">✨ LUMINA AI</h1>
        <p style="color: #38bdf8; font-size: 16px; margin-top: 5px; font-weight: bold;">
            Analyze  →  Decide  →  Create
        </p>
    </div>
""", unsafe_allow_html=True)

# --- 3. إنشاء التبويبات ---
tab_workspace, tab_analytics = st.tabs(["🚀 منصة التحليل والإنشاء", "📊 تقييمات المستخدمين (Analytics)"])

# ==========================================
# TAB 1: LUMINA WORKSPACE
# ==========================================
with tab_workspace:
    st.sidebar.header("🔍 رفع الأصل البصري")
    uploaded_file = st.sidebar.file_uploader("اختر صورة للتحليل", type=["jpg", "jpeg", "png", "webp"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.sidebar.image(image, caption="الصورة المرفوعة", use_container_width=True)

        if st.sidebar.button("⚡ تشغيل التحليل الموحد", type="primary", use_container_width=True):
            with st.spinner("جاري تشغيل خط سير العمليات (Analyze → Decide → Create)..."):
                try:
                    # Prompt جديد واضح يلزم Gemini بتوليد كابشن وهاشتاغات حقيقية للـ Image
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
                        model='gemini-2.5-flash',
                        contents=[image, unified_prompt]
                    )

                    raw = response.text.strip().replace("```json", "").replace("```", "")
                    st.session_state["lumina_data"] = json.loads(raw)
                    st.session_state["current_image"] = image
                    st.success("✅ اكتمل التحليل بنجاح!")

                except Exception as e:
                    st.error(f"حدث خطأ أثناء معالجة الصورة: {e}")

    # عرض النتائج إذا كانت متوفرة
    if "lumina_data" in st.session_state:
        data = st.session_state["lumina_data"]

        # 🧠 Lumina Insight Box
        st.info(f"**🧠 Lumina Insight:**\n\n{data.get('lumina_insight', '')}")

        col_left, col_right = st.columns([1, 1.5])

        with col_left:
            st.subheader("🔍 Phase 1 & 2: التحليل والقرار")
            
            score = data.get("readiness_score", 85)
            st.metric(
                label="Publishing Readiness Score (جاهزية النشر)",
                value=f"{score}%",
                delta=data.get("readiness_status", "READY TO PUBLISH")
            )
            st.progress(score / 100)

            st.markdown(f"**نوع المحتوى:** `{data.get('category')}`")
            st.markdown(f"**الأصالة:** `{data.get('authenticity_score')}` ({data.get('status')})")

            st.write("**تفاصيل التقييم:**")
            for item in data.get("readiness_breakdown", []):
                st.write(f"- {item}")

            st.write("**المبررات الجنائية/البصرية:**")
            for r in data.get("reasoning", []):
                st.write(f"• {r}")

        with col_right:
            st.subheader("✨ Phase 3: Create (المقترحات الذكية والكابشن)")
            
            actions = data.get("smart_actions", [])
            titles = [act["title"] for act in actions]
            
            selected_tab = st.radio("اختر الإجراء المباشر:", titles, horizontal=True)

            for act in actions:
                if act["title"] == selected_tab:
                    st.text_area("المحتوى المولد:", value=act["content"], height=230)

        st.divider()

        # 💬 Ask Lumina Consultant
        st.subheader("💬 Ask Lumina (المستشار الذكي)")
        
        c1, c2, c3, c4 = st.columns(4)
        
        # استخدام Session State للتحكم بالنص المدخل بمرونة
        if "asked_question" not in st.session_state:
            st.session_state["asked_question"] = ""

        if c1.button("💡 كيف أحسن الصورة؟"): st.session_state["asked_question"] = "كيف أحسن الصورة؟"
        if c2.button("🔍 ليش اعتبرتها أصلية؟"): st.session_state["asked_question"] = "ليش اعتبرتها أصلية؟"
        if c3.button("👔 اكتب نسخة رسمية"): st.session_state["asked_question"] = "اكتب نسخة رسمية للمحتوى"
        if c4.button("🎯 مين الجمهور المناسب؟"): st.session_state["asked_question"] = "مين الجمهور المستهدف لهذه الصورة؟"

        user_input = st.text_input("أو اكتب سؤالك هنا:", value=st.session_state["asked_question"], key="chat_input")

        if user_input:
            with st.spinner("جاري استشارة Lumina..."):
                try:
                    consult_prompt = (
                        f"أجب على سؤال المستخدم التالي باللغة العربية بأسلوب احترافي ومختصر بناءً على تحليل هذه الصورة: '{user_input}'. "
                        f"سياق التحليل السابق: {json.dumps(data, ensure_ascii=False)}"
                    )
                    
                    contents_payload = [consult_prompt]
                    if "current_image" in st.session_state and st.session_state["current_image"] is not None:
                        contents_payload.insert(0, st.session_state["current_image"])

                    res = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=contents_payload
                    )
                    
                    st.markdown("### 🤖 إجابة المستشار الذكي:")
                    st.info(res.text)

                except Exception as e:
                    st.error(f"عذراً، حدث خطأ أثناء الرد: {e}")

        st.divider()

        # ⭐ قسم التقييم الخاص بالمستخدم
        st.subheader("⭐ تقييم تجربتك مع Lumina AI")
        with st.form("feedback_form"):
            rating = st.slider("تقييمك للدقة والجودة (من 1 إلى 5 نجوم):", 1, 5, 5)
            comment = st.text_input("ملاحظاتك أو تعليقك على النتيجة (اختياري):")
            submitted = st.form_submit_button("إرسال التقييم 🚀")

            if submitted:
                new_data = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Rating": rating,
                    "Category": data.get("category", "General"),
                    "Comment": comment
                }])
                new_data.to_csv(FEEDBACK_FILE, mode='a', header=False, index=False)
                st.balloons()
                st.success("شكراً لك! تم حفظ تقييمك بنجاح.")

    else:
        st.info("👈 يرجى رفع صورة من القائمة الجانبية وتفعيل التحليل لبدء العمل.")

# ==========================================
# TAB 2: USER FEEDBACK & ANALYTICS
# ==========================================
with tab_analytics:
    st.header("📊 لوحة تحليلات تقييمات المستخدمين (User Feedback Dashboard)")

    if os.path.exists(FEEDBACK_FILE):
        df_feedback = pd.read_csv(FEEDBACK_FILE)

        if not df_feedback.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric("إجمالي التقييمات", len(df_feedback))
            m2.metric("متوسط التقييم", f"{df_feedback['Rating'].mean():.2f} / 5.0 ⭐")
            m3.metric("نسبة الرضا العالي", f"{(df_feedback['Rating'] >= 4).mean() * 100:.1f}%")

            st.divider()

            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.subheader("توزيع التقييمات")
                st.bar_chart(df_feedback['Rating'].value_counts())

            with col_chart2:
                st.subheader("التقييمات حسب نوع الصورة")
                st.bar_chart(df_feedback.groupby('Category')['Rating'].mean())

            st.subheader("📝 سجل الآراء والتعليقات:")
            st.dataframe(df_feedback, use_container_width=True)
        else:
            st.warning("لا توجد تقييمات مسجلة حتى الآن.")
