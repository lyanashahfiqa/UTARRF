import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import date
import uuid

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "suppliers.db"
DOC_DIR = DATA_DIR / "certificates"
DOC_DIR.mkdir(exist_ok=True)

def connect():
    return sqlite3.connect(DB_PATH)

def init_db():
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            certificate_number TEXT,
            expiry_date TEXT,
            file_path TEXT,
            original_filename TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")

init_db()

def get_suppliers():
    with connect() as conn:
        return pd.read_sql_query("SELECT * FROM suppliers ORDER BY id DESC", conn)

def expiry_label(value):
    if not value:
        return "No expiry date recorded"
    try:
        d = date.fromisoformat(value)
    except ValueError:
        return "Date needs review"
    return "Expired (date only)" if d < date.today() else "Date not expired (unverified)"


st.set_page_config(page_title='AI-SWHC | Research Prototype', page_icon='🌿', layout='wide')

st.markdown('''<style>
.block-container {padding-top: 1.7rem; max-width: 1200px;}
h1,h2,h3 {color:#12634e;}
[data-testid="stMetric"] {background:#f0f8f4; padding:16px; border-radius:12px; border:1px solid #d6e9df;}
</style>''', unsafe_allow_html=True)

st.sidebar.title('🌿 AI-SWHC')
st.sidebar.caption('Research Prototype • GitHub Edition')
page = st.sidebar.radio('Navigation', ['Dashboard', 'Supplier Verification', 'Document Processing', 'Traceability Monitoring', 'Compliance Assessment', 'Research Evaluation'])
st.sidebar.divider()
st.sidebar.info('Demonstration only. Not an official halal certification or verification service.')

if page == 'Dashboard':
    st.title('AI-SWHC Dashboard')
    st.write('Single-Window Halal Compliance • MSMFE Research Prototype')
    st.info('Supplier and document counts come from the temporary local database. The chart and activities below are simulated.')
    a,b,c,d = st.columns(4)
    a.metric('Suppliers Registered', str(len(get_suppliers())))
    b.metric('Documents Uploaded', str(int(get_suppliers()['file_path'].notna().sum())))
    c.metric('Records to Review', str(len(get_suppliers())))
    d.metric('Readiness', 'Checklist only')
    st.subheader('Compliance Overview')
    chart = pd.DataFrame({'Module':['Documents','Suppliers','Traceability','Evidence'], 'Completion (%)':[85,70,65,80]})
    st.bar_chart(chart.set_index('Module'))
    st.subheader('Recent Activities (Simulated)')
    st.dataframe(pd.DataFrame({'Activity':['Supplier record added','Document uploaded','Batch record updated'], 'Status':['Pending review','Awaiting extraction','Recorded']}), use_container_width=True, hide_index=True)
elif page == 'Supplier Verification':
    st.title('Supplier Records & Document Review')
    st.warning('This module does not verify official halal status. All certificates require independent verification with the relevant authority.')
    st.caption('Use synthetic test data only on public deployments. Uploaded files are not private and may be lost when the server restarts.')
    with st.form('supplier', clear_on_submit=True):
        name = st.text_input('Supplier name *')
        cert = st.text_input('Certificate number (optional)')
        expiry = st.date_input('Certificate expiry date', value=None)
        uploaded = st.file_uploader('Certificate file (PDF / PNG / JPG, max 5 MB)', type=['pdf','png','jpg','jpeg'])
        submitted = st.form_submit_button('Save supplier')
    if submitted:
        if not name.strip():
            st.error('Supplier name is required.')
        elif uploaded is not None and uploaded.size > 5 * 1024 * 1024:
            st.error('File exceeds 5 MB.')
        else:
            stored_path, original_name = None, None
            if uploaded is not None:
                raw = uploaded.getvalue()
                ext = Path(uploaded.name).suffix.lower()
                signatures = {'.pdf':raw.startswith(b'%PDF-'), '.png':raw.startswith(b'\x89PNG\r\n\x1a\n'), '.jpg':raw.startswith(b'\xff\xd8\xff'), '.jpeg':raw.startswith(b'\xff\xd8\xff')}
                if not signatures.get(ext, False):
                    st.error('File content does not match its extension.')
                    st.stop()
                filename = uuid.uuid4().hex + ext
                path = DOC_DIR / filename
                path.write_bytes(raw)
                stored_path, original_name = str(path), uploaded.name
            with connect() as conn:
                conn.execute('INSERT INTO suppliers (name,certificate_number,expiry_date,file_path,original_filename) VALUES (?,?,?,?,?)',
                             (name.strip(), cert.strip(), expiry.isoformat() if expiry else None, stored_path, original_name))
            st.success('Supplier record saved. Official verification is still pending.')
            st.rerun()
    df = get_suppliers()
    st.subheader('Saved suppliers')
    if df.empty:
        st.info('No suppliers saved yet.')
    else:
        display = df[['id','name','certificate_number','expiry_date','original_filename']].copy()
        display['Document date status'] = df['expiry_date'].apply(expiry_label)
        display['Official verification'] = 'Not verified'
        st.dataframe(display, use_container_width=True, hide_index=True)
        options = {f"{r['id']} — {r['name']}": int(r['id']) for _, r in df.iterrows()}
        choice = st.selectbox('Select record to manage', list(options))
        record_id = options[choice]
        record = df[df['id'] == record_id].iloc[0]
        if record['file_path'] and Path(record['file_path']).is_file():
            with open(record['file_path'], 'rb') as f:
                st.download_button('Download stored document', f.read(), file_name=record['original_filename'] or 'certificate', key=f'download_{record_id}')
        with st.expander('Edit selected supplier'):
            with st.form(f'edit_{record_id}'):
                new_name = st.text_input('Supplier name', value=record['name'])
                new_cert = st.text_input('Certificate number', value=record['certificate_number'] or '')
                new_expiry = st.date_input('Expiry date', value=date.fromisoformat(record['expiry_date']) if record['expiry_date'] else None)
                if st.form_submit_button('Save changes'):
                    if not new_name.strip():
                        st.error('Supplier name is required.')
                    else:
                        with connect() as conn:
                            conn.execute('UPDATE suppliers SET name=?,certificate_number=?,expiry_date=? WHERE id=?',
                                         (new_name.strip(),new_cert.strip(),new_expiry.isoformat() if new_expiry else None,record_id))
                        st.success('Changes saved.')
                        st.rerun()
        with st.expander('Delete selected supplier'):
            confirm = st.checkbox('I confirm deletion of this supplier record and attached file.', key=f'confirm_{record_id}')
            if st.button('Delete supplier', disabled=not confirm):
                with connect() as conn:
                    conn.execute('DELETE FROM suppliers WHERE id=?', (record_id,))
                if record['file_path']:
                    Path(record['file_path']).unlink(missing_ok=True)
                st.success('Supplier deleted.')
                st.rerun()
elif page == 'Document Processing':
    st.title('Document Processing')
    st.caption('Upload preview only. OCR and secure storage will be added in a later phase.')
    file=st.file_uploader('Upload a sample PDF, PNG or JPG', type=['pdf','png','jpg','jpeg'])
    if file: st.success(f'File selected: {file.name} ({file.size:,} bytes). Not saved or analysed.')
elif page == 'Traceability Monitoring':
    st.title('Traceability Monitoring')
    st.info('Illustrative traceability records. Database integration will follow.')
    st.dataframe(pd.DataFrame({'Ingredient':['Flour','Cooking oil','Sugar'], 'Supplier':['Supplier A','Supplier B','Supplier C'], 'Batch':['B001','B002','B003'], 'Review':['Pending','Pending','Pending']}), use_container_width=True, hide_index=True)
elif page == 'Compliance Assessment':
    st.title('Compliance Readiness Assessment')
    st.warning('This checklist is a demonstration, not a JAKIM compliance decision.')
    checks=['Supplier details recorded','Supporting documents available','Ingredient batches recorded','Evidence organised']
    selected=[st.checkbox(x) for x in checks]
    score=round(sum(selected)/len(checks)*100)
    st.progress(score/100)
    st.metric('Demonstration completeness score',f'{score}%')
    st.caption('The score measures only the four sample checklist items; it does not establish halal status.')
else:
    st.title('Research Evaluation')
    st.write('Prototype evaluation for perceived effectiveness (Section F of the proposal).')
    st.info('The validated questionnaire, consent process and response storage will be implemented after instrument finalisation and ethics approval.')
    st.write('Evaluation dimensions: documentation accuracy, supplier verification efficiency, traceability, centralised evidence submission and overall certification readiness support.')
