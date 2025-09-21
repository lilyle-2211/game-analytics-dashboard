"""Contact Me tab for the dashboard."""

import streamlit as st


def render_contact_tab():
    """Render contact information tab."""

    # Elegant, clean custom CSS
    st.markdown(
        """
        <style>
        .contact-main {
            background: #fff;
            border-radius: 18px;
            box-shadow: 0 4px 24px 0 rgba(79,139,249,0.07);
            padding: 2.5rem 2.5rem 2rem 2.5rem;
            margin-bottom: 2rem;
        }
        .contact-header {
            font-size: 2.7rem;
            font-weight: 800;
            color: #2d3a4a;
            margin-bottom: 0.2rem;
            letter-spacing: -1px;
        }
        .contact-role {
            font-size: 1.2rem;
            color: #4F8BF9;
            font-weight: 600;
            margin-bottom: 1.2rem;
        }
        .summary-box {
            background: linear-gradient(120deg, #e0e7ff 0%, #f7faff 100%);
            border-radius: 16px;
            padding: 2rem 2.2rem 1.7rem 2.2rem;
            margin-bottom: 1.7rem;
            border-left: 6px solid #4F8BF9;
            font-size: 1.13rem;
            color: #2d3a4a;
            box-shadow: 0 4px 18px 0 rgba(79,139,249,0.09);
            transition: box-shadow 0.2s;
        }
        .summary-box:hover {
            box-shadow: 0 8px 32px 0 rgba(79,139,249,0.16);
        }
        .contact-info {
            background: #f9fafb;
            border-radius: 10px;
            padding: 1.1rem 1.5rem;
            border: 1px solid #e0e6f0;
            font-size: 1.08rem;
            color: #2d3a4a;
        }
        .contact-label {
            color: #4F8BF9;
            font-weight: 600;
        }
        .contact-footer {
            margin-top: 2.5rem;
            font-size: 1.1rem;
            color: #6b7685;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="contact-main">', unsafe_allow_html=True)
    st.markdown('<div class="contact-header">Lily Le</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="contact-role">Data Analytics | Machine Learning | GenAI </div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="summary-box">'
        "<b>Professional Summary</b><br>"
        "<p>With over a decade of experience working with data, I blend a love for numbers with a creative approach to problem-solving.</p>"
        "<p>My background in mathematics and software development has fueled my passion for building smart, reliable, and impactful data solutions.</p>"
        "<p>Whether it's designing data strategies, ensuring data quality, or diving into analytics, machine learning, and GenAI, I thrive on turning ideas into production-ready systems.</p>"
        "<p>I believe in the power of data to tell stories and drive innovation—and I enjoy every step of the journey!</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="contact-info" style="margin-top:2.2rem;">'
        '<span class="contact-label">Email:</span> lelisa.dk@gmail.com<br>'
        '<span class="contact-label">Phone:</span> +44 7548 107427<br>'
        '<span class="contact-label">Location:</span> London, UK<br>'
        '<span class="contact-label">LinkedIn:</span> <a href="https://www.linkedin.com/in/lily-le-a19705225/" target="_blank">lily-le</a><br>'
        '<span class="contact-label">GitHub:</span> <a href="https://github.com/lilyle-2211" target="_blank">lilyle-2211</a>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="contact-footer">Thank you for visiting my page! I look forward to connecting with you.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
