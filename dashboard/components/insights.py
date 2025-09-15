"""Common UI components for insights and analysis."""
import streamlit as st


def render_ai_insights(explanation, explainer=None, error_message="⚠️ Configure OpenAI API key in .streamlit/secrets.toml to enable AI insights"):
    """Render AI insights section with proper error handling."""
    if explanation:
        with st.expander("🤖 AI Analysis", expanded=False):
            st.success(explanation)
    else:
        with st.expander("🤖 AI Analysis", expanded=False):
            if explainer and hasattr(explainer, 'rate_limit_exceeded') and explainer.rate_limit_exceeded:
                st.warning("⚠️ OpenAI API rate limit exceeded. Please check your usage or upgrade your plan.")
            else:
                st.error(error_message)


def render_manual_insights(placeholder_text, height=120, key_suffix=""):
    """Render manual insights text area."""
    return st.text_area(
        "",  # Removed the "Your analysis notes:" label
        placeholder=placeholder_text,
        height=height,
        key=f"manual_{key_suffix}"
    )