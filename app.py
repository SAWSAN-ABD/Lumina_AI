import io
import requests
from PIL import Image, ImageStat
import google.generativeai as genai
import numpy as np
from sklearn.cluster import KMeans
import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION & ORIGINAL PINK NUDE CSS
# ==========================================
st.set_page_config(
    page_title="Lumina Aesthetic AI Assistant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium Pink Nude & Aesthetic Soft Beige Theme
st.markdown("""
<style>
    /* Global App Background */
    .stApp {
        background-color: #FAF5F0 !important;
        color: #4A3E3D !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #F4E3D7 0%, #E8D1C5 100%);
        padding: 35px 20px;
        border-radius: 24px;
        text-align: center;
        margin-bottom: 30px;
        border: 1px solid #E2C7B8;
        box-shadow: 0 8px 20px rgba(226, 199, 184, 0.25);
    }
    
    .main-header h1 {
        color: #3D2C2E !important;
        font-size: 2.3rem !important;
        font-weight: 700 !important;
        margin-bottom: 10px !important;
    }
    
    .main-header p {
        color: #6E5A58 !important;
        font-size: 1.15rem !important;
    }

    /* Cards / Containers */
    .aesthetic-card {
        background-color: #FFFFFF !important;
        border-radius: 20px !important;
        padding: 28px !important;
        margin-bottom: 25px !important;
        border: 1px solid #F0E2D8 !important;
        box-shadow: 0 6px 18px rgba(74, 62, 61, 0.03) !important;
    }

    /* Custom Buttons - Pink Nude */
    .stButton>button {
        background: linear-gradient(135deg, #E0B09A 0%, #D09A83 100%) !important;
        color: #FFFFFF !important;
        border-radius: 16px !important;
        padding: 14px 32px !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(208, 154, 131, 0.35) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(208, 154, 131, 0.45) !important;
    }

    /* Text inputs & textareas */
    .stTextInput input, .stTextArea textarea {
        border-radius: 14px !important;
        border: 1px solid #E8D7CC !important;
        background-color: #FAF5F0 !important;
        color: #3D2C2E !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. LOCAL COMPUTER VISION & MATH FUNCTIONS
# ==========================================
def extract_dominant_colors(image, num_colors=5):
    """Extract dominant colors using K-Means Clustering locally."""
    img = image.copy()
    img.thumbnail((150, 150))
    img_np = np.array(img)
    
    if len(img_np.shape) == 2:
        img_np = np.stack((img_np,) * 3, axis=-1)
    elif img_np.shape[2] == 4:
        img_np = img_np[:, :, :3]

    pixels = img_np.reshape(-1, 3)
    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=5)
    kmeans.fit(pixels)
    
    colors = kmeans.cluster_centers_.astype(int)
    hex_colors = [f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}" for c in colors]
    return hex_colors

def analyze_image_metrics(image):
    """Calculate Aspect Ratio and Pinterest Fitness Score locally."""
    width, height = image.size
    aspect_ratio = round(width / height, 2)
    gray_img = image.convert('L')
    stat = ImageStat.Stat(gray_img)
    brightness = round(stat.mean[0], 2)
    is_pinterest_ideal = 0.6 <= aspect_ratio <= 0.75
    return aspect_ratio, brightness, is_pinterest_ideal


# ==========================================
# 3. GEMINI AI PIPELINE WITH SAFE ERROR HANDLING
# ==========================================
def analyze_aesthetic_with_gemini(api_key, image, user_prompt):
    """Call Gemini API wrapped in safe exception handling."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        system_instruction = """
        You are an elite Aesthetic AI Creative Director and Visual Strategist.
        Analyze the image and return a structured analysis covering:
        1. Visual Aesthetic Vibe (e.g., Minimalist Warm, Cyberpunk, Dark Academia).
        2. Color Psychology & Brand Emotional Perception.
        3. Suggested Typography Pairings (Header & Body fonts with Hex contrast).
        4. Smart Pinterest Pin Data (SEO Title, Rich Description, Recommended Boards).
        5. Creative Scene Expansion (Prompts for Midjourney/DALL-E to expand this visual universe).
        Keep the response highly elegant, structured, and inspiring in Arabic.
        """
        
        response = model.generate_content([system_instruction, user_prompt, image])
        return response.text, None

    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "ResourceExhausted" in error_str or "Quota" in error_str:
            user_friendly_error = "⏳ **تم الوصول للحد الأقصى المؤقت من الحصة المجانية (API Quota Limit).**\n\nيرجى الانتظار دقيقة واحدة ثم إعادة المحاولة، أو التأكد من مفتاح الـ API الخاص بكم."
        else:
            user_friendly_error = f"حدث خطأ غير متوقع أثناء المعالجة: {error_str}"
        return None, user_friendly_error


# ==========================================
# 4. MAIN INTERFACE (PINK NUDE ELEGANCE)
# ==========================================

# Banner Title
st.markdown("""
<div class="main-header">
    <h1>✨ Lumina Aesthetic AI Assistant</h1>
    <p>نظام التحليل البصري الجمالي وصناعة المحتوى الإبداعي الاستراتيجي</p>
</div>
""", unsafe_allow_html=True)

# Sidebar (Minimalist Info & Key fallback if needed)
with st.sidebar:
    st.markdown("### 🌸 عن النظام")
    st.info("منصة ذكية تحلل التكوين الجمالي للصور واستخراج الهويات البصرية باستخدام الذكاء الاصطناعي والرؤية الحاسوبية.")
    
    # API Key retrieval (Checks secrets first, fallback to hidden expander)
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        with st.expander("🔑 إعداد المفتاح البرمجي (عند الحاجة)"):
            api_key = st.text_input("أدخل Gemini API Key:", type="password")

# Upload Section
st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("📸 قم برفع الصورة للتحليل البصري الشامل:", type=["jpg", "jpeg", "png", "webp"])
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
        st.image(image, caption="الصورة المرفوعة", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
        st.markdown("### 📊 التحليل الرياضي والبصري (Computer Vision)")
        
        aspect_ratio, brightness, is_pin_ideal = analyze_image_metrics(image)
        colors = extract_dominant_colors(image, num_colors=5)
        
        st.write(f"📐 **نسبة الأبعاد (Aspect Ratio):** `{aspect_ratio}`")
        st.write(f"💡 **مستوى الإضاءة (Brightness):** `{brightness}/255`")
        
        if is_pin_ideal:
            st.success("✅ أبعاد الصورة مثالية لمنصة Pinterest (نسبة 2:3)!")
        else:
            st.info("💡 نصيحة: يُفضل قص الصورة بنسبة طولية (2:3) للحصول على أفضل انتشار بصري.")
            
        st.markdown("#### 🎨 لوحة الألوان السائدة (K-Means Palette):")
        cols = st.columns(len(colors))
        for idx, hex_code in enumerate(colors):
            with cols[idx]:
                st.markdown(f"<div style='background-color:{hex_code}; height:42px; border-radius:10px; border:1px solid #E2D2C7;'></div>", unsafe_allow_html=True)
                st.caption(hex_code)
                
        st.markdown("</div>", unsafe_allow_html=True)

    # AI Processing Section
    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
    st.markdown("### 🔮 التحليل الإبداعي بالذكاء الاصطناعي")
    user_note = st.text_input("ملاحظات إضافية للذكاء الاصطناعي (اختياري):", placeholder="مثال: ركز على الهوية الفخمة، أو كابشن موجه للموضة...")
    
    if st.button("🚀 بدء التحليل الجمالي الشامل"):
        if not api_key:
            st.error("⚠️ يرجى التأكد من وجود مفتاح الـ API للبدء!")
        else:
            with st.spinner("جاري تحليل العناصر الجمالية وبناء الاستراتيجية البصرية..."):
                prompt = f"قم بتحليل الصورة استراتيجياً وجمالياً. ملاحظات: {user_note}"
                ai_result, error = analyze_aesthetic_with_gemini(api_key, image, prompt)
                
                if error:
                    st.warning(error) # الرسالة اللطيفة عند انتهاء الكوتا
                else:
                    st.markdown("---")
                    st.markdown("### 📝 تقرير التحليل الإبداعي")
                    st.write(ai_result)
    st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # 5. FEEDBACK SYSTEM (At the very bottom!)
    # ==========================================
    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
    st.markdown("### 💬 تقييم تجربة المستخدم (Feedback Loop)")
    
    with st.form("feedback_form"):
        rating = st.slider("ما مدى رضاك عن دقة التحليل الجمالي؟", 1, 5, 5)
        comments = st.text_area("شاركونا رأيكم وملاحظاتكم لتطوير المنصة:")
        submit_feedback = st.form_submit_button("إرسال التقييم 📤")
        
        if submit_feedback:
            # 🔗 ضعي رابط Google Apps Script الخاص بكِ هنا:
            WEBHOOK_URL = "https://script.google.com/macros/s/AKfycby5jFANTTKQSC3xYeo_LXJ1mYsDDPDJgo_TW_M4thXp4Q6vgo_9SxGma_KJAjkAldcy/exec"
            payload = {"rating": rating, "comments": comments, "filename": uploaded_file.name}
            try:
                requests.post(WEBHOOK_URL, json=payload, timeout=5)
                st.balloons()
                st.success("شكراً لك! تم تسليم تقييمك بنجاح في قاعدة البيانات السحابية 🎉")
            except:
                st.info("شكراً لمشاركتك التقييم! ✨")
    st.markdown("</div>", unsafe_allow_html=True)
