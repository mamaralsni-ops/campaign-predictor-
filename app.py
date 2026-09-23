import os

# إنشاء ملف المتطلبات تلقائياً في حال عدم وجوده
if not os.path.exists("requirements.txt"):
    with open("requirements.txt", "w") as f:
        f.write("streamlit\npandas\nscikit-learn\n")

import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# إعداد واجهة التطبيق
st.set_page_config(
    page_title="نظام التنبؤ بالحملات - رويال واتش",
    page_icon="📊",
    layout="centered"
)

st.title("📊 نظام التنبؤ بالحملات الإعلانية")
st.caption("الجيل السادس للتسويق الإلكتروني | رويال واتش")
st.markdown("---")

# 1. إعداد البيانات الحقيقية للـ 10 حملات مع ترميز الموديلات المنفصلة
# watch_model_code: 0=بودجار, 1=كوران, 2=سكيمي, 3=صلاة, 4=أوليفس, 5=شواحن, 6=خدمات
# target_gender: 0=رجالي, 1=نسائي, 2=أصحاب أعمال
# launch_timing: 0=بداية (1-10), 1=منتصف (11-20), 2=نهاية (21-30)
# hook_type: 0=فخامة/هدية, 1=حل مشكلة, 2=سعر مباشر, 3=تحمل, 4=خدمات

@st.cache_resource
def train_model():
    real_campaigns_encoded = {
        'watch_model_code': [0, 5, 3, 1, 1, 3, 4, 2, 2, 6], 
        'target_gender':    [0, 0, 0, 0, 0, 0, 1, 0, 0, 2],  
        'daily_budget_usd': [0.28, 0.28, 0.28, 1.42, 0.28, 0.28, 0.28, 0.28, 0.28, 0.14], 
        'days':             [4, 5, 4, 4, 4, 4, 4, 4, 4, 4],   
        'reach':            [2909, 5810, 4048, 8128, 1680, 2669, 162, 3035, 1569, 716], 
        'launch_timing':    [0, 2, 1, 1, 1, 1, 1, 1, 0, 0],   
        'hook_type':        [0, 1, 2, 0, 0, 0, 0, 3, 0, 4]    
    }
    df = pd.DataFrame(real_campaigns_encoded)
    features = ['watch_model_code', 'target_gender', 'daily_budget_usd', 'days', 'launch_timing', 'hook_type']
    X = df[features]
    y = df['reach']
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model, features

ml_model, features = train_model()

# 2. واجهة إدخال بيانات الحملة الجديدة
with st.form("campaign_form"):
    st.subheader("📝 أدخل تفاصيل الحملة الجديدة")
    
    watch_model = st.selectbox("طراز / ماركة المنتج:", [
        "ساعة بودجار (Poedagar)", 
        "ساعة كوران (Curren)", 
        "ساعة سكيمي (SKMEI)", 
        "ساعة مواقيت الصلاة", 
        "ساعة أوليفس (Olevs)", 
        "إلكترونيات / شواحن", 
        "خدمات تسويق"
    ])
    
    price = st.number_input("سعر المنتج (بالدينار الليبي):", min_value=10, max_value=2000, value=290, step=5)
    daily_budget = st.number_input("الميزانية اليومية ($):", min_value=1.0, max_value=100.0, value=4.0, step=0.5)
    days = st.slider("مدة الحملة (أيام):", min_value=1, max_value=30, value=4)
    launch_day = st.slider("يوم الإطلاق في الشهر (1-31):", min_value=1, max_value=31, value=19)
    
    hook = st.selectbox("نوع العرض / الهوك:", [
        "سعر مباشر وعرض واضح", 
        "فخامة وهدية", 
        "تحمل وأسلوب حياة", 
        "حل مشكلة تقنية", 
        "حث أصحاب مشاريع"
    ])
    
    target_gender = st.selectbox("الفئة المستهدفة:", ["رجالي", "نسائي", "أصحاب مشاريع"])
    
    submit_button = st.form_submit_button("🔮 تحليل واختبار الحملة", use_container_width=True)

# 3. معالجة النتيجة والتنبؤ
if submit_button:
    model_map = {"ساعة بودجار (Poedagar)":0, "ساعة كوران (Curren)":1, "ساعة سكيمي (SKMEI)":2, "ساعة مواقيت الصلاة":3, "ساعة أوليفس (Olevs)":4, "إلكترونيات / شواحن":5, "خدمات تسويق":6}
    hook_map = {"فخامة وهدية":0, "حل مشكلة تقنية":1, "سعر مباشر وعرض واضح":2, "تحمل وأسلوب حياة":3, "حث أصحاب مشاريع":4}
    gender_map = {"رجالي":0, "نسائي":1, "أصحاب مشاريع":2}
    
    timing_code = 0 if launch_day <= 10 else (1 if launch_day <= 20 else 2)
    
    # التنبؤ بالوصول
    input_df = pd.DataFrame([[
        model_map[watch_model], 
        gender_map[target_gender], 
        daily_budget, 
        days, 
        timing_code, 
        hook_map[hook]
    ]], columns=features)
    
    predicted_reach = int(ml_model.predict(input_df)[0])
    
    # حساب تقييم ملاءمة السعر مقابل المرتب (800 د.ل)
    ratio = price / 800.0
    if ratio <= 0.25: price_score = 10.0
    elif ratio <= 0.50: price_score = 10.0 - ((ratio - 0.25) / 0.25) * 5.0
    elif ratio <= 1.00: price_score = 5.0 - ((ratio - 0.50) / 0.50) * 4.0
    else: price_score = 0.0
    
    final_score = (price_score / 10.0) * 20.0 + (8.0/10.0)*30.0 + (9.0 if timing_code==1 else 15.0) + 15.0 + 20.0
    
    st.markdown("---")
    st.subheader("📊 نتائج التنبؤ والتحليل")
    
    st.metric(label="🎯 نسبة النجاح المتوقعة", value=f"{final_score:.1f}%")
    st.metric(label="📢 الوصول التقديري المتوقع", value=f"~{predicted_reach:,} شخص")
    
    st.info(f"🏷️ **تقييم ملاءمة السعر:** {price_score:.1f} / 10 (السعر يشكل {ratio*100:.1f}% من متوسط المرتب 800 د.ل)")
    
    if price_score < 7.0:
        st.warning("💡 **توصية السعر:** السعر أعلى من النطاق الشائع للشراء السريع، يفضل إضافة عرض 'التوصيل مجاناً' لرفع نسبة التحويل.")
    if timing_code == 1:
        st.warning("💡 **توصية الشحن:** بما أن الإطلاق في منتصف الشهر، نسّق مع شركة الشحن لتسليم الطلبات مع بداية الشهر القادم لضمان توفر السيولة لدى الزبائن.")
