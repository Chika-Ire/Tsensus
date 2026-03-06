import streamlit as st
import time
import RAG_assisstant3
import data_utils2 as data_utils
import database_query3 as database_query

st.set_page_config(
    page_title="彩砖选课AI",
    layout='wide'
)

st.title("彩砖选课AI（0.5 Beta）")
st.caption("Powered by Deepseek V3.2 | Streamlit")

# ==========================================
# 0. 定义反馈表单弹窗 (st.dialog)

# ==========================================
@st.dialog("🚀 30秒提交反馈，帮助学弟学妹！")
def teacher_evaluation_dialog():
    # 1. 禁用自动清空，改为手动控制逻辑
    with st.form("teacher_evaluation_form_dialog", clear_on_submit=False):
  
        st.caption(" 提示：下拉框可以打字搜索，有个多选也是框，别看漏了QvQ")
        st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
        st.subheader("1️⃣ 基础信息")

        teacher_options = data_utils.get_teacher_options()
        
        # 使用 key 绑定状态，确保 rerun 时数据不丢失
        selected_teacher = st.selectbox(
            "教师姓名 (必填)", 
            options=teacher_options,
            format_func=lambda x: x["label"] if x else "",
            index=None,
            placeholder="🔎 输入关键字搜索教师...",
            key="eval_teacher" # 绑定 Key
        )
        
        st.subheader("2️⃣ 考勤细节")
        attendance_freq = st.radio(
            "签到频率", 
            ["未选择", "每节必签", "看心情签到", "几乎不签到"], 
            horizontal=True,
            key="eval_freq"
        )
        
        attendance_method = st.multiselect(
            "签到方式", 
            options=["位置", "二维码", "手势", "数字", "拍照", "普通签到"],
            placeholder="请选择签到方式（可多选）",
            key="eval_method"
        )

        roll_call = st.radio("课上有无点名", ["未选择", "不点名", "会点名"], horizontal=True, key="eval_roll")
        roll_call_logic = st.radio("点名逻辑", ["未选择", "有提前预告", "无预告突击点名", "每节课必点名"], horizontal=True, key="eval_logic")
        
        st.subheader("3️⃣ 教学与考核")
        interaction_style = st.radio("交互风格", ["未选择", "照本宣科", "生动有趣", "严厉认真"], horizontal=True, key="eval_style")
        
        col_exam, col_grade = st.columns(2)
        with col_exam:
            exam_tips = st.radio("划重点", ["未选择", "会划重点", "不划重点"], horizontal=True, key="eval_tips")
        with col_grade:
            grading_style = st.radio("给分风格", ["未选择", "严格按照扣分标准", "求情可捞（熟悉可捞）", "一键全捞"], horizontal=True, key="eval_grading")
        
        workload = st.radio("平时作业量", ["未选择", "几乎没作业", "作业量适中", "作业极多/耗时"], horizontal=True, key="eval_workload")

        st.subheader("4️⃣ 备注")
        special_notes = st.text_area("这位老师的特殊情况 (非必填)", placeholder="例如：老师上课不让看手机...", key="eval_notes")
        
        submitted = st.form_submit_button("🚀 匿名提交情报", use_container_width=True, type="primary")
        
        if submitted:
            # --- 校验逻辑保持不变 ---
            is_valid = True
            error_messages = []
            
            if selected_teacher is None:
                is_valid = False
                error_messages.append("请选择【教师姓名】")
                
            if not attendance_method:
                is_valid = False
                error_messages.append("请至少选择一种【签到方式】")

            required_check = {
                "签到频率": attendance_freq,
                "交互风格": interaction_style,
                "划重点": exam_tips,
                "给分风格": grading_style,
                "作业量": workload,
                "有无点名": roll_call
            }
            
            for label, value in required_check.items():
                if value == "未选择":
                    is_valid = False
                    error_messages.append(f"请填写【{label}】")

            # 联动逻辑
            final_roll_call_logic = roll_call_logic
            if roll_call == "会点名" and roll_call_logic == "未选择":
                is_valid = False
                error_messages.append("既然选了“会点名”，请务必选择对应的【点名逻辑】")

            # --- 执行提交 ---
            if is_valid:
                methods_str = ", ".join(attendance_method)
                form_data = {
                    "teacher_id": selected_teacher["teacher_id"], 
                    "attendance_freq": attendance_freq,
                    "attendance_method": methods_str,
                    "roll_call": roll_call,
                    "roll_call_logic": final_roll_call_logic if roll_call == "会点名" else "未选择", 
                    "interaction_style": interaction_style,
                    "exam_tips": exam_tips,
                    "grading_style": grading_style,
                    "workload": workload,
                    "special_notes": special_notes,
                    "timestamp": time.time()
                }
                
                if data_utils.save_survey_to_db(form_data):
                    st.success(f"成功提交【{selected_teacher['label']}】的情报！")
                    st.balloons()
                    # 提交成功后清空 Session State 中的相关值（可选）
                    # 或者直接通过 st.rerun() 刷新页面，这会重置所有 dialog 内的状态
                    time.sleep(1.5) 
                    st.rerun() 
                else:
                    st.error("存储失败，请检查数据库连接。")
            else:
                # 校验失败时，因为 clear_on_submit=False 且有 key 绑定
                # 用户填过的内容会完整保留在界面上
                for msg in error_messages:
                    st.error(msg)
# ==========================================
# 3. 顶部进度条与数据收集入口
# ==========================================

# 获取实时进度数据
try:
    covered, total = data_utils.get_collection_progress()
    progress_percentage = covered / total if total > 0 else 0
except:
    covered, total, progress_percentage = 0, 1059, 0 # 防止数据库未初始化报错

# 容器化布局，保证视觉紧凑
progress_container = st.container()

with progress_container:
    # 进度条描述
    col_text, col_metric = st.columns([3, 1])
    with col_text:
        st.markdown(f"### 🎯 情报点亮进度: {progress_percentage:.1%}")
        st.caption(f"已有 {covered} 名教师获得至少一条评价数据，目标覆盖全校 {total} 名教学人员")

    # 显示进度条
    st.progress(progress_percentage)

    # --- 强化版数据收集按键 ---
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
    
    # 使用 st.button 的 use_container_width 参数使其占满宽度，更加醒目
    # 配合一些简单的 Markdown CSS 模拟大按钮视觉
    st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #FF4B4B;
            color: white;
            height: 3em;
            width: 100%;
            border-radius: 10px;
            border: none;
            font-size: 20px;
            font-weight: bold;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }
        div.stButton > button:first-child:hover {
            background-color: #FF2B2B;
            transform: translateY(-2px);
            box-shadow: 0px 6px 15px rgba(0,0,0,0.2);
        }
        </style>
    """, unsafe_allow_html=True)

if st.button("🚀 30秒贡献一条情报，帮助学弟学妹！", use_container_width=True):
    teacher_evaluation_dialog()

st.divider() 

# 1. 初始化AI

@st.cache_resource 
def init_assistant():
    return RAG_assisstant3.API_Assistant()

assistant = init_assistant()


# 2. Deepseek启动！

if user_input := st.chat_input("这里查询，请输入教师姓名..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    

    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        with st.status("🧠 正在烧烤你的需求...", expanded=True) as status:
            st.write("1️⃣ 正在进行意图识别与参数提取...")
            search_params = assistant.extract_params(user_input)
            st.code(f"意图解析结果: {search_params}", language="json")
            
            if search_params.get("intent") == "chat":
                st.write("2️⃣ 识别为日常闲聊，跳过数据库检索。")
                final_answer = "暂不支持日常聊天，请出门左转找DeepSeek本体QvQ"
            else:
                st.write("2️⃣ 正在查询本地课程数据库...")
                db_results = database_query.query_courses(search_params)
                st.write(f"数据库命中: 共找到 {len(db_results)} 条相关课程记录。")
                
                st.write("3️⃣ 正在生成最终情报总结...")
                final_answer = assistant.generate_final_answer(user_input, db_results)
            
            status.update(label="处理完成！", state="complete", expanded=False) 
        
        full_response = ""
        for chunk in final_answer:
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.01) 
        
        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": final_answer})

