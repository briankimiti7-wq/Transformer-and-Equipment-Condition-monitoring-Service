"""Streamlit presentation only. All reads/writes pass through authorised services."""
from datetime import datetime,time,timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import plotly.express as px
import streamlit as st
from config.settings import TIMEZONE
from database.models.base import utcnow
from modules.assets import service as inventory
from modules.authentication import service as accounts
from modules.data_acquisition import service as acquisition
from modules.monitoring import service as monitoring
from modules.monitoring.demo import seed_demo
from modules.alerts.service import record_event


def frame(rows,hide=None):
    df=pd.DataFrame(rows)
    if hide:df=df.drop(columns=hide,errors='ignore')
    st.dataframe(df,hide_index=True,width='stretch')


def render(principal,user,grants):
    if user['platform']:
        platform(principal);return
    pages=['Overview','Asset register','Substations','Measurements','Evidence','Alerts']
    if 'users.manage' in grants:pages+=['Users','Sample data']
    page=st.sidebar.radio('Workspace',pages)
    st.sidebar.divider()
    st.sidebar.caption('Foundation release • Database-backed inventory and monitoring')
    st.sidebar.caption('Engineering diagnostics, bulk imports and full reporting are subsequent milestones.')
    if page=='Overview':overview(principal,grants)
    elif page=='Asset register':asset_register(principal,grants)
    elif page=='Substations':stations(principal,grants)
    elif page=='Measurements':measurements(principal,grants)
    elif page=='Evidence':evidence(principal)
    elif page=='Alerts':alerts(principal,grants)
    elif page=='Users':users(principal)
    elif page=='Sample data':
        st.title('Synthetic training data')
        st.write('Load two transformer examples, 150 time-series observations, oil gas results, inspection, relay and maintenance evidence, and a sample alert. All examples are explicitly labelled synthetic.')
        confirmed=st.checkbox('Load synthetic examples into my organisation')
        if st.button('Load sample dataset',disabled=not confirmed):
            with st.spinner('Writing sample history…'):seed_demo(principal)
            st.success('Synthetic dataset loaded. Open Overview to explore it.')


def platform(principal):
    st.title('Organisation administration')
    st.caption('Provision organisations and their initial administrators. Platform credentials do not impersonate tenant users.')
    rows=inventory.organisations(principal)
    frame(rows,['id'])
    with st.expander('Register organisation',expanded=not rows):
        with st.form('org',clear_on_submit=True):
            a,b=st.columns(2)
            code=a.text_input('Organisation code');name=b.text_input('Organisation name')
            country=st.text_input('Country',value='Kenya')
            admin_email=st.text_input('Administrator email');admin_name=st.text_input('Administrator name')
            password=st.text_input('Initial administrator password (12+ characters)',type='password')
            confirmation=st.text_input('Repeat administrator password',type='password')
            if st.form_submit_button('Create organisation',type='primary'):
                if password!=confirmation:raise ValueError('Passwords do not match.')
                inventory.create_organisation(principal,code,name,country,admin_email,admin_name,password)
                st.success('Organisation created. Sign out and use its administrator account.');st.rerun()
    if rows:
        with st.form('orgstatus'):
            selected=st.selectbox('Organisation status',rows,format_func=lambda r:r['name'])
            active=st.selectbox('New status',['Active','Inactive'])
            if st.form_submit_button('Update organisation status'):
                inventory.set_organisation_active(principal,selected['id'],active=='Active');st.rerun()


def overview(principal,grants):
    st.title('Asset condition overview')
    st.caption('Evidence first. Missing measurements are never treated as healthy.')
    view=st.selectbox('Task view',['Asset / reliability','Operations','Maintenance','Supervisor'])
    st.caption('Task views change presentation only. Your signed-in role controls permissions.')
    assets=inventory.assets(principal);stations=inventory.substations(principal);alarms=monitoring.alerts(principal)
    cols=st.columns(4)
    cols[0].metric('Registered assets',len(assets));cols[1].metric('Transformers',sum(a['type_code']=='transformer' for a in assets));cols[2].metric('Substations',len(stations));cols[3].metric('Open alerts',sum(a['status']!='resolved' for a in alarms))
    if not assets:
        st.info('Register a substation and transformer, or ask your administrator to load the synthetic dataset.');return
    if view=='Operations':
        st.subheader('Alarm and equipment context');frame(alarms,['id','asset_id','evidence'])
        st.info('Review relay events and equipment evidence under Evidence. No live SCADA connection is active.')
    elif view=='Maintenance':
        st.subheader('Follow-up queue');frame([a for a in alarms if a['status']!='resolved'],['id','asset_id','evidence'])
        st.info('Open Alerts to acknowledge and record findings. Work-order editing is scheduled for the maintenance milestone.')
    elif view=='Supervisor':
        acknowledged=[(a['acknowledged_at']-a['triggered_at']).total_seconds()/60 for a in alarms if a['acknowledged_at']]
        st.metric('Mean time to acknowledge',f'{sum(acknowledged)/len(acknowledged):.1f} min' if acknowledged else 'Not available')
        st.caption('Based on recorded acknowledgements, including synthetic scenarios if present.')
    selected=st.selectbox('Transformer or equipment',assets,format_func=lambda a:f"{a['code']} · {a['name']}")
    rows=monitoring.measurements(principal,selected['id'])
    st.subheader('Monitoring history')
    if not rows:st.info('No measurements recorded for this asset. Condition is not assessed.');return
    df=pd.DataFrame(rows)
    param=st.selectbox('Trend parameter',list(df['parameter'].unique()))
    series=df[df.parameter==param].copy()
    series['observed_at']=pd.to_datetime(series['observed_at'],utc=True).dt.tz_convert(TIMEZONE)
    series['provenance']=series.simulated.map({True:'Synthetic',False:'Recorded'})
    fig=px.line(series,x='observed_at',y='value',color='provenance',markers=True,labels={'observed_at':'Observation time (EAT)','value':f"{param} ({series.iloc[0]['unit']})"},color_discrete_map={'Synthetic':'#d58a18','Recorded':'#137d8c'})
    fig.update_layout(template='plotly_white',height=350,margin=dict(l=10,r=10,t=20,b=10))
    st.plotly_chart(fig,width='stretch')
    st.caption('Synthetic and recorded observations are plotted separately. Lines do not imply an engineering diagnosis.')
    last=series.iloc[-1]
    left,right=st.columns(2)
    left.metric('Latest observation',f"{last['value']:g} {last['unit']}")
    right.metric('Health classification','Not assessed')
    st.caption('Health-index calculations remain unavailable until their methodology and reference examples are validated.')
    # Coverage describes data presence, not technical confidence or health.
    applicable=[p for p in acquisition.parameters(principal) if p['code'] in ['top_oil','winding','ambient','loading'] and not (selected['construction']=='dry' and p['applicability']=='oil_only')]
    recent=[r for r in rows if r['observed_at']>=utcnow()-timedelta(hours=24)]
    covered=len({r['parameter_code'] for r in recent}&{p['code'] for p in applicable})
    if applicable:st.caption(f'Core monitoring coverage in the last 24 hours: {covered}/{len(applicable)} applicable parameters. Data presence is not a confidence score.')
    st.subheader('Latest evidence');frame(rows[-12:],['id','asset_id','parameter_code'])


def stations(principal,grants):
    st.title('Substations');frame(inventory.substations(principal),['id'])
    if 'inventory.write' not in grants:return
    with st.form('station',clear_on_submit=True):
        st.subheader('Register substation')
        code=st.text_input('Substation code');name=st.text_input('Substation name');location=st.text_input('Location')
        voltage=st.number_input('Voltage level (kV)',min_value=0.001,value=33.0)
        if st.form_submit_button('Save substation'):
            inventory.create_substation(principal,code,name,location,voltage);st.rerun()


def asset_register(principal,grants):
    st.title('Asset register');frame(inventory.assets(principal),['id','type_code'])
    if 'inventory.write' not in grants:return
    stations=inventory.substations(principal)
    if not stations:st.info('Register a substation first.');return
    st.subheader('Register equipment')
    types=inventory.catalogues(principal)
    kind=st.selectbox('Equipment category',types,format_func=lambda t:t['name'])
    construction=st.selectbox('Transformer construction',['oil','dry']) if kind['code']=='transformer' else None
    with st.form('asset',clear_on_submit=True):
        station=st.selectbox('Substation',stations,format_func=lambda s:s['name'])
        a,b=st.columns(2);code=a.text_input('Asset code');name=b.text_input('Asset name')
        manufacturer=a.text_input('Manufacturer');serial=b.text_input('Serial number')
        criticality=st.selectbox('Criticality',['Low','Medium','High','Critical'],index=1)
        details=None
        if kind['code']=='transformer':
            application=st.selectbox('Application',['distribution','power'])
            c1,c2,c3=st.columns(3)
            rating=c1.number_input('Rated capacity (kVA)',min_value=0.001,value=1000.0)
            primary=c2.number_input('Primary voltage (kV)',min_value=0.001,value=11.0)
            secondary=c3.number_input('Secondary voltage (kV)',min_value=0.001,value=0.415,format='%.3f')
            phases=c1.selectbox('Phases',[3,1]);frequency=c2.number_input('Frequency (Hz)',min_value=0.001,value=50.0)
            vector=c1.text_input('Vector group');cooling=c2.text_input('Cooling method');insulation=c3.text_input('Insulation class')
            details={'application':application,'construction':construction,'rating_kva':rating,'primary_kv':primary,'secondary_kv':secondary,'phases':phases,'frequency_hz':frequency,'vector_group':vector or None,'cooling':cooling or None,'insulation_class':insulation or None}
        if st.form_submit_button('Save asset',type='primary'):
            inventory.create_asset(principal,station['id'],kind['id'],code,name,manufacturer,serial,criticality,details);st.rerun()


def measurements(principal,grants):
    st.title('Measurements')
    if 'measurement_notice' in st.session_state:
        st.success(st.session_state.pop('measurement_notice'))
    st.caption('History and CSV downloads show at most the first 100,000 observations in chronological order. Large-history pagination is planned.')
    assets=inventory.assets(principal)
    if not assets:st.info('Register an asset first.');return
    asset=st.selectbox('Asset',assets,format_func=lambda a:f"{a['code']} · {a['name']}")
    rows=monitoring.measurements(principal,asset['id']);frame(rows,['id','asset_id','parameter_code'])
    if 'reports.read' in grants:
        exported=monitoring.measurements(principal,asset['id'],export=True)
        st.download_button('Download measurement CSV',pd.DataFrame(exported).to_csv(index=False).encode('utf-8-sig'),file_name='tecm_measurements.csv',mime='text/csv')
    if 'measurement.write' not in grants:return
    pars=[p for p in acquisition.parameters(principal) if asset['type_code']=='transformer' and not (p['applicability']=='oil_only' and asset['construction']=='dry')]
    if not pars:st.info('Monitoring parameters for this equipment category are not implemented yet.');return
    parameter=st.selectbox('Parameter',pars,format_func=lambda p:f"{p['name']} ({p['unit']})")
    local=utcnow().astimezone(ZoneInfo(TIMEZONE))
    with st.form('reading',clear_on_submit=True):
        value=st.number_input(f"Value ({parameter['unit']})",value=0.0,format='%.4f')
        date=st.date_input('Observation date (EAT)',value=local.date())
        clock=st.time_input('Observation time (EAT)',value=local.time().replace(tzinfo=None))
        synthetic=st.checkbox('This is a simulated observation')
        if st.form_submit_button('Save measurement',type='primary'):
            observed=datetime.combine(date,clock,tzinfo=ZoneInfo(TIMEZONE))
            _,created=acquisition.record_measurement(principal,asset['id'],parameter['id'],value,observed,parameter['unit'],synthetic)
            st.session_state.measurement_notice = 'Saved.' if created else 'Identical observation already exists; no duplicate saved.'
            st.rerun()
    st.caption('CSV/Excel bulk import preview and confirmation will be added in the acquisition milestone.')


def evidence(principal):
    st.title('Engineering evidence')
    assets=inventory.assets(principal)
    if not assets:st.info('No assets yet.');return
    asset=st.selectbox('Evidence asset',assets,format_func=lambda a:f"{a['code']} · {a['name']}")
    data=monitoring.evidence(principal,asset['id'])
    for label,key in [('Inspections','inspection_records'),('Relay events','relay_events'),('Maintenance history','maintenance_records')]:
        st.subheader(label)
        if data[key]:frame(data[key])
        else:st.caption('No evidence recorded.')
    st.subheader('Dissolved gas samples')
    if asset['construction']=='dry':st.info('Oil and DGA testing are not applicable to this dry-type transformer.')
    elif not data['dga_samples']:st.caption('No DGA samples recorded.')
    else:
        for sample in data['dga_samples']:
            with st.expander(sample['reference'],expanded=True):
                st.write(sample['sampled_at']);st.caption('Synthetic sample' if sample['simulated'] else 'Recorded sample')
                frame([{'Gas':k,'Concentration (ppm)':str(v)} for k,v in sample['gases'].items()])
        st.info('Gas results are evidence only. IEC/IEEE, Rogers and Duval interpretation are not yet enabled.')


def alerts(principal,grants):
    st.title('Alerts and feedback')
    items=monitoring.alerts(principal)
    if not items:st.info('No alerts recorded. This does not establish healthy equipment condition.');return
    frame(items,['id','asset_id','evidence'])
    item=st.selectbox('Review alert',items,format_func=lambda a:a['title'])
    st.write(item['message']);st.json(item['evidence'])
    st.subheader('Activity history');frame(monitoring.alert_events(principal,item['id']))
    choices=[]
    if 'alerts.write' in grants:
        if item['status']=='open':choices+=['acknowledge']
        if item['status']!='resolved':choices+=['verify','handoff','finding']
    if 'alerts.resolve' in grants:
        if item['status']=='acknowledged':choices+=['resolve']
        if item['status']=='resolved':choices+=['reopen']
    if 'feedback.write' in grants:choices+=['evaluate']
    if not choices:return
    action=st.selectbox('Action',choices)
    with st.form('alert_action',clear_on_submit=True):
        note=st.text_area('Evidence, findings or feedback')
        rating=st.slider('Alert clarity rating',1,5,3) if action=='evaluate' else None
        if st.form_submit_button('Save action',type='primary'):
            record_event(principal,item['id'],action,note,rating);st.rerun()


def users(principal):
    st.title('Organisation users');rows=accounts.list_users(principal);frame(rows,['id'])
    with st.form('new_user',clear_on_submit=True):
        email=st.text_input('User email');name=st.text_input('Display name')
        role=st.selectbox('Assigned role',['viewer','technician','electrical_engineer','maintenance_engineer','organisation_admin'])
        password=st.text_input('Initial password (12+ characters)',type='password')
        if st.form_submit_button('Create user'):
            accounts.create_user(principal,email,name,password,role);st.rerun()
    other=[r for r in rows if r['id']!=principal.user_id]
    if other:
        with st.form('user_status'):
            target=st.selectbox('Account',other,format_func=lambda u:u['email'])
            active=st.selectbox('Account status',['Active','Inactive'])
            if st.form_submit_button('Update account status'):
                accounts.set_user_active(principal,target['id'],active=='Active');st.rerun()
