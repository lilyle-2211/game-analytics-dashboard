"""Contact Me tab for the dashboard."""

import streamlit as st


def render_contact_tab():
    """Render contact information tab."""

    # Profile container with information
    with st.container():
        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("## Lily Le")
            st.markdown(
                "Thank you for visiting my page! I look forward to connecting with you :-)"
            )

    contact_col1, contact_col2 = st.columns(2)

    with contact_col1:
        st.markdown("### Contact Information")
        st.markdown("**Email:** lelisa.dk@gmail.com")
        st.markdown("**Phone:** +44 7548 107427")
        st.markdown("**Location:** London, UK")
