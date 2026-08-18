import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import csv
from datetime import datetime, date

st.set_page_config(
    page_title="Stock movement Monitoring | Sales & Interlocation vs Stock Movement",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg-base: #F8FAFC;
        --surface-glass: #FFFFFF;
        --surface-hover: #F1F5F9;
        --border-glass: #E2E8F0;
        --primary: #3B82F6;
        --secondary: #8B5CF6;
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
        --text-primary: #0F172A;
        --text-secondary: #64748B;
    }

    html, body, [class*="css"]:not([data-testid="stIconMaterial"]) {
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }

    /* Icon glyphs (expander arrows, checkbox ticks, etc.) render via a
       ligature font (Material Symbols). We must NOT declare our own guess
       of that font-family (it may not exactly match what Streamlit loaded,
       breaking the ligature and showing literal text like
       "keyboard_arrow_right"). Simplest safe fix: exclude icon elements
       from our Inter override above (via :not()) and leave their
       font-family completely untouched - only override color. */
    .stApp [data-testid="stIconMaterial"] { color: var(--text-primary) !important; }

    /* Force readable text color everywhere - Streamlit's default theme
       leaves several inner components (uploader instructions, widget
       labels, markdown paragraphs) with inconsistent text color. */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp div,
    .stApp li, .stApp small, .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stFileUploaderDropzoneInstructions"],
    .stApp [data-testid="stFileUploaderDropzoneInstructions"] span,
    .stApp [data-testid="stFileUploaderDropzoneInstructions"] small,
    .stApp [data-testid="stFileUploaderDropzoneInstructions"] div {
        color: var(--text-primary) !important;
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }
    /* Widget labels (Filter Status, selectbox mapping, dst) - dibuat merah
       supaya jelas terbaca & menonjol. */
    .stApp [data-testid="stWidgetLabel"] p,
    .stApp [data-testid="stWidgetLabel"] label {
        color: var(--danger) !important;
        font-weight: 700 !important;
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }
    .stApp [data-testid="stFileUploaderDropzoneInstructions"] small {
        color: var(--text-secondary) !important;
    }
    .stApp [data-testid="stFileUploaderFile"] * {
        color: var(--text-primary) !important;
        opacity: 1 !important;
    }
    .stApp button[data-testid="stBaseButton-secondary"] { color: var(--text-primary) !important; }

    /* ---------------- APP BACKGROUND ---------------- */
    .stApp {
        background: var(--bg-base);
        color: var(--text-primary);
    }
    .block-container { padding-top: 1.5rem; max-width: 1400px; }
    h1, h2, h3, h4, h5, p, span, label, div { color: var(--text-primary); }
    .stApp p, .stApp span, .stApp label, .stApp li { font-size: 14px; }
    .stCaption, [data-testid="stCaptionContainer"] { color: var(--text-secondary) !important; font-size: 12px !important; }

    /* Sidebar title ("Panel Control") - dikecilkan supaya proporsional */
    section[data-testid="stSidebar"] h1 { font-size: 19px !important; }
    section[data-testid="stSidebar"] h2 { font-size: 16px !important; }
    section[data-testid="stSidebar"] h3 { font-size: 14px !important; }
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label { font-size: 13px !important; }

    /* ---------------- HERO HEADER ---------------- */
    .hero-header {
        position: relative;
        text-align: center;
        padding: 34px 24px 30px 24px;
        margin-bottom: 24px;
        border-radius: 14px;
        background: var(--surface-glass);
        border: 1px solid var(--border-glass);
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        overflow: hidden;
    }
    .hero-header .hero-icon { font-size: clamp(22px, 2.2vw, 30px); position: relative; z-index: 1; }
    .hero-header h1 {
        position: relative; z-index: 1;
        font-size: clamp(17px, 1.6vw, 21px); font-weight: 800; margin: 6px 0 6px 0;
        color: var(--text-primary);
        letter-spacing: -0.3px;
        line-height: 1.25;
    }
    .hero-header p.hero-sub {
        position: relative; z-index: 1;
        font-size: clamp(11px, 0.9vw, 12.5px); color: var(--text-secondary); font-weight: 500;
        margin-bottom: 12px;
    }
    .hero-header p.hero-author {
        position: relative; z-index: 1;
        font-size: clamp(10px, 0.8vw, 11px); color: var(--text-secondary); font-weight: 500;
        opacity: 0.85; margin: -2px 0 14px 0; letter-spacing: 0.3px;
    }
    .hero-badge {
        position: relative; z-index: 1;
        display: inline-flex; align-items: center; gap: 6px;
        padding: 5px 14px; border-radius: 999px;
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        color: #059669; font-size: 11px; font-weight: 700; letter-spacing: 0.8px;
    }
    .hero-badge .dot {
        width: 6px; height: 6px; border-radius: 50%; background: #10B981;
        animation: pulse-dot 1.6s infinite;
    }
    @keyframes pulse-dot { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

    /* ---------------- CARD ---------------- */
    .glass-card {
        background: var(--surface-glass);
        border: 1px solid var(--border-glass);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        transition: box-shadow 0.2s ease;
    }
    .glass-card h4 { margin-top: 0; font-weight: 700; font-size: 14px; }
    .glass-card-title {
        font-size: 13.5px; font-weight: 700; color: var(--text-primary);
        margin-bottom: 4px; display: flex; align-items: center; gap: 8px;
    }
    .glass-card-sub { font-size: 12px; color: var(--text-secondary); margin-bottom: 12px; }

    /* Audit / summary box */
    .audit-box {
        background: #EFF6FF;
        border: 1px solid var(--border-glass);
        border-left: 4px solid var(--primary);
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .audit-box h4 { margin: 0 0 10px 0; font-weight: 700; color: var(--text-primary); }
    .audit-box ul { margin: 0; padding-left: 18px; }
    .audit-box li { margin-bottom: 6px; font-size: 14px; color: var(--text-secondary); }
    .audit-box li b { color: var(--text-primary); }

    /* ---------------- KPI CARD ---------------- */
    .kpi-card {
        background: var(--surface-glass);
        border: 1px solid var(--border-glass);
        border-radius: 12px;
        padding: 18px 20px;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        background: var(--surface-hover);
        box-shadow: 0 4px 12px rgba(0,0,0,0.10);
    }
    .kpi-label {
        font-size: 11px; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.6px; color: var(--text-secondary); margin-bottom: 6px;
    }
    .kpi-value { font-size: 24px; font-weight: 800; line-height: 1.1; }

    /* ---------------- FILE UPLOADER ---------------- */
    [data-testid="stFileUploaderDropzone"] {
        background: #FFFFFF !important;
        border: 1.5px dashed #93C5FD !important;
        border-radius: 10px !important;
        transition: border-color 0.2s ease;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        background: #EFF6FF !important;
        border-color: #3B82F6 !important;
    }
    [data-testid="stFileUploaderDropzone"] * { color: var(--text-secondary) !important; }

    /* The native "Browse files" button has hidden/duplicate inner nodes
       (icon + accessibility label) that render on top of each other with
       different colors once touched - causing ghosted double-text. Fix:
       hide the button's native content and paint one clean centered label
       via ::after. IMPORTANT: this must ONLY apply while no file has been
       uploaded yet ( :not(:has(...)) ) - once a file exists, this same
       dropzone area also contains a small "replace/remove" icon button,
       and blindly relabeling every button "Browse files" duplicates the
       text onto that control too. */
    [data-testid="stFileUploader"]:not(:has([data-testid="stFileUploaderFile"]))
        [data-testid="stFileUploaderDropzone"] button {
        position: relative !important;
        background: #F1F5F9 !important;
        border: 1px solid rgba(15,23,42,0.15) !important;
        border-radius: 8px !important;
        padding: 8px 26px !important;
        min-width: 120px !important;
        min-height: 34px !important;
    }
    [data-testid="stFileUploader"]:not(:has([data-testid="stFileUploaderFile"]))
        [data-testid="stFileUploaderDropzone"] button * {
        color: transparent !important;
        opacity: 0 !important;
        fill: transparent !important;
    }
    [data-testid="stFileUploader"]:not(:has([data-testid="stFileUploaderFile"]))
        [data-testid="stFileUploaderDropzone"] button::after {
        content: "Browse files";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: #0F172A;
        font-weight: 600;
        font-size: 14px;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        white-space: nowrap;
    }
    [data-testid="stFileUploader"]:not(:has([data-testid="stFileUploaderFile"]))
        [data-testid="stFileUploaderDropzone"] button:hover {
        background: #E2E8F0 !important;
    }

    /* Once a file HAS been uploaded, only fix colors on the remaining
       small icon button (replace/remove) - no content replacement, no
       opacity hacks, so nothing overlaps the file-info row. */
    [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
        [data-testid="stFileUploaderDropzone"] button {
        background: #F1F5F9 !important;
        border: 1px solid rgba(15,23,42,0.15) !important;
        border-radius: 8px !important;
    }
    [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
        [data-testid="stFileUploaderDropzone"] button * {
        color: #0F172A !important;
        opacity: 1 !important;
    }


    /* ---------------- BUTTONS ---------------- */
    .stButton > button, .stDownloadButton > button {
        background: #3B82F6;
        color: #fff !important;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        font-size: 13.5px;
        padding: 8px 20px;
        transition: background 0.2s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: #2563EB;
        color: #fff !important;
    }

    /* ---------------- SIDEBAR ---------------- */
    section[data-testid="stSidebar"] {
        background: #F1F5F9;
        border-right: 1px solid var(--border-glass);
    }
    section[data-testid="stSidebar"] * { color: var(--text-primary); }

    /* ---------------- EXPANDER (used for advanced mapping) ---------------- */
    [data-testid="stExpander"] {
        background: var(--surface-glass) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 10px;
        margin-bottom: 8px;
        overflow: hidden;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] details,
    [data-testid="stExpander"] > div {
        background: transparent !important;
        color: var(--text-primary) !important;
    }
    [data-testid="stExpander"] summary:hover {
        background: var(--surface-hover) !important;
    }
    /* The Material Symbols icon font is not rendering as glyphs in this
       deployment (shows raw ligature text like "keyboard_arrow_right" /
       "double_arrow_right" instead) - happens on the expander arrows AND
       the sidebar collapse/expand toggle, and possibly elsewhere. Since
       we can't rely on the icon font loading correctly in this
       environment, hide EVERY such icon completely rather than chase
       individual locations one at a time. */
    [data-testid="stIconMaterial"] {
        font-size: 0 !important;
        line-height: 0 !important;
        color: transparent !important;
        width: 0 !important;
        min-width: 0 !important;
        overflow: hidden !important;
    }
    /* The sidebar collapse/expand control becomes an empty hit-target once
       its icon is hidden - give it a simple CSS chevron instead so it's
       still visually discoverable and clickable. */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"] button,
    button[kind="header"] {
        position: relative;
    }
    [data-testid="stSidebarCollapsedControl"]::after {
        content: "»";
        font-size: 20px !important;
        color: var(--text-primary);
        line-height: 1;
    }

    /* ---------------- INPUTS ---------------- */
    .stSelectbox [data-baseweb="select"], .stMultiSelect [data-baseweb="select"],
    .stNumberInput input, .stDateInput input, .stTextInput input {
        background: #FFFFFF !important;
        border-radius: 8px !important;
        border: 1px solid var(--border-glass) !important;
        color: #0F172A !important;
    }
    .stSelectbox [data-baseweb="select"] *,
    .stMultiSelect [data-baseweb="select"] *,
    .stNumberInput input, .stDateInput input, .stTextInput input {
        color: #0F172A !important;
    }
    .stMultiSelect [data-baseweb="select"] input::placeholder,
    .stSelectbox [data-baseweb="select"] input::placeholder {
        color: #64748B !important;
    }
    /* Selected chips/tags inside a multiselect. */
    [data-baseweb="tag"] {
        background: #3B82F6 !important;
        border-radius: 6px !important;
        border: none !important;
    }
    [data-baseweb="tag"] *,
    [data-baseweb="tag"] span,
    [data-baseweb="tag"] svg {
        color: #fff !important;
        fill: #fff !important;
    }

    /* ---------------- DROPDOWN POPUP (selectbox / multiselect options) ----
       Streamlit renders this list in a portal appended outside the .stApp
       tree, so none of the .stApp-scoped rules above reach it - it was
       silently falling back to a near-invisible default. Style it
       explicitly, globally, to match the basic light theme. */
    div[data-baseweb="popover"] [data-baseweb="menu"],
    div[data-baseweb="popover"] ul[role="listbox"],
    div[data-baseweb="popover"] div[role="listbox"] {
        background: #FFFFFF !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.12) !important;
    }
    div[data-baseweb="popover"] li,
    div[data-baseweb="popover"] li *,
    div[data-baseweb="popover"] [role="option"],
    div[data-baseweb="popover"] [role="option"] * {
        color: #0F172A !important;
        background: transparent !important;
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="popover"] [role="option"]:hover,
    div[data-baseweb="popover"] [aria-selected="true"] {
        background: #EFF6FF !important;
    }

    /* ---------------- METRICS ---------------- */
    [data-testid="stMetric"] {
        background: var(--surface-glass);
        border: 1px solid var(--border-glass);
        border-radius: 12px;
        padding: 14px 16px;
        transition: box-shadow 0.2s ease;
    }
    [data-testid="stMetric"]:hover { background: var(--surface-hover); }
    [data-testid="stMetricLabel"] { color: var(--text-secondary) !important; }
    [data-testid="stMetricValue"] { color: var(--text-primary) !important; }

    /* ---------------- TABS ---------------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: #F1F5F9;
        padding: 6px;
        border-radius: 999px;
        border: 1px solid var(--border-glass);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 999px !important;
        padding: 8px 20px !important;
        color: var(--text-secondary) !important;
        font-weight: 600;
        transition: background 0.2s ease;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab"]:hover { background: #E2E8F0 !important; }
    .stTabs [aria-selected="true"] {
        background: #3B82F6 !important;
        color: #fff !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }

    /* ---------------- DATAFRAME / TABLE ---------------- */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid var(--border-glass);
    }
    [data-testid="stDataFrame"] table thead tr th {
        background: #EFF6FF !important;
        color: #1E3A8A !important;
    }
    [data-testid="stDataFrame"] table tbody tr:nth-child(even) { background: #F8FAFC; }
    [data-testid="stDataFrame"] table tbody tr:hover { background: #EFF6FF !important; }

    /* ---------------- FOOTER ---------------- */
    .app-footer {
        text-align: center;
        padding: 22px 0 10px 0;
        color: var(--text-secondary);
        font-size: 12.5px;
        border-top: 1px solid var(--border-glass);
        margin-top: 30px;
    }

    /* ---------------- RESPONSIVE ---------------- */
    /* hero-header h1/sub/author already use clamp() for fluid sizing, so
       no fixed-size override needed here anymore. */
    @media (max-width: 1366px) {
        .kpi-value { font-size: 20px; }
    }
    @media (max-width: 768px) {
        .hero-header { padding: 24px 14px; }
        .glass-card { padding: 14px; }
        .kpi-value { font-size: 18px; }
    }

    /* ---------------- DROPDOWN POPUP - HARD OVERRIDE (kept last so it
       wins any cascade tie against earlier broad ".stApp div { color }"
       rules, in case the popup renders inside .stApp instead of as a
       body-level portal). Very wide selector net since the exact markup
       varies by Streamlit/BaseWeb version. ---------------- */
    ul[role="listbox"], div[role="listbox"],
    [data-baseweb="menu"], [data-baseweb="popover"] [data-baseweb="menu"],
    [data-baseweb="popover"] ul, [data-baseweb="popover"] li,
    li[role="option"], div[role="option"], [data-baseweb="menu-item"],
    [data-baseweb^="select-"], [data-baseweb*="option"] {
        background-color: #FFFFFF !important;
    }
    ul[role="listbox"] *, div[role="listbox"] *,
    [data-baseweb="menu"] *, [data-baseweb="popover"] [data-baseweb="menu"] *,
    li[role="option"], li[role="option"] *,
    div[role="option"], div[role="option"] *,
    [data-baseweb="menu-item"], [data-baseweb="menu-item"] *,
    [data-baseweb*="option"], [data-baseweb*="option"] * {
        color: #0F172A !important;
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }
    li[role="option"]:hover, div[role="option"]:hover,
    [data-baseweb="menu-item"]:hover, [aria-selected="true"] {
        background-color: #EFF6FF !important;
    }
</style>
""", unsafe_allow_html=True)

def auto_detect_csv(file_bytes):
    """Detects CSV delimiter automatically and reads using pandas with string dtypes."""
    try:
        sample = file_bytes[:1024].decode('utf-8', errors='ignore')
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample, delimiters=[',', ';', '|', '\t'])
        sep = dialect.delimiter
    except Exception:
        sep = ','
    
    file_bytes.seek(0)
    df = pd.read_csv(file_bytes, sep=sep, dtype=str, keep_default_na=False)
    # Normalize header whitespace (" Quantity " vs "Quantity") - important
    # once multiple periodic files get concatenated, otherwise the same
    # logical column splits into two due to a stray space in one file.
    df.columns = [str(c).strip() for c in df.columns]
    return df


# ======================================================================
# GENERIC MULTI-SOURCE RECONCILIATION ENGINE
# ----------------------------------------------------------------------
# Program ini sekarang mencocokkan 3 jenis dokumen sumber terhadap 1 file
# Stock Movement:
#   1. SALES            (Qty sold pada file sales-report)
#   2. TRANSFER IN       (barang DITERIMA dari lokasi lain - interlocation)
#   3. TRANSFER OUT       (barang DIKIRIM ke lokasi lain - interlocation)
# Untuk masing-masing, kita cek apakah qty pada dokumen sumber sudah
# "tercapture" di Stock Movement (dicocokkan lewat kolom Reason/Transaction
# Type), lalu digabung jadi satu laporan.
# ======================================================================

NONE_LABEL = "-- Kosongkan / Tidak Ada --"

# Semua sumber (Sales, Transfer In, Transfer Out) dinormalisasi ke skema
# internal yang SAMA supaya bisa dipakai 1 fungsi rekonsiliasi generik:
#   Date, Store, Product Code, Product Description, Qty, Document Number
GENERIC_REQUIRED_FIELDS = ['Date', 'Store', 'Product Code', 'Product Description', 'Qty']
GENERIC_OPTIONAL_FIELDS = ['Document Number']

SALES_FIELD_CANDIDATES = {
    'Date':                ['sales date', 'transaction date', 'tanggal', 'date'],
    'Store':               ['branch code', 'store code', 'toko', 'store', 'branch'],
    'Product Code':        ['plu number', 'product code', 'sku', 'item code', 'plu', 'kode barang'],
    'Product Description': ['plu description', 'product description', 'product name', 'nama barang', 'description', 'item name'],
    'Qty':                 ['qty sold', 'quantity', 'qty', 'jumlah'],
}
SALES_OPTIONAL = {
    'Document Number': ['receipt number', 'receipt no', 'invoice number', 'no struk', 'transaction number', 'pos number'],
    'Net Sales':        ['net sales', 'net sale', 'nilai penjualan', 'sales value', 'amount'],
}

TRANSFER_IN_FIELD_CANDIDATES = {
    # Transfer IN = barang DITERIMA oleh toko yang sedang kita cek -> pakai kolom "Transfer To" sebagai Store
    'Date':                ['gi date', 'transfer date', 'tanggal'],
    'Store':               ['transfer to', 'receiver location', 'receiving location'],
    'Product Code':        ['item code', 'product code', 'sku'],
    'Product Description': ['item name', 'product name', 'description'],
    'Qty':                 ['receiving qty', 'received qty', 'transfered qty', 'qty'],
}
TRANSFER_IN_OPTIONAL = {
    'Document Number': ['transfer number', 'document number', 'reference'],
}

TRANSFER_OUT_FIELD_CANDIDATES = {
    # Transfer OUT = barang DIKIRIM oleh toko yang sedang kita cek -> pakai kolom "Transfer From" sebagai Store
    'Date':                ['gi date', 'transfer date', 'tanggal'],
    'Store':               ['transfer from', 'sender location'],
    'Product Code':        ['item code', 'product code', 'sku'],
    'Product Description': ['item name', 'product name', 'description'],
    'Qty':                 ['gi quantity', 'transfered qty', 'qty'],
}
TRANSFER_OUT_OPTIONAL = {
    'Document Number': ['transfer number', 'document number', 'reference'],
}

MOV_FIELD_CANDIDATES = {
    'Movement Date':       ['movement date', 'tanggal', 'date'],
    'Store':               ['location code', 'store code', 'toko', 'branch code', 'store'],
    'Product Code':        ['product code', 'sku', 'item code', 'kode barang'],
    'Product Description': ['product', 'nama barang', 'description', 'item name'],
    'Qty':                 ['difference', 'qty', 'quantity', 'jumlah'],
}
MOV_OPTIONAL_FIELDS = {
    'Transaction Type': ['reason', 'transaction type', 'movement type', 'type', 'jenis'],
    'Document Number':  ['document number', 'doc number', 'reference', 'description', 'no dokumen'],
    'User':             ['user', 'created by', 'staff', 'petugas'],
    'UOM':              ['uom', 'unit of measure', 'satuan', 'base uom'],
}

# Weight/volume-based UOMs where the item is sold "timbang" (variable weight
# e.g. produce, meat, fish). For these items, Sales Qty (often a pcs/lines
# count) will almost never equal Movement Qty (actual KG deducted) even
# when everything is posted correctly - so we must not flag them as a hard
# OVER/PARTIAL CAPTURED finding.
WEIGHT_BASED_UOMS = {'KG', 'KGM', 'G', 'GR', 'GRAM', 'GRM', 'LB', 'LBS', 'OZ', 'L', 'LTR', 'LITER', 'ML'}

def guess_column(df, keywords, exclude=None):
    """Best-effort auto-detect a source column based on keyword matches.
    Tries an exact (whole-name) match first, then falls back to substring
    matching. `exclude` lets us skip columns already claimed by another
    field in the same mapping. Columns that are entirely blank are only
    used as a last resort (e.g. an optional 'GI Date' column that exists
    but was never filled in should NOT win over 'Transfer Date')."""
    exclude = exclude or set()
    all_cols = [c for c in df.columns if c not in exclude]
    non_blank = [c for c in all_cols if df[c].astype(str).str.strip().replace('nan', '').ne('').any()]
    for candidate_pool in (non_blank, all_cols):
        cols_lower = {c: str(c).strip().lower() for c in candidate_pool}
        for kw in keywords:
            for c, cl in cols_lower.items():
                if cl == kw:
                    return c
        for kw in keywords:
            for c, cl in cols_lower.items():
                if kw in cl:
                    return c
    return None

def build_column_mapping_ui(df, field_candidates, optional_fields, section_key, section_label, container=None):
    """Renders selectboxes so the user can confirm/override the
    auto-detected column mapping for one uploaded file. `container` lets
    the caller decide where this renders (main area expander, sidebar,
    etc.) - defaults to the sidebar for backward compatibility."""
    if container is None:
        container = st.sidebar
    mapping = {}
    used = set()
    columns = list(df.columns)
    with container.expander(f"🔧 Mapping Kolom - {section_label}", expanded=False):
        st.caption("Kolom sudah ditebak otomatis. Cek/ubah bila kurang tepat.")
        for field, keywords in field_candidates.items():
            guess = guess_column(df, keywords, exclude=used)
            options = columns
            default_idx = options.index(guess) if guess in options else 0
            chosen = st.selectbox(f"{field} *", options, index=default_idx, key=f"{section_key}_{field}")
            mapping[field] = chosen
            used.add(chosen)
        for field, keywords in optional_fields.items():
            guess = guess_column(df, keywords, exclude=used)
            options = [NONE_LABEL] + columns
            default_idx = options.index(guess) if guess in columns else 0
            chosen = st.selectbox(f"{field} (opsional)", options, index=default_idx, key=f"{section_key}_{field}")
            mapping[field] = chosen
            if chosen != NONE_LABEL:
                used.add(chosen)
    return mapping

def normalize_date_value(s):
    """Parses many date formats (ISO, M/D/YYYY, D-Mon-YYYY, etc.) into a
    canonical YYYY-MM-DD string so files with different date formats can
    still be matched correctly. Falls back to the original string if it
    cannot be parsed."""
    parsed = pd.to_datetime(s, errors='coerce')
    out = parsed.dt.strftime('%Y-%m-%d')
    return out.fillna(s.astype(str).str.strip())

def normalize_store_value(s):
    """Normalizes store/branch codes so '0104' and '104' are treated as the
    same store. Falls back to the original stripped string when it isn't
    purely numeric (e.g. store codes with letters)."""
    s = s.astype(str).str.strip()
    def _norm(v):
        v2 = v.lstrip('0')
        if v2 == '':
            v2 = '0'
        return v2 if v.replace('.', '', 1).isdigit() or v.isdigit() else v.upper()
    return s.apply(_norm)

def apply_mapping(df, mapping, date_fields=None, store_fields=None, code_fields=None):
    """Builds a new DataFrame using the internal standard column names,
    based on the user-confirmed mapping. Unmapped optional fields become
    empty strings so downstream logic degrades gracefully instead of
    raising a KeyError. Also normalizes date/store/product-code columns so
    files with different formats (e.g. '0104' vs '104', '0146249' vs
    '146249', '8/12/2026' vs '2026-08-12') can still be matched correctly."""
    date_fields = date_fields or []
    store_fields = store_fields or []
    code_fields = code_fields or []
    out = pd.DataFrame(index=df.index)
    for internal_name, source_col in mapping.items():
        if source_col and source_col != NONE_LABEL and source_col in df.columns:
            out[internal_name] = df[source_col].astype(str)
        else:
            out[internal_name] = ''
    for f in date_fields:
        if f in out.columns:
            out[f] = normalize_date_value(out[f])
    for f in (store_fields + code_fields):
        if f in out.columns:
            out[f] = normalize_store_value(out[f])
    return out

def clean_numeric(series):
    """Parses numeric strings that may contain thousand separators (','),
    surrounding whitespace, or be blank - returns 0 for anything unparsable
    instead of silently producing NaN/0 without the person knowing why."""
    cleaned = series.astype(str).str.replace(',', '', regex=False).str.strip()
    return pd.to_numeric(cleaned, errors='coerce').fillna(0)

def dedupe_movement(mov_std):
    """Flags duplicate rows in the (already standardized) movement data."""
    mov = mov_std.copy()
    mov['Qty_num'] = clean_numeric(mov['Qty']).abs()
    dup_cols = ['Movement Date', 'Store', 'Product Code', 'Qty_num']
    if 'Transaction Type' in mov.columns and (mov['Transaction Type'] != '').any():
        dup_cols.insert(3, 'Transaction Type')
    if 'Document Number' in mov.columns and (mov['Document Number'] != '').any():
        dup_cols.insert(len(dup_cols) - 1, 'Document Number')
    mov['Is_Duplicate'] = mov.duplicated(subset=dup_cols, keep='first')
    return mov

def reconcile_source(source_std, mov_dedup, source_label, type_values, has_type, date_offset_days=0, over_posted_reasons=None):
    """Generic reconciliation: checks whether Qty on the source document
    (Sales / Transfer In / Transfer Out) has been captured in the Stock
    Movement file, for the Reason/Transaction Type values relevant to this
    source. Returns one combined dataframe with a Status column.

    over_posted_reasons: optional list of Reason/Transaction Type values.
    When provided, a row is only classified as 'OVER CAPTURED' if the
    excess quantity actually comes from movement rows with one of these
    reasons (e.g. only 'POS Sale Transaction' for Sales). If the movement
    total is inflated by OTHER reasons mixed into the same Date/Store/
    Product bucket (e.g. Material Conversion, Return, Disposal), that
    excess is not treated as an over-posting finding - the row falls back
    to MATCH (if the eligible-reason movement equals source qty) or
    PARTIAL/whatever the eligible-reason movement alone indicates.
    """
    src = source_std.copy()
    src['Qty_num'] = clean_numeric(src['Qty']).abs()
    dup_cols = ['Date', 'Store', 'Product Code', 'Qty_num']
    if 'Document Number' in src.columns and (src['Document Number'] != '').any():
        dup_cols.insert(len(dup_cols) - 1, 'Document Number')
    src['Is_Duplicate'] = src.duplicated(subset=dup_cols, keep='first')
    duplicate_source = src[src['Is_Duplicate']].copy()
    unique_src = src[~src['Is_Duplicate']].copy()

    mov = mov_dedup[~mov_dedup['Is_Duplicate']].copy()
    if has_type and 'Transaction Type' in mov.columns and (mov['Transaction Type'] != '').any():
        types_upper = [t.upper() for t in (type_values or [])]
        mov = mov[mov['Transaction Type'].str.upper().isin(types_upper)].copy()

    if date_offset_days:
        parsed = pd.to_datetime(mov['Movement Date'], errors='coerce')
        shifted = (parsed - pd.Timedelta(days=date_offset_days)).dt.strftime('%Y-%m-%d')
        mov['Movement Date Match'] = shifted.fillna(mov['Movement Date'])
    else:
        mov['Movement Date Match'] = mov['Movement Date']

    src_agg = unique_src.groupby(['Date', 'Store', 'Product Code', 'Product Description'], as_index=False).agg(
        Source_Qty=('Qty_num', 'sum'),
        Doc_Count=('Document Number', 'nunique')
    )
    mov_agg = mov.groupby(['Movement Date Match', 'Store', 'Product Code'], as_index=False).agg(
        Movement_Qty=('Qty_num', 'sum'),
        **{'Movement Date': ('Movement Date', 'first')}
    )

    recon = pd.merge(
        src_agg, mov_agg,
        left_on=['Date', 'Store', 'Product Code'],
        right_on=['Movement Date Match', 'Store', 'Product Code'],
        how='outer'
    )
    recon['Date'] = recon['Date'].combine_first(recon['Movement Date'])
    recon['Source_Qty'] = recon['Source_Qty'].fillna(0)
    recon['Movement_Qty'] = recon['Movement_Qty'].fillna(0)

    # Separate "eligible for over-posting" movement (e.g. only rows whose
    # Reason is genuinely POS Sale Transaction) so movement from other
    # reasons mixed into the same bucket doesn't falsely trigger OVER CAPTURED.
    if over_posted_reasons and 'Transaction Type' in mov.columns:
        eligible_upper = [t.upper() for t in over_posted_reasons]
        mov_eligible = mov[mov['Transaction Type'].str.upper().isin(eligible_upper)]
        mov_eligible_agg = mov_eligible.groupby(['Movement Date Match', 'Store', 'Product Code'], as_index=False).agg(
            Movement_Qty_Eligible=('Qty_num', 'sum')
        )
        recon = pd.merge(
            recon, mov_eligible_agg,
            left_on=['Date', 'Store', 'Product Code'],
            right_on=['Movement Date Match', 'Store', 'Product Code'],
            how='left', suffixes=('', '_elig')
        )
        recon['Movement_Qty_Eligible'] = recon['Movement_Qty_Eligible'].fillna(0)
        if 'Movement Date Match_elig' in recon.columns:
            recon = recon.drop(columns=['Movement Date Match_elig'])
    else:
        recon['Movement_Qty_Eligible'] = recon['Movement_Qty']

    def classify(row):
        s, m = row['Source_Qty'], row['Movement_Qty']
        m_elig = row['Movement_Qty_Eligible']
        if s == 0 and m > 0:
            return 'UNMATCHED MOVEMENT'
        if s > 0 and m == 0:
            return 'NOT CAPTURED'
        if abs(s - m) < 1e-6:
            return 'MATCH'
        if m < s:
            return 'PARTIAL CAPTURED'
        # m > s: would be over-posted under a naive check. Only confirm it
        # as an over-posting finding if the eligible-reason movement alone
        # already exceeds the source qty; otherwise the excess came from
        # an unrelated Reason and shouldn't be flagged as over-posted.
        if m_elig > s + 1e-6:
            return 'OVER CAPTURED'
        if abs(m_elig - s) < 1e-6:
            return 'MATCH'
        return 'PARTIAL CAPTURED'

    recon['Status'] = recon.apply(classify, axis=1)
    recon['Source'] = source_label
    recon['Gap_Qty'] = recon['Source_Qty'] - recon['Movement_Qty']
    recon = recon.drop(columns=['Movement Date Match', 'Movement_Qty_Eligible'])
    return {
        'reconciled': recon,
        'duplicate_source': duplicate_source,
        'all_source': src,
    }

def suggest_best_date_offset(source_std, mov_dedup, type_values, has_type, max_offset=3):
    """Auto-detects the best 'Movement posted N days after source doc'
    offset by testing 0..max_offset and picking whichever yields the
    highest MATCH rate, measured only over (Store, Product) pairs that
    actually exist in the movement file."""
    mov_products = set(mov_dedup['Product Code'].astype(str).unique())
    results = []
    for offset in range(0, max_offset + 1):
        res = reconcile_source(source_std, mov_dedup, 'X', type_values, has_type, date_offset_days=offset)
        recon = res['reconciled']
        scoped = recon[(recon['Source_Qty'] > 0) & (recon['Product Code'].isin(mov_products))]
        rate = (scoped['Status'] == 'MATCH').mean() * 100 if len(scoped) else 0.0
        results.append((offset, rate, len(scoped)))
    best_offset = max(results, key=lambda r: r[1])[0] if results else 0
    return best_offset, results

def generate_excel_report(combined, per_source):
    """Builds a multi-sheet Excel export: one sheet per source plus a
    combined 'Not Captured' summary sheet."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        not_captured = combined[combined['Status'].isin(['NOT CAPTURED', 'PARTIAL CAPTURED', 'UNMATCHED MOVEMENT'])]
        not_captured.to_excel(writer, sheet_name='Belum Tercapture', index=False)
        combined.to_excel(writer, sheet_name='Semua Data (Gabungan)', index=False)
        for label, data in per_source.items():
            sheet = label[:31]
            data['reconciled'].to_excel(writer, sheet_name=sheet, index=False)
    output.seek(0)
    return output

def generate_sales_summary_html(r, dup_count, mov_dup_count, total_mov_tx):
    """Builds the Executive Dashboard (audit box + KPI cards) for SALES,
    styled the same way as the previous version of the app."""
    matched = r[r['Status'] == 'MATCH']
    not_posted = r[r['Status'] == 'NOT CAPTURED']
    partial = r[r['Status'] == 'PARTIAL CAPTURED']
    over = r[r['Status'] == 'OVER CAPTURED']

    total_unique_sales_tx = len(r[r['Source_Qty'] > 0])
    total_matched_tx = len(matched)
    total_not_posted = len(not_posted)
    total_partial = len(partial)
    total_over = len(over)

    posting_accuracy = (total_matched_tx / total_unique_sales_tx * 100) if total_unique_sales_tx > 0 else 0

    unposted_qty = not_posted['Source_Qty'].sum() + partial['Gap_Qty'].sum()
    net_sales_map = st.session_state.get('_sales_net_sales_map', {})
    unposted_val = 0.0
    if net_sales_map:
        combo = pd.concat([not_posted, partial])
        for _, row in combo.iterrows():
            key = (row['Date'], row['Store'], row['Product Code'])
            unposted_val += net_sales_map.get(key, 0.0)

    unposted_skus = pd.concat([not_posted, partial])['Product Code'].nunique()
    unposted_stores = pd.concat([not_posted, partial])['Store'].nunique()

    st.markdown(f"""
    <div class="audit-box">
        <h4>📋 Laporan Ringkasan Posting Sales</h4>
        <ul>
            <li><b>Posting Accuracy Rate:</b> {posting_accuracy:.2f}% transaksi sales berhasil terposting sempurna.</li>
            <li><b>Potential Revenue at Risk:</b> Estimasi Rp {unposted_val:,.0f} sales belum tercatat di stock movement.</li>
            <li><b>Unposted Quantity:</b> Total {int(unposted_qty):,} pcs sales belum mengurangi stok.</li>
            <li><b>Scope Impact:</b> Mempengaruhi {unposted_skus} SKU di {unposted_stores} Toko/Store.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Posting Accuracy</div>
            <div class="kpi-value" style="color: {'#16a34a' if posting_accuracy > 98 else '#ca8a04' if posting_accuracy > 95 else '#dc2626'};">{posting_accuracy:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Matched Tx</div>
            <div class="kpi-value" style="color: #16a34a;">{total_matched_tx:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Sales Not Posted</div>
            <div class="kpi-value" style="color: #dc2626;">{total_not_posted:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Partial Posted</div>
            <div class="kpi-value" style="color: #ca8a04;">{total_partial:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Over Posted</div>
            <div class="kpi-value" style="color: #2563eb;">{total_over:,}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Total Unique Sales Tx", f"{total_unique_sales_tx:,}", delta=f"-{dup_count} Duplicates", delta_color="inverse")
    col_b.metric("Total Stock Movement Tx", f"{total_mov_tx:,}", delta=f"-{mov_dup_count} Duplicates", delta_color="inverse")
    col_c.metric("Duplicate Sales Flagged", f"{dup_count:,}")
    col_d.metric("Duplicate Movement Flagged", f"{mov_dup_count:,}")
    st.markdown("---")

# ======================================================================
# UI
# ======================================================================
st.markdown("""
<div class="hero-header">
    <div class="hero-icon">📊</div>
    <h1>Stock movement Monitoring</h1>
    <p class="hero-author">Author : Rachmat Hidayat</p>
    <p class="hero-sub">Sales &amp; Interlocation vs Stock Movement Checker · Professional Inventory HRN</p>
    <div class="hero-badge"><span class="dot"></span>LIVE &nbsp;•&nbsp; OPTIMUS CLOUD</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# UPLOAD SECTION (moved from sidebar to main area, glass card)
# ---------------------------------------------------------------
st.markdown("""
<div class="glass-card">
    <div class="glass-card-title">📁 Upload Data</div>
    <div class="glass-card-sub">Upload file Sales &amp; Stock Movement (wajib), plus Interlocation Diterima/Dikirim (opsional). Bisa upload beberapa file sekaligus per kategori (mis. file harian tanggal 1 s/d 30) - semua akan digabung otomatis sebelum diproses.</div>
</div>
""", unsafe_allow_html=True)

up_col1, up_col2, up_col3, up_col4 = st.columns(4)
with up_col1:
    st.markdown("**1. File Sales**")
    sales_files = st.file_uploader("Upload File Sales", type=['csv', 'xlsx', 'xls'], key="sales", label_visibility="collapsed", accept_multiple_files=True)
with up_col2:
    st.markdown("**2. Stock Movement**")
    movement_files = st.file_uploader("Upload File Stock Movement", type=['csv', 'xlsx', 'xls'], key="mov", label_visibility="collapsed", accept_multiple_files=True)
with up_col3:
    st.markdown("**3. Transfer In (Diterima)**")
    transfer_in_files = st.file_uploader("Upload File Interlocation (Transfer To = toko ini)", type=['csv', 'xlsx', 'xls'], key="tin", label_visibility="collapsed", accept_multiple_files=True)
with up_col4:
    st.markdown("**4. Transfer Out (Dikirim)**")
    transfer_out_files = st.file_uploader("Upload File Interlocation (Transfer From = toko ini)", type=['csv', 'xlsx', 'xls'], key="tout", label_visibility="collapsed", accept_multiple_files=True)

def _read_one(f):
    """Reads a single uploaded file (csv/xlsx) into a string-typed DataFrame."""
    if f.name.lower().endswith('.csv'):
        return auto_detect_csv(f)
    df = pd.read_excel(f, dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    return df

def _read_any(files):
    """Reads and concatenates ANY number of uploaded files of the same
    category (e.g. 30 daily Sales exports for date 1-30) into a single
    DataFrame. Files don't need identical columns - pd.concat aligns by
    column name and fills missing ones with blank, so a slightly
    different export format on some days won't break the batch."""
    if not files:
        return None
    frames = []
    for f in files:
        try:
            frames.append(_read_one(f))
        except Exception as e:
            st.error(f"Gagal membaca {f.name}: {e}")
    if not frames:
        return None
    combined = pd.concat(frames, ignore_index=True, sort=False).fillna('')
    if len(files) > 1:
        st.caption(f"✅ {len(files)} file digabung -> {len(combined):,} baris total.")
    return combined

sales_preview = _read_any(sales_files)
mov_preview = _read_any(movement_files)
tin_preview = _read_any(transfer_in_files)
tout_preview = _read_any(transfer_out_files)

# ---------------------------------------------------------------
# ADVANCED SETTINGS (mapping kolom + reason type) - collapsed by
# default in the main area, no longer cluttering the sidebar.
# ---------------------------------------------------------------
sales_map = mov_map = tin_map = tout_map = None
sales_types = tin_types = tout_types = None
has_txn_type = False

if any(p is not None for p in [sales_preview, mov_preview, tin_preview, tout_preview]):
    with st.expander("⚙️ Pengaturan Lanjutan - Mapping Kolom & Reason/Transaction Type", expanded=False):
        st.caption("Kolom & reason sudah ditebak otomatis. Buka bagian ini hanya jika perlu koreksi manual.")
        m1, m2 = st.columns(2)
        with m1:
            sales_map = build_column_mapping_ui(sales_preview, SALES_FIELD_CANDIDATES, SALES_OPTIONAL, "sales", "Sales", container=st) if sales_preview is not None else None
            tin_map = build_column_mapping_ui(tin_preview, TRANSFER_IN_FIELD_CANDIDATES, TRANSFER_IN_OPTIONAL, "tin", "Transfer In (Diterima)", container=st) if tin_preview is not None else None
        with m2:
            mov_map = build_column_mapping_ui(mov_preview, MOV_FIELD_CANDIDATES, MOV_OPTIONAL_FIELDS, "mov", "Stock Movement", container=st) if mov_preview is not None else None
            tout_map = build_column_mapping_ui(tout_preview, TRANSFER_OUT_FIELD_CANDIDATES, TRANSFER_OUT_OPTIONAL, "tout", "Transfer Out (Dikirim)", container=st) if tout_preview is not None else None

        st.markdown("---")

        # Reason/Transaction Type selection per source
        if mov_preview is not None and mov_map is not None and mov_map.get('Transaction Type') not in (None, NONE_LABEL):
            has_txn_type = True
            txn_col = mov_map['Transaction Type']
            unique_types = sorted(mov_preview[txn_col].dropna().astype(str).str.strip().unique().tolist())
            r1, r2, r3 = st.columns(3)
            with r1:
                default_s = [t for t in unique_types if 'sale' in t.lower() or 'jual' in t.lower()] or unique_types
                sales_types = st.multiselect("Reason -> SALES:", unique_types, default=default_s, key="sales_types")
            with r2:
                default_in = [t for t in unique_types if 'transfer' in t.lower() and 'receiv' in t.lower() and 'sale' not in t.lower()]
                tin_types = st.multiselect("Reason -> TRANSFER IN:", unique_types, default=default_in, key="tin_types")
            with r3:
                default_out = [t for t in unique_types if 'transfer' in t.lower() and 'receiv' not in t.lower() and 'sale' not in t.lower()]
                tout_types = st.multiselect("Reason -> TRANSFER OUT:", unique_types, default=default_out, key="tout_types")
        elif mov_preview is not None:
            st.info("ℹ️ Kolom Reason/Transaction Type di Stock Movement tidak dipetakan - semua baris movement dianggap relevan untuk tiap sumber (kurang akurat).")

st.sidebar.title("🛠️ Panel Control")
st.sidebar.markdown("---")
st.sidebar.caption("File upload sekarang ada di halaman utama. Panel ini hanya untuk pengaturan proses.")

date_offset_days = st.sidebar.number_input(
    "Toleransi selisih hari (Movement setelah dokumen sumber):",
    min_value=0, max_value=7, value=0, step=1,
    help="Dihitung otomatis dari data Sales setelah tombol CHECK ditekan (jika mapping lengkap). Bisa diubah manual."
)

check_button = st.sidebar.button("🚀 CHECK CAPTURE STATUS", use_container_width=True, type="primary")

def _mapping_complete(preview, mapping, required_fields):
    if preview is None or mapping is None:
        return False
    return all(mapping.get(f) and mapping[f] != NONE_LABEL for f in required_fields)

if check_button:
    errors = []
    if not _mapping_complete(sales_preview, sales_map, SALES_FIELD_CANDIDATES):
        errors.append("Sales")
    if not _mapping_complete(mov_preview, mov_map, MOV_FIELD_CANDIDATES):
        errors.append("Stock Movement")
    has_tin = _mapping_complete(tin_preview, tin_map, TRANSFER_IN_FIELD_CANDIDATES)
    has_tout = _mapping_complete(tout_preview, tout_map, TRANSFER_OUT_FIELD_CANDIDATES)

    if "Sales" in errors or "Stock Movement" in errors:
        st.warning(f"⚠️ Kolom wajib belum lengkap untuk: {', '.join(errors)}. Lengkapi mapping di sidebar.")
    else:
        with st.spinner("🔍 Memproses rekonsiliasi..."):
            sales_std = apply_mapping(sales_preview, sales_map, date_fields=['Date'], store_fields=['Store'], code_fields=['Product Code'])
            mov_std = apply_mapping(mov_preview, mov_map, date_fields=['Movement Date'], store_fields=['Store'], code_fields=['Product Code'])
            mov_dedup = dedupe_movement(mov_std)

            # Auto-detect date offset using Sales (largest, most reliable volume)
            auto_offset, offset_results = suggest_best_date_offset(sales_std, mov_dedup, sales_types, has_txn_type)
            st.session_state['_offset_info'] = (auto_offset, offset_results)
            effective_offset = date_offset_days if date_offset_days else auto_offset

            per_source = {}
            # Over-posting for SALES should only be flagged when the excess
            # movement genuinely comes from "POS Sale Transaction" - other
            # reasons (Material Conversion, Return, Disposal, etc.) mixed
            # into the same Date/Store/Product bucket must not create a
            # false OVER POSTED finding.
            sales_over_posted_reasons = None
            if has_txn_type and mov_map.get('Transaction Type') not in (None, NONE_LABEL):
                _all_reasons = mov_preview[mov_map['Transaction Type']].dropna().astype(str).str.strip().unique().tolist()
                sales_over_posted_reasons = [t for t in _all_reasons if t.strip().upper() == 'POS SALE TRANSACTION']
                if not sales_over_posted_reasons:
                    sales_over_posted_reasons = None  # literal reason not found - fall back to no restriction

            per_source['SALES'] = reconcile_source(sales_std, mov_dedup, 'SALES', sales_types, has_txn_type, effective_offset, over_posted_reasons=sales_over_posted_reasons)

            # Build a (Date, Store, Product Code) -> Net Sales lookup for the
            # Executive Dashboard's "Potential Revenue at Risk" figure.
            if 'Net Sales' in sales_std.columns and (sales_std['Net Sales'] != '').any():
                ns = sales_std.copy()
                ns['Net Sales_num'] = clean_numeric(ns['Net Sales'])
                ns_agg = ns.groupby(['Date', 'Store', 'Product Code'])['Net Sales_num'].sum()
                st.session_state['_sales_net_sales_map'] = ns_agg.to_dict()
            else:
                st.session_state['_sales_net_sales_map'] = {}

            st.session_state['_sales_dup_count'] = len(per_source['SALES']['duplicate_source'])
            st.session_state['_mov_dup_count'] = int(mov_dedup['Is_Duplicate'].sum())
            st.session_state['_total_mov_tx'] = int((~mov_dedup['Is_Duplicate']).sum())

            if has_tin:
                tin_std = apply_mapping(tin_preview, tin_map, date_fields=['Date'], store_fields=['Store'], code_fields=['Product Code'])
                per_source['TRANSFER IN'] = reconcile_source(tin_std, mov_dedup, 'TRANSFER IN', tin_types, has_txn_type, effective_offset)
                if has_txn_type and not tin_types:
                    st.warning("⚠️ Tidak ada Reason/Transaction Type yang dipilih untuk TRANSFER IN. Semua item transfer masuk akan otomatis dianggap 'NOT CAPTURED'. Cek daftar Reason yang tersedia di sidebar dan pilih yang sesuai (mis. 'Receiving Stock Transfer').")
            if has_tout:
                tout_std = apply_mapping(tout_preview, tout_map, date_fields=['Date'], store_fields=['Store'], code_fields=['Product Code'])
                per_source['TRANSFER OUT'] = reconcile_source(tout_std, mov_dedup, 'TRANSFER OUT', tout_types, has_txn_type, effective_offset)
                if has_txn_type and not tout_types:
                    st.warning("⚠️ Tidak ada Reason/Transaction Type di file Stock Movement yang cocok sebagai 'Transfer Out' (mis. 'Sending Stock Transfer'/'Goods Issue'). Kemungkinan file Stock Movement Anda memang belum mencakup transaksi pengiriman antar toko - semua item TRANSFER OUT akan tampil 'NOT CAPTURED'. Ini bisa jadi temuan nyata: transfer keluar belum tercatat di Stock Movement.")

            combined = pd.concat([v['reconciled'] for v in per_source.values()], ignore_index=True)

            st.session_state['per_source'] = per_source
            st.session_state['combined'] = combined
            st.session_state['effective_offset'] = effective_offset
            st.session_state['missing_transfer_files'] = []
            if not has_tin and (tin_preview is not None or transfer_in_files):
                st.session_state['missing_transfer_files'].append('Transfer In')
            if not has_tout and (tout_preview is not None or transfer_out_files):
                st.session_state['missing_transfer_files'].append('Transfer Out')

if 'combined' in st.session_state:
    combined = st.session_state['combined']
    per_source = st.session_state['per_source']
    auto_offset, offset_results = st.session_state.get('_offset_info', (0, []))

    st.info(f"📅 Toleransi selisih hari yang dipakai: **{st.session_state['effective_offset']} hari** "
            f"(auto-detected dari Sales: {auto_offset} hari - {', '.join(f'{o}h:{r:.0f}%' for o,r,n in offset_results)})")

    # Coverage sanity check per source
    for label, res in per_source.items():
        src_products = set(res['all_source']['Product Code'].unique())
        mov_products = set(st.session_state.get('_mov_products', set()))
    
    st.markdown("### 📊 Ringkasan")
    cols = st.columns(len(per_source))
    for i, (label, res) in enumerate(per_source.items()):
        r = res['reconciled']
        not_captured = r[r['Status'].isin(['NOT CAPTURED', 'PARTIAL CAPTURED'])]
        total_docs = len(r[r['Source_Qty'] > 0])
        with cols[i]:
            st.metric(f"{label} - Belum Tercapture", f"{len(not_captured)} / {total_docs}")

    tab_labels = list(per_source.keys()) + ["📦 Gabungan / Export"]
    tabs = st.tabs(tab_labels)

    status_colors = {
        'MATCH': 'background-color:#d4edda',
        'NOT CAPTURED': 'background-color:#f8d7da',
        'PARTIAL CAPTURED': 'background-color:#fff3cd',
        'OVER CAPTURED': 'background-color:#cce5ff',
        'UNMATCHED MOVEMENT': 'background-color:#e2e3e5',
    }

    def style_status(df):
        # Pandas Styler has a hard cap on total styled cells (rows x cols)
        # to avoid runaway rendering cost. Our reconciliation tables can
        # get large (many SKUs x many stores x many days), so raise the
        # cap to fit the current dataframe instead of leaving pandas'
        # conservative default (262144) in place.
        n_cells = df.shape[0] * df.shape[1]
        if n_cells > pd.get_option("styler.render.max_elements"):
            pd.set_option("styler.render.max_elements", n_cells + 1000)
        return df.style.apply(lambda row: [status_colors.get(row['Status'], '')] * len(row), axis=1)

    for i, label in enumerate(per_source.keys()):
        with tabs[i]:
            r = per_source[label]['reconciled'].sort_values(['Status', 'Date'])
            if label == 'SALES':
                generate_sales_summary_html(
                    r,
                    st.session_state.get('_sales_dup_count', 0),
                    st.session_state.get('_mov_dup_count', 0),
                    st.session_state.get('_total_mov_tx', 0)
                )
            status_filter = st.multiselect(f"Filter Status ({label}):", r['Status'].unique().tolist(), default=r['Status'].unique().tolist(), key=f"filter_{label}")
            r_filtered = r[r['Status'].isin(status_filter)]
            st.dataframe(style_status(r_filtered[['Date', 'Store', 'Product Code', 'Product Description', 'Source_Qty', 'Movement_Qty', 'Gap_Qty', 'Status']]), use_container_width=True, height=450)
            dup = per_source[label]['duplicate_source']
            if len(dup):
                with st.expander(f"⚠️ {len(dup)} baris duplikat terdeteksi di dokumen {label} (sudah dikeluarkan dari perhitungan)"):
                    st.dataframe(dup, use_container_width=True)

    with tabs[-1]:
        st.markdown("#### Semua item yang BELUM tercapture di Stock Movement (semua sumber)")
        not_captured_all = combined[combined['Status'].isin(['NOT CAPTURED', 'PARTIAL CAPTURED', 'UNMATCHED MOVEMENT'])].sort_values(['Source', 'Status', 'Date'])
        st.dataframe(style_status(not_captured_all[['Source', 'Date', 'Store', 'Product Code', 'Product Description', 'Source_Qty', 'Movement_Qty', 'Gap_Qty', 'Status']]), use_container_width=True, height=500)

        excel_data = generate_excel_report(combined, per_source)
        st.download_button(
            "📥 Download Laporan Excel",
            data=excel_data,
            file_name=f"capture_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.markdown("""
    <div class="glass-card">
    <h4>👋 Cara pakai</h4>

    1. Upload **File Sales** dan **File Stock Movement** (wajib) di panel atas.
    2. Upload **File Interlocation - Diterima** dan/atau **Dikirim** (opsional, kalau ada).
    3. Buka **⚙️ Pengaturan Lanjutan** kalau perlu koreksi mapping kolom / Reason (biasanya sudah benar otomatis).
    4. Klik **CHECK CAPTURE STATUS** di sidebar.

    Program otomatis menyamakan format tanggal dan kode toko yang berbeda-beda antar file (mis. `0104` vs `104`, `2026-08-12` vs `8/12/2026`).
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="app-footer">
    Stock movement Monitoring &nbsp;·&nbsp; Sales &amp; Interlocation vs Stock Movement Checker &nbsp;·&nbsp; Built with Pyhton
</div>
""", unsafe_allow_html=True)
