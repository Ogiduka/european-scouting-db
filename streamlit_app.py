"""Mobile-friendly Europe scouting viewer: documented demo and imported source CSV."""
from pathlib import Path
import io
import pandas as pd
import streamlit as st

ROOT=Path(__file__).parent
st.set_page_config(page_title='European Scouting DB',page_icon='🏀',layout='wide')
st.title('🏀 European Scouting DB')
st.caption('Scouting viewer · 2026/27 · Sources and samples are not a complete European database')

@st.cache_data(ttl=600)
def base_sheet(name):
    return pd.read_excel(ROOT/'data'/'European_Scouting_DB_v4_2026.xlsx',sheet_name=name)

league_tab, player_tab, source_tab, help_tab = st.tabs(['Players','FEB CSV','Leagues & Sources','Instructions'])
with league_tab:
    st.subheader('Player search · verified sample')
    st.info('This is a previously collected limited FEB sample. It does not contain all registered players; missing ages are not assumed to pass the age filter.')
    df=base_sheet('FEB V4 verified 18Oct')
    cols=list(df.columns)
    st.caption('Source sheet: FEB V4 verified 18Oct')
    search=st.text_input('Search player/team (text)',key='players_search')
    if search:
        df=df[df.astype(str).apply(lambda x: x.str.contains(search,case=False,regex=False)).any(axis=1)]
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button('Download displayed sample as CSV',df.to_csv(index=False).encode('utf-8-sig'),'feb_sample.csv','text/csv')
with player_tab:
    st.subheader('Imported FEB data')
    st.caption('Only shows the first-page importer output where present. CSV upload lets you inspect new verified exports on iPhone/iPad.')
    found=sorted((ROOT/'data').glob('feb_*.csv'))
    uploaded=st.file_uploader('Optional: upload CSV',type='csv')
    chosen=st.selectbox('Saved FEB exports', ['None']+[p.name for p in found])
    data=None
    try:
        if uploaded is not None: data=pd.read_csv(uploaded)
        elif chosen!='None': data=pd.read_csv(ROOT/'data'/chosen)
    except Exception as exc:
        st.error(f'Cannot read CSV: {exc}')
    if data is None:
        st.info('No successful automated CSV import yet. The scheduled workflow records failures instead of inventing rows.')
    else:
        league=st.selectbox('League', ['All']+sorted(data['league'].dropna().astype(str).unique().tolist())) if 'league' in data else 'All'
        if league!='All':data=data[data['league'].astype(str)==league]
        st.metric('Imported rows',len(data))
        st.dataframe(data,use_container_width=True,hide_index=True)
        st.download_button('Download import CSV',data.to_csv(index=False).encode('utf-8-sig'),'scouting_import.csv','text/csv')
with source_tab:
    st.subheader('Competition registry')
    lig=base_sheet('Lige Evrope')
    query=st.text_input('Find league/country',key='league_search')
    if query: lig=lig[lig.astype(str).apply(lambda x:x.str.contains(query,case=False,regex=False)).any(axis=1)]
    st.dataframe(lig,use_container_width=True,hide_index=True)
    st.subheader('Importer status')
    st.dataframe(base_sheet('V4 Import status'),use_container_width=True,hide_index=True)
with help_tab:
    st.markdown('''**What works now:** V4 competition directory, existing validated FEB sample, CSV uploads, downloads, and simple text search.

**What does not yet work:** universal age ≤34 filter (most sample rows do not have verified birthdates), full roster coverage, confirmed pagination and API integrations, all-Europe automatic import.

**Automatic import:** GitHub Actions schedule runs the FEB **first-page** importer once daily. If parsing fails or there are no rows, no data are overwritten. CSV availability depends on source response and terms of use. Check the Actions log. Imported data are only sample rankings, not full roster coverage.

**Your target scouting criteria:** all positions, age ≤34, PPG ≥0, league levels 1–4. These filters will become enforceable when complete age and season statistics are available.
''')
