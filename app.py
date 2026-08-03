import io
import requests
from PIL import Image, ImageStat
import google.generativeai as genai
import numpy as np
from sklearn.cluster import KMeans
import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION & EXACT PINK/WHITE CSS
# ==========================================
st.set_page_config(
    page_title="Lumina AI Assistant",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling: Matching the exact screenshot design
st.markdown("""
<style>
    /* Global App Background - Pure Clean White */
    .stApp {
        background-color: #FFFFFF !important;
        color: #2D2D2D !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Main Header Card - Pure White with Soft Pink Border */
    .main-header {
        background-color: #FFFFFF !important;
        padding: 35px 20px;
        border-radius: 28px;
        text-align: center;
        margin-bottom: 30px;
        border: 2px solid #F8D7E3 !important;
        box-shadow: 0 4px 20px rgba(248, 215, 227, 0.2);
    }
    
    .main-header h1 {
        color: #2B2B2B !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        margin-bottom: 12px !important;
    }
    
    .main-header .sub-title {
        color: #333333 !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        margin-bottom: 8px !important;
    }

    .main-header .tags {
        color: #B85B75 !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }

    /* Cards / Containers - White with Light Pink Borders */
    .aesthetic-card {
        background-color: #FFFFFF !important;
        border-radius: 20px !important;
        padding: 26px !important;
        margin-bottom: 25px !important;
        border: 1.5px solid #F9E2EB !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02) !important;
    }

    .aesthetic-card h3 {
        color: #8D5B66 !important;
        font-weight: 700 !important;
    }

    /* Custom Buttons - Rose / Pink Dust Gradient */
    .stButton>button {
        background: linear-gradient(135deg, #E2889B 0%, #D87088 100%) !important;
        color: #FFFFFF !important;
        border-radius: 16px !important;
        padding: 12px 28px !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(216, 112, 136, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(216, 112, 136, 0.45) !important;
    }

    /* Soft Blue Alert Container (Matching 👉 نحن بانتظارك اركع صورتك) */
    .soft-blue-box {
        background-color: #EBF3FA !important;
        color: #2B72B8 !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        margin-bottom: 20px !important;
        border: 1px solid #D2E4F5 !important;
    }

    /* Form Inputs */
    .stTextInput input, .stTextArea textarea {
        border-radius: 14px !important;
        border: 1.5px solid #F2D5E0 !important;
        background-color: #FFFFFF !important;
        color: #333333 !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #E2889B !important;
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
            user_friendly_error = f"حدث خطأ أثناء المعالجة: {error_str}"
        return None, user_friendly_error


# ==========================================
# 4. MAIN INTERFACE (EXACT SCREENSHOT MATCH)
# ==========================================

# Banner Header (Matching exact style from picture)
st.markdown("""
<div class="main-header">
    <div style="font-size: 3rem; margin-bottom: 10px;">🌸</div>
    <h1>Lumina AI</h1>
    <div class="sub-title">Your Smart Content Assistant | مساعدك الذكي للمحتوى</div>
    <div class="tags">حلّل • حسّن • أنشئ | Analyze • Improve • Create</div>
</div>
""", unsafe_allow_html=True)

# Minimal Sidebar
with st.sidebar:
    st.markdown("### 🌸 Lumina AI")
    st.info("مساعدك الذكي لتحليل الهويات البصرية والصور بنقرة واحدة.")
    
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        with st.expander("🔑 إعداد المفتاح البرمجي"):
            api_key = st.text_input("أدخل مفتاح Gemini API Key:", type="password")

# Upload Area
st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
st.markdown("<div class='soft-blue-box'>👈 نحن بانتظارك، قم برفع صورتك للتحليل الجمالي الاستراتيجي:</div>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png", "webp"])
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
        st.write(f"💡 **درجة الإضاءة (Brightness):** `{brightness}/255`")
        
        if is_pin_ideal:
            st.success("✅ أبعاد الصورة مثالية لمنصة Pinterest (نسبة 2:3)!")
        else:
            st.info("💡 نصيحة: يُفضل قص الصورة بنسبة طولية (2:3) للحصول على أفضل انتشار بصري.")
            
        st.markdown("#### 🎨 لوحة الألوان السائدة (K-Means Palette):")
        cols = st.columns(len(colors))
        for idx, hex_code in enumerate(colors):
            with cols[idx]:
                st.markdown(f"<div style='background-color:{hex_code}; height:40px; border-radius:10px; border:1px solid #F0D5E1;'></div>", unsafe_allow_html=True)
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
                    st.warning(error)
                else:
                    st.markdown("---")
                    st.markdown("### 📝 تقرير التحليل الإبداعي")
                    st.write(ai_result)
    st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # 5. FEEDBACK SYSTEM (At the bottom)
    # ==========================================
    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
    st.markdown("### 💬 تقييم تجربة المستخدم (Feedback Loop)")
    
    with st.form("feedback_form"):
        rating = st.slider("ما مدى رضاك عن دقة التحليل الجمالي؟", 1, 5, 5)
        comments = st.text_area("شاركونا رأيكم وملاحظاتكم لتطوير المنصة:")
        submit_feedback = st.form_submit_button("إرسال التقييم 📤")
        
        if submit_feedback:
            WEBHOOK_URL = "https://script.google.com/macros/s/AKfycby5jFANTTKQSC3xYeo_LXJ1mYsDDPDJgo_TW_M4thXp4Q6vgo_9SxGma_KJAjkAldcy/exec"
            payload = {"rating": rating, "comments": comments, "filename": uploaded_file.name}
            try:
                requests.post(WEBHOOK_URL, json=payload, timeout=5)
                st.balloons()
                st.success("شكراً لك! تم تسليم تقييمك بنجاح في قاعدة البيانات السحابية 🎉")
            except:
                st.info("شكراً لمشاركتك التقييم! ✨")
    st.markdown("</div>", unsafe_allow_html=True)
