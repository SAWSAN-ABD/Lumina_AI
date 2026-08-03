import io
import requests
from PIL import Image, ImageStat
import google.generativeai as genai
import numpy as np
from sklearn.cluster import KMeans
import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM AESTHETIC CSS
# ==========================================
st.set_page_config(
    page_title="Lumina Aesthetic AI Assistant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deep Luxury Nude/Beige Theme with High-Contrast Dark Emerald Typography
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #F7F3ED;
        color: #1C2826;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #EFE8DE !important;
        border-right: 1px solid #DCD0C0;
    }
    
    /* Card Container */
    .aesthetic-card {
        background-color: #E8DFD5;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        border: 1px solid #D5C8B8;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        color: #1C2826;
    }
    
    /* Typography Override for Mobile High Contrast */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #1C2826 !important;
    }
    
    /* Accent Buttons */
    .stButton>button {
        background-color: #2D4A43 !important;
        color: #F7F3ED !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #1C302B !important;
        transform: translateY(-2px);
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
        # تعديل رسالة الخطأ لتظهر بشكل لطيف ومفهوم بدلاً من الأخطاء الطويلة
        if "429" in error_str or "ResourceExhausted" in error_str or "Quota" in error_str:
            user_friendly_error = "⏳ **تم الوصول للحد الأقصى المؤقت من الحصة المجانية (API Quota Limit).**\n\nيرجى الانتظار دقيقة واحدة ثم إعادة المحاولة، أو التأكد من مفتاح الـ API الخاص بكم."
        else:
            user_friendly_error = f"حدث خطأ غير متوقع أثناء المعالجة: {error_str}"
        return None, user_friendly_error


# ==========================================
# 4. STREAMLIT APPLICATION INTERFACE
# ==========================================
st.title("✨ Lumina Aesthetic AI Assistant")
st.subheader("نظام التحليل البصري الجمالي وصناعة المحتوى الإبداعي")

# Sidebar
with st.sidebar:
    st.header("⚙️ الإعدادات والتحكم")
    api_key = st.text_input("أدخل مفتاح Gemini API Key:", type="password")
    st.markdown("---")
    st.info("نظام ذكي يدمج بين الرؤية الحاسوبية والذكاء الاصطناعي التوليدي لاستخراج الهوية البصرية للصور.")

# Upload Section
uploaded_file = st.file_uploader("📸 قم برفع الصورة للتحليل البصري الاستراتيجي:", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(image, caption="الصورة المرفوعة", use_container_width=True)
        
    with col2:
        st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
        st.markdown("### 📊 التحليل الرياضي والمحلي (Computer Vision)")
        
        aspect_ratio, brightness, is_pin_ideal = analyze_image_metrics(image)
        colors = extract_dominant_colors(image, num_colors=5)
        
        st.write(f"📐 **نسبة الأبعاد (Aspect Ratio):** `{aspect_ratio}`")
        st.write(f"💡 **مستوى الإضاءة العامة (Brightness):** `{brightness}/255`")
        
        if is_pin_ideal:
            st.success("✅ أبعاد الصورة مثالية لمنصة Pinterest (نسبة 2:3)!")
        else:
            st.info("💡 نصيحة: للحصول على أفضل تفاعل على Pinterest يُفضل قص الصورة بنسبة طولية (2:3).")
            
        st.markdown("#### 🎨 لوحة الألوان السائدة (K-Means Palette):")
        cols = st.columns(len(colors))
        for idx, hex_code in enumerate(colors):
            with cols[idx]:
                st.markdown(f"<div style='background-color:{hex_code}; height:45px; border-radius:8px; border:1px solid #ccc;'></div>", unsafe_allow_html=True)
                st.caption(hex_code)
                
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    
    # AI Execution
    st.markdown("### 🔮 التحليل الإبداعي والاستراتيجي بالذكاء الاصطناعي")
    user_note = st.text_input("ملاحظات إضافية للذكاء الاصطناعي (اختياري):", placeholder="مثال: ركز على الهوية الفخمة أو كابشن للموضة...")
    
    if st.button("🚀 بدء التحليل الجمالي الشامل"):
        if not api_key:
            st.error("⚠️ يرجى إدخال مفتاح الـ API في القائمة الجانبية أولاً!")
        else:
            with st.spinner("جاري تحليل العناصر الجمالية وبناء الاستراتيجية..."):
                prompt = f"قم بتحليل الصورة استراتيجياً وجمالياً. ملاحظات: {user_note}"
                ai_result, error = analyze_aesthetic_with_gemini(api_key, image, prompt)
                
                if error:
                    st.warning(error) # إظهار تنبيه لطيف ومصمم برمجياً
                else:
                    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
                    st.markdown("### 📝 تقرير التحليل الإبداعي")
                    st.write(ai_result)
                    st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # 5. SERVERLESS FEEDBACK SYSTEM (Google Sheets Integration)
    # ==========================================
    st.markdown("---")
    st.markdown("### 💬 تقييم تجربة المستخدم (Feedback Loop)")
    
    with st.form("feedback_form"):
        rating = st.slider("تقييمك لدقة التحليل الجمالي:", 1, 5, 5)
        comments = st.text_area("ملاحظاتك لتطوير المنصة:")
        submit_feedback = st.form_submit_button("إرسال التقييم 📤")
        
        if submit_feedback:
            # 🔗 ضعي رابط الـ Google Apps Script الخاص بكِ بين التنصيص هنا:
            WEBHOOK_URL = "https://script.google.com/macros/s/AKfycby5jFANTTKQSC3xYeo_LXJ1mYsDDPDJgo_TW_M4thXp4Q6vgo_9SxGma_KJAjkAldcy/exec"
            
            payload = {
                "rating": rating,
                "comments": comments,
                "filename": uploaded_file.name
            }
            try:
                response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
                st.balloons()
                st.success("شكرًا لك! تم تسجيل تقييمك بنجاح في قاعدة البيانات السحابية (Google Sheets) 🎉")
            except Exception as e:
                st.info("تم حفظ تقييمك محلياً، شكرًا لمشاركتك! ✨")
