"""AI assistant tab for analytics questions."""
import streamlit as st
from dashboard.utils.ai_explainer import DashboardExplainer


def render_assistant_tab():
    """Render the AI assistant tab."""
    st.header("Data Analytics Assistant")
    st.write("Ask questions about your game metrics, data analysis, or get insights about player behavior!")
    
    # Initialize explainer
    explainer = DashboardExplainer()
    
    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hi! I'm your data analytics assistant. I can help you understand your game metrics like retention, revenue, acquisition, and engagement. What would you like to know?"}
        ]
    
    # Display chat messages
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about your data metrics..."):
        # Add user message to chat history
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Prepare context data from the current session
        context_data = "Dashboard showing player acquisition, weekly patterns, demographics distribution"
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your question..."):
                response = _generate_response(prompt, context_data, explainer)
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
    
    # Quick action buttons for common questions
    st.markdown("**Quick Questions:**")
    col1, col2, col3, col4 = st.columns(4)
    
    _render_quick_action_buttons(col1, col2, col3, col4)
    
    # Clear chat option
    if st.button("Clear Chat", type="secondary"):
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hi! I'm your data analytics assistant. I can help you understand your game metrics like retention, revenue, acquisition, and engagement. What would you like to know?"}
        ]
        st.rerun()


def _generate_response(prompt, context_data, explainer):
    """Generate response based on AI or fallback logic."""
    if explainer.ai_enabled:
        try:
            ai_prompt = f"""
            You are a game analytics expert assistant. Answer this question about game data analytics:
            
            User Question: {prompt}
            Context: {context_data}
            
            Provide helpful, actionable advice focused on game metrics, player behavior, and business insights.
            Keep your response concise and practical.
            """
            response = explainer.model.generate_content(ai_prompt).text
            return response
        except Exception:
            return "I'm having trouble accessing AI insights right now. However, I can still help with general analytics questions. Could you be more specific about what metrics or data you'd like to analyze?"
    else:
        return _get_fallback_response(prompt)


def _get_fallback_response(prompt):
    """Provide fallback responses for common questions when AI is not available."""
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ['retention', 'keep', 'return']):
        return "To improve retention, focus on: 1) Onboarding optimization - ensure new players understand core mechanics quickly, 2) Daily engagement features like rewards/streaks, 3) Social features to build community, 4) Regular content updates, and 5) Analyzing churn points to fix friction areas."
    elif any(word in prompt_lower for word in ['revenue', 'monetization', 'money', 'purchase']):
        return "For revenue optimization: 1) Analyze your conversion funnel to find drop-off points, 2) A/B test different price points and offers, 3) Implement time-limited offers, 4) Focus on high-LTV user segments, 5) Optimize your in-app purchase flow for minimal friction."
    elif any(word in prompt_lower for word in ['acquisition', 'users', 'install', 'growth']):
        return "User acquisition tips: 1) Analyze your best-performing channels and double down, 2) Optimize your app store presence (ASO), 3) Track cohort performance by source, 4) Test different creative assets, 5) Focus on channels that bring high-LTV users, not just volume."
    elif any(word in prompt_lower for word in ['metrics', 'kpi', 'track', 'measure']):
        return "Key game metrics to track: 1) DAU/MAU for engagement, 2) Retention rates (D1, D7, D30), 3) LTV and ARPU, 4) Conversion rates, 5) Session length and frequency, 6) Churn rate and reasons, 7) Viral coefficient, 8) Cost per acquisition (CPA)."
    else:
        return "I'd be happy to help with your game analytics question! I can provide insights on player retention, revenue optimization, user acquisition, key metrics to track, A/B testing, and more. Could you be more specific about what aspect of your game data you'd like to analyze?"


def _render_quick_action_buttons(col1, col2, col3, col4):
    """Render quick action buttons for common questions."""
    with col1:
        if st.button("How to improve retention?"):
            _add_quick_question("How can I improve player retention in my game?", 
                               "To improve retention, focus on: 1) Onboarding optimization - ensure new players understand core mechanics quickly, 2) Daily engagement features like rewards/streaks, 3) Social features to build community, 4) Regular content updates, and 5) Analyzing churn points to fix friction areas.")
    
    with col2:
        if st.button("Revenue optimization?"):
            _add_quick_question("What are the best strategies to optimize game revenue?",
                               "For revenue optimization: 1) Analyze your conversion funnel to find drop-off points, 2) A/B test different price points and offers, 3) Implement time-limited offers, 4) Focus on high-LTV user segments, 5) Optimize your in-app purchase flow for minimal friction.")
    
    with col3:
        if st.button("Key metrics to track?"):
            _add_quick_question("What are the most important metrics I should track for my game?",
                               "Key game metrics to track: 1) DAU/MAU for engagement, 2) Retention rates (D1, D7, D30), 3) LTV and ARPU, 4) Conversion rates, 5) Session length and frequency, 6) Churn rate and reasons, 7) Viral coefficient, 8) Cost per acquisition (CPA).")
    
    with col4:
        if st.button("User acquisition tips?"):
            _add_quick_question("How can I improve my user acquisition strategy?",
                               "User acquisition tips: 1) Analyze your best-performing channels and double down, 2) Optimize your app store presence (ASO), 3) Track cohort performance by source, 4) Test different creative assets, 5) Focus on channels that bring high-LTV users, not just volume.")


def _add_quick_question(question, response):
    """Add a quick question and response to chat history."""
    st.session_state.chat_messages.append({"role": "user", "content": question})
    st.session_state.chat_messages.append({"role": "assistant", "content": response})
    st.rerun()