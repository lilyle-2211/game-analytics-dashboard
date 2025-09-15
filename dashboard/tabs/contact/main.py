"""Contact Me tab for the dashboard."""

import streamlit as st

def render_contact_tab():
    """Render contact information tab."""
    st.markdown("# Contact Me")
    
    # Profile container with information
    with st.container():
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image("https://avatars.githubusercontent.com/u/your-github-id?v=4", 
                    caption="Lily Le", width=200)
        
        with col2:
            st.markdown("## Lily Le")
            st.markdown("### Data Analytics | Machine Learning")
            st.markdown("""
            Welcome to my contact page! I'm passionate about turning data into actionable insights, building 
            powerful analytics, AI/ML tools. With expertise in data governance, data warehouse, analytics, machine learning, and genAI solutions, I help companies make data-driven decisions.
            """)
    
    # Contact information
    st.markdown("## Get in Touch")
    
    contact_col1, contact_col2 = st.columns(2)
    
    with contact_col1:
        st.markdown("### Contact Information")
        st.markdown("**Email:** lelisa.dk@gmail.com")
        st.markdown("**Phone:** +44 7548 107427")
        st.markdown("**Location:** London, UK")
    
    with contact_col2:
        st.markdown("### Professional Profiles")
        st.markdown("[LinkedIn](https://linkedin.com/in/your-profile)")
        st.markdown("[GitHub](https://github.com/your-username)")
        st.markdown("[Personal Website](https://your-website.com)")
    
    # Skills section
    st.markdown("## Skills")
    
    skill_col1, skill_col2, skill_col3, skill_col4 = st.columns(4)
    
    with skill_col1:
        st.markdown("### Data Science")
        st.markdown("- Python / Pandas / NumPy")
        st.markdown("- Machine Learning")
        st.markdown("- Statistical Analysis")
        st.markdown("- A/B Testing")
    
    with skill_col2:
        st.markdown("### Data Engineering")
        st.markdown("- SQL / BigQuery")
        st.markdown("- ETL Pipeline Design")
        st.markdown("- Data Modeling")
        st.markdown("- Cloud Infrastructure")
    
    with skill_col3:
        st.markdown("### Visualization")
        st.markdown("- Streamlit")
        st.markdown("- Plotly / Matplotlib")
        st.markdown("- Tableau")
        st.markdown("- Dashboard Design")

    with skill_col4:
        st.markdown("### Machine Learning")
        st.markdown("- Distributed Systems")
        st.markdown("- Terraform")
        st.markdown("- MLFlow")
        st.markdown("- System Design")
    
    
    # Footer
    st.markdown("---")
    st.markdown("Thank you for visiting my profile! I look forward to connecting with you.")
