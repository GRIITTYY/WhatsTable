import streamlit as st
import pandas as pd
from io import BytesIO
from streamlit_option_menu import option_menu
from whatstable import extract_data_from_txt_file_in_archive, parse_chat_to_dataframe

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="WhatsTable",
    page_icon="🪟",
    layout="centered"
)

# --- GLOBAL STYLES ---
st.markdown("""
<style>
    .title-container { text-align: center;}
    .title { font-family: 'Arial', sans-serif; font-weight: bold; color: #2E8B57; text-shadow: 2px 2px 4px #cccccc; }
    .subtitle { font-family: 'Arial', sans-serif; color: #464646; font-size: 1.1em; }
    .stDownloadButton > button { background-color: #2E8B57; color: white; font-weight: bold; border-radius: 5px; border: none; padding: 10px 20px; }
    .stDownloadButton > button:hover { background-color: #3CB371; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    selected_page = option_menu(
        "Menu", 
        ["Home", "About"], 
        icons=["house-door-fill", "info-circle-fill"], 
        menu_icon="list-ul",
        styles={"nav-link-selected": {"background-color": "#2E8B57"}}
    )
    st.sidebar.info("Welcome to WhatsTable!")
    st.image("WhatsTable.png", use_container_width=True)

def rainbow_divider():
    st.markdown("""
                <div style="height: 2px; background: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet); border-radius: 5px; margin-top: 0.5rem;"></div>
                    """, unsafe_allow_html=True)

# HOME PAGE
if selected_page == "Home":
    st.markdown("""
        <div class="title-container">
            <h1 class="title" style="font-size: 3em">WhatsTable</h1>
            <p class="subtitle">Upload your WhatsApp data and watch it transform into a clean structured table ready for analysis.</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div style="background-color: #8A2BE2; border-radius: 5px;">
            <marquee behavior="scroll" direction="left" style="color: white; font-size: 1.8em; font-weight: bold;">
                Convert any WhatsApp chat to a table • Download as CSV • Enjoy
            </marquee>
        </div>
        """, unsafe_allow_html=True)
    st.write("")
        
    # File uploader
    uploaded_file = st.file_uploader("Upload your WhatsApp chat .zip file", type=["zip"])

    if uploaded_file is not None:
        with st.container():
            zip_path = BytesIO(uploaded_file.getvalue())
            with st.spinner("Analyzing your chat... 🕵️‍♂️"):
                chat_lines = extract_data_from_txt_file_in_archive(zip_path)
                if chat_lines:
                    df = parse_chat_to_dataframe(chat_lines)
                    if not df.empty:
                        st.success("✅ Use the button below to download your WhatsTable.")
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download Your Chat Data as CSV",
                            data=csv,
                            file_name=f'{uploaded_file.name[:-4]}.csv',
                            mime='text/csv',
                        )
                        rainbow_divider()
                        st.dataframe(df)
                        st.balloons()
                    else:
                        st.error("Could not parse any valid messages from the chat file.")
                else:
                    st.error("Failed to extract a .txt file from the uploaded .zip archive.")
        st.markdown('</div>', unsafe_allow_html=True)

# ABOUT PAGE
elif selected_page == "About":
    with st.container():
        st.markdown('<h2 class="title" style="font-size: 2em; text-align:left;">About WhatsTable</h2>', unsafe_allow_html=True)
        st.markdown("""
        <p class="subtitle" style="text-align:left;">
        WhatsTable is a simple tool to make your WhatsApp chat data accessible. 
        It transforms the standard .zip file exported from WhatsApp into a structured table (DataFrame) 
        that you can easily view and download as a CSV file.
        </p>
        """, unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<h3 style="color: #2E8B57;">How It Works</h3>', unsafe_allow_html=True)
        st.markdown("""
        1.  **Upload:** Provide the `.zip` file directly exported from WhatsApp.
        2.  **Extract:** We find and reads the `.txt` file from the archive.
        3.  **Parse:** We intelligently process each chat message with it's respective `Timestamp` and `Sender`.
        4.  **Display:** The cleaned data is presented in a `table` and made available for download.
        """)
    st.markdown('</div>', unsafe_allow_html=True)