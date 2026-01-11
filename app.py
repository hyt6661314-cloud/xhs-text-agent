"""
XHS Text Agent - 小红书创作小白 · 文字内容生成
A Streamlit app for generating weekly text content plans.
"""

import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from agent.state import get_state, update_state, DayContent
from agent.router import get_current_view, advance_onboarding
from agent.tools import generate_weekly_content, rewrite_day_content, generate_weekly_review


# Page config
st.set_page_config(
    page_title="小红书创作小白",
    page_icon="📝",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    .step-card {
        background: linear-gradient(135deg, #fff5f5 0%, #fff 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #ffe0e0;
    }
    .day-card {
        background: #fafafa;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #ff6b6b;
    }
    .content-section {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .tag {
        display: inline-block;
        background: #ffe0e0;
        color: #d63031;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        margin: 0.2rem;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


def render_header():
    """Render the app header."""
    st.markdown("""
    <div class="main-header">
        <h1>📝 小红书创作小白</h1>
        <p style="color: #666;">文字内容生成助手 · 帮你规划一周内容</p>
    </div>
    """, unsafe_allow_html=True)


def render_onboarding_niche():
    """Render niche selection step."""
    state = get_state()
    
    st.markdown("### 🎯 第一步：选择你的赛道/领域")
    st.markdown("你想在小红书分享什么类型的内容？")
    
    options = ["生活方式", "学习/成长", "职场/留学", "健康/健身", "副业/搞钱", "兴趣/爱好", "不确定"]
    
    cols = st.columns(4)
    for i, option in enumerate(options):
        with cols[i % 4]:
            if st.button(option, key=f"niche_{option}", use_container_width=True):
                state.niche = option
                state.current_step = "goal"
                update_state(state)
                st.rerun()


def render_onboarding_goal():
    """Render goal selection step."""
    state = get_state()
    
    st.markdown("### 🚀 第二步：你的目标是什么")
    st.markdown(f"赛道：**{state.niche}**")
    
    options = ["记录生活", "做个人IP", "副业/变现探索", "先试试看"]
    
    cols = st.columns(4)
    for i, option in enumerate(options):
        with cols[i % 4]:
            if st.button(option, key=f"goal_{option}", use_container_width=True):
                state.goal = option
                state.current_step = "style"
                update_state(state)
                st.rerun()
    
    if st.button("← 返回上一步", type="secondary"):
        state.niche = None
        state.current_step = "niche"
        update_state(state)
        st.rerun()


def render_onboarding_style():
    """Render style selection step."""
    state = get_state()
    
    st.markdown("### ✨ 第三步：选择内容风格")
    st.markdown(f"赛道：**{state.niche}** | 目标：**{state.goal}**")
    
    options = ["轻松日常", "实用干货", "记录型", "总结型"]
    
    cols = st.columns(4)
    for i, option in enumerate(options):
        with cols[i % 4]:
            if st.button(option, key=f"style_{option}", use_container_width=True):
                state.style = option
                state.current_step = "effort"
                update_state(state)
                st.rerun()
    
    if st.button("← 返回上一步", type="secondary"):
        state.goal = None
        state.current_step = "goal"
        update_state(state)
        st.rerun()


def render_onboarding_effort():
    """Render effort level selection step."""
    state = get_state()
    
    st.markdown("### ⏰ 第四步：你能投入多少精力")
    st.markdown(f"赛道：**{state.niche}** | 目标：**{state.goal}** | 风格：**{state.style}**")
    
    options = ["很少(1-2条/周)", "一般(3-4条/周)", "还可以(5-7条/周)", "不确定你来安排"]
    
    cols = st.columns(2)
    for i, option in enumerate(options):
        with cols[i % 2]:
            if st.button(option, key=f"effort_{option}", use_container_width=True):
                state.effort = option
                state.current_step = "constraints"
                update_state(state)
                st.rerun()
    
    if st.button("← 返回上一步", type="secondary"):
        state.style = None
        state.current_step = "style"
        update_state(state)
        st.rerun()


def render_onboarding_constraints():
    """Render constraints selection step."""
    state = get_state()
    
    st.markdown("### 🚫 第五步：有什么话题需要避免？")
    st.markdown(f"赛道：**{state.niche}** | 目标：**{state.goal}** | 风格：**{state.style}** | 精力：**{state.effort}**")
    
    options = ["不谈金钱/收入", "不谈情感隐私", "不涉及争议话题", "没有特别忌讳"]
    
    # Use checkboxes for multi-select
    selected = []
    cols = st.columns(2)
    for i, option in enumerate(options):
        with cols[i % 2]:
            if st.checkbox(option, key=f"constraint_{option}"):
                selected.append(option)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 返回上一步", type="secondary"):
            state.effort = None
            state.current_step = "effort"
            update_state(state)
            st.rerun()
    
    with col2:
        if st.button("继续 →", type="primary"):
            state.constraints = selected
            state.current_step = "custom"
            update_state(state)
            st.rerun()


def render_onboarding_custom():
    """Render custom note input step."""
    state = get_state()
    
    st.markdown("### 📝 最后一步：还有什么想补充的？")
    
    st.markdown("**你的选择：**")
    st.markdown(f"""
    - 赛道：{state.niche}
    - 目标：{state.goal}
    - 风格：{state.style}
    - 精力：{state.effort}
    - 避免话题：{', '.join(state.constraints) if state.constraints else '无'}
    """)
    
    custom_note = st.text_area(
        "自定义补充一句（可选）",
        placeholder="例如：我是大学生，想分享考研经验...",
        key="custom_note_input"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 返回上一步", type="secondary"):
            state.current_step = "constraints"
            update_state(state)
            st.rerun()
    
    with col2:
        if st.button("完成设置 ✓", type="primary"):
            state.custom_note = custom_note
            state.current_step = "ready"
            update_state(state)
            st.rerun()


def render_ready_to_generate():
    """Render the generate button screen."""
    state = get_state()
    
    st.markdown("### ✅ 设置完成！")
    
    st.markdown("**你的创作档案：**")
    st.markdown(f"""
    - 🎯 赛道：{state.niche}
    - 🚀 目标：{state.goal}
    - ✨ 风格：{state.style}
    - ⏰ 精力：{state.effort}
    - 🚫 避免：{', '.join(state.constraints) if state.constraints else '无特别限制'}
    - 📝 补充：{state.custom_note if state.custom_note else '无'}
    """)
    
    st.divider()
    
    if state.generation_error:
        st.error(state.generation_error)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("修改设置", type="secondary"):
            state.current_step = "niche"
            state.niche = None
            state.goal = None
            state.style = None
            state.effort = None
            state.constraints = []
            state.custom_note = ""
            update_state(state)
            st.rerun()
    
    with col2:
        if st.button("🎉 生成我的一周内容", type="primary", use_container_width=True):
            with st.spinner("正在生成内容，请稍候..."):
                days, error = generate_weekly_content(
                    niche=state.niche,
                    goal=state.goal,
                    style=state.style,
                    effort=state.effort,
                    constraints=state.constraints,
                    custom_note=state.custom_note
                )
                
                if error:
                    state.generation_error = error
                    update_state(state)
                    st.rerun()
                else:
                    state.weekly_plan = days
                    state.generation_error = None
                    update_state(state)
                    st.rerun()


def render_weekly_plan():
    """Render the weekly plan view."""
    state = get_state()
    
    st.markdown("### 📅 你的一周内容计划")
    st.markdown(f"赛道：**{state.niche}** | 风格：**{state.style}**")
    
    # Day cards
    for day in state.weekly_plan:
        with st.container():
            st.markdown(f"""
            <div class="day-card">
                <strong>第{day.day}天</strong>: {day.title}
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"👀 查看内容", key=f"view_{day.day}"):
                    state.viewing_day = day.day
                    update_state(state)
                    st.rerun()
            with col2:
                if st.button(f"✏️ 改写这条", key=f"rewrite_{day.day}"):
                    state.rewriting_day = day.day
                    state.rewrite_instruction = ""
                    update_state(state)
                    st.rerun()
    
    st.divider()
    
    # Weekly review section
    with st.expander("📊 周复盘与下周建议", expanded=False):
        render_weekly_review_form()
    
    st.divider()
    
    # Reset button
    if st.button("🔄 重新开始", type="secondary"):
        state.reset_all()
        update_state(state)
        st.rerun()


def render_view_day():
    """Render single day content view."""
    state = get_state()
    day_num = state.viewing_day
    
    # Find the day content
    day_content = None
    for d in state.weekly_plan:
        if d.day == day_num:
            day_content = d
            break
    
    if not day_content:
        st.error("找不到该天的内容")
        return
    
    st.markdown(f"### 第{day_num}天 内容详情")
    
    # Title
    st.markdown(f"**📌 标题**")
    st.info(day_content.title)
    
    # Hook
    st.markdown(f"**🎣 开头 Hook**")
    st.success(day_content.hook)
    
    # Bullets
    st.markdown(f"**📝 内容要点**")
    for bullet in day_content.bullets:
        st.markdown(f"• {bullet}")
    
    # CTA
    st.markdown(f"**💬 互动引导 (CTA)**")
    st.warning(day_content.cta)
    
    # Tags
    st.markdown(f"**🏷️ 标签**")
    tags_html = " ".join([f'<span class="tag">{tag}</span>' for tag in day_content.tags])
    st.markdown(tags_html, unsafe_allow_html=True)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 返回计划", type="secondary"):
            state.viewing_day = None
            update_state(state)
            st.rerun()
    with col2:
        if st.button("✏️ 改写这条", type="primary"):
            state.viewing_day = None
            state.rewriting_day = day_num
            update_state(state)
            st.rerun()


def render_rewrite_day():
    """Render rewrite interface for a single day."""
    state = get_state()
    day_num = state.rewriting_day
    
    # Find the day content
    day_content = None
    for d in state.weekly_plan:
        if d.day == day_num:
            day_content = d
            break
    
    if not day_content:
        st.error("找不到该天的内容")
        return
    
    st.markdown(f"### ✏️ 改写第{day_num}天内容")
    
    st.markdown("**当前标题：**")
    st.info(day_content.title)
    
    st.markdown("**输入改写要求：**")
    instruction = st.text_area(
        "告诉我怎么改",
        placeholder="例如：语气更轻松一点 / 内容简短一些 / 加入更多情感 / 换个角度写...",
        key="rewrite_instruction_input"
    )
    
    if state.generation_error:
        st.error(state.generation_error)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 取消", type="secondary"):
            state.rewriting_day = None
            state.generation_error = None
            update_state(state)
            st.rerun()
    
    with col2:
        if st.button("🔄 开始改写", type="primary", disabled=not instruction.strip()):
            with st.spinner("正在改写..."):
                new_content, error = rewrite_day_content(day_content, instruction)
                
                if error:
                    state.generation_error = error
                    update_state(state)
                    st.rerun()
                else:
                    # Update the weekly plan
                    for i, d in enumerate(state.weekly_plan):
                        if d.day == day_num:
                            state.weekly_plan[i] = new_content
                            break
                    
                    state.rewriting_day = None
                    state.viewing_day = day_num  # Show the updated content
                    state.generation_error = None
                    update_state(state)
                    st.rerun()


def render_weekly_review_form():
    """Render the weekly review form."""
    state = get_state()
    
    st.markdown("**回顾这周的计划，选择你的感受：**")
    
    # Best days multi-select
    day_options = [f"第{i}天" for i in range(1, 8)]
    
    best_selected = st.multiselect(
        "😊 感觉最好的内容（可多选）",
        options=day_options,
        key="review_best"
    )
    
    hardest_selected = st.multiselect(
        "😅 感觉最难的内容（可多选）",
        options=day_options,
        key="review_hardest"
    )
    
    pace = st.radio(
        "📈 下周的节奏偏好",
        options=["轻松一点", "多尝试新内容"],
        horizontal=True,
        key="review_pace"
    )
    
    notes = st.text_area(
        "💭 其他想说的（可选）",
        placeholder="任何想法都可以写下来...",
        key="review_notes"
    )
    
    if state.review_error:
        st.error(state.review_error)
    
    if st.button("📝 生成下周建议", type="primary"):
        # Parse day numbers
        best_days = [int(d.replace("第", "").replace("天", "")) for d in best_selected]
        hardest_days = [int(d.replace("第", "").replace("天", "")) for d in hardest_selected]
        
        with st.spinner("正在生成复盘..."):
            review, error = generate_weekly_review(
                weekly_plan=state.weekly_plan,
                best_days=best_days,
                hardest_days=hardest_days,
                pace=pace,
                notes=notes
            )
            
            if error:
                state.review_error = error
                update_state(state)
                st.rerun()
            else:
                state.weekly_review = review
                state.review_error = None
                update_state(state)
                st.rerun()
    
    # Show review if available
    if state.weekly_review:
        st.divider()
        st.markdown("### 📋 复盘总结")
        st.success(state.weekly_review.reflection)
        
        st.markdown("### 💡 下周建议")
        for i, suggestion in enumerate(state.weekly_review.suggestions, 1):
            st.markdown(f"{i}. {suggestion}")


def main():
    """Main app entry point."""
    render_header()
    
    state = get_state()
    current_view = get_current_view(state)
    
    # Route to appropriate view
    if current_view == "onboarding_niche":
        render_onboarding_niche()
    elif current_view == "onboarding_goal":
        render_onboarding_goal()
    elif current_view == "onboarding_style":
        render_onboarding_style()
    elif current_view == "onboarding_effort":
        render_onboarding_effort()
    elif current_view == "onboarding_constraints":
        render_onboarding_constraints()
    elif current_view == "onboarding_custom":
        render_onboarding_custom()
    elif current_view == "ready_to_generate":
        render_ready_to_generate()
    elif current_view == "weekly_plan":
        render_weekly_plan()
    elif current_view == "view_day":
        render_view_day()
    elif current_view == "rewrite_day":
        render_rewrite_day()


if __name__ == "__main__":
    main()

