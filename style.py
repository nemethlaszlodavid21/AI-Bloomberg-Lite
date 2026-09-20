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


        /* ===== TOP NAVIGATION / TABS ===== */

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            padding: 6px;
            margin-bottom: 18px;
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
        }

        .stTabs [data-baseweb="tab"] {
            height: 44px;
            padding: 0 18px;
            color: #64748b;
            background: transparent;
            border: 1px solid transparent;
            border-radius: 9px;
            font-weight: 600;
            transition:
                background-color 0.16s ease,
                color 0.16s ease,
                border-color 0.16s ease,
                box-shadow 0.16s ease;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #1e3a5f;
            background: #f8fafc;
            border-color: #e2e8f0;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            color: #0f172a;
            background: #f1f5f9;
            border-color: #cbd5e1;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
        }

        .stTabs [data-baseweb="tab-highlight"] {
            display: none;
        }

        .stTabs [data-baseweb="tab-border"] {
            display: none;
        }

        @media (max-width: 900px) {
            .stTabs [data-baseweb="tab-list"] {
                overflow-x: auto;
                justify-content: flex-start;
            }

            .stTabs [data-baseweb="tab"] {
                flex: 0 0 auto;
                padding: 0 14px;
            }
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