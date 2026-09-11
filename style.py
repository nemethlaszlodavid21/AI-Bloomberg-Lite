import streamlit as st


def alkalmaz_style():

    st.markdown(
        """
        <style>

        /* ===== APP BACKGROUND ===== */

        .stApp {
            background-color: #f4f6f8;
            color: #17202a;
        }


        /* ===== MAIN CONTAINER ===== */

        .block-container {
            max-width: 1480px;
            padding-top: 1.8rem;
            padding-bottom: 3rem;
        }


        /* ===== HEADINGS ===== */

        h1 {
            color: #111827 !important;
            font-size: 2.1rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.03em;
        }

        h2 {
            color: #1f2937 !important;
            font-size: 1.45rem !important;
            font-weight: 650 !important;
        }

        h3 {
            color: #374151 !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
        }


        /* ===== CAPTION ===== */

        [data-testid="stCaptionContainer"] {
            color: #6b7280;
        }


        /* ===== METRIC CARDS ===== */

        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            padding: 18px 20px;
            border-radius: 12px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
        }

        [data-testid="stMetricLabel"] {
            color: #6b7280;
            font-size: 0.82rem;
            font-weight: 500;
        }

        [data-testid="stMetricValue"] {
            color: #111827;
            font-size: 1.5rem;
            font-weight: 700;
        }


        /* ===== TABS ===== */

        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
            border-bottom: 1px solid #d1d5db;
        }

        .stTabs [data-baseweb="tab"] {
            height: 44px;
            padding-left: 18px;
            padding-right: 18px;
            color: #4b5563;
            background: transparent;
            border-radius: 8px 8px 0 0;
        }

        .stTabs [aria-selected="true"] {
            color: #111827;
            background: #ffffff;
            border-bottom: 2px solid #2563eb;
        }


        /* ===== BUTTONS ===== */

        .stButton > button {
            border-radius: 8px;
            border: 1px solid #d1d5db;
            background-color: #ffffff;
            color: #1f2937;
            font-weight: 600;
        }

        .stButton > button:hover {
            border-color: #2563eb;
            color: #2563eb;
        }


        /* ===== DATAFRAMES ===== */

        [data-testid="stDataFrame"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
        }


        /* ===== EXPANDERS ===== */

        [data-testid="stExpander"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
        }


        /* ===== DIVIDERS ===== */

        hr {
            border-color: #e5e7eb !important;
        }


        /* ===== INPUTS ===== */

        input {
            background-color: #ffffff !important;
            color: #111827 !important;
        }


        /* ===== REMOVE STREAMLIT DECORATION ===== */

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        </style>
        """,
        unsafe_allow_html=True
    )