import streamlit as st
import plotly.express as px
import pandas as pd
import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("cdn-perf-reports")

def getLog(uuid):
    response = table.get_item(
        Key={
            'uuid': uuid
        }
    )
        
    if 'Item' in response:
        return response['Item']
    else:
        print(f"No item found with uuid: {uuid}")
        return None

def drawTimeline(data):
    phases = []
    phases.append(("Fetch", data["startTime"], data["fetchStart"]))
    phases.append(("DNS Lookup", data["domainLookupStart"], data["domainLookupEnd"]))
    phases.append(("TCP Connect", data["connectStart"], data["connectEnd"]))
    if "secureConnectionStart" in data:
        phases.append(("Secure Connect", data["secureConnectionStart"], data["connectEnd"]))
    phases.append(("Request", data["requestStart"], data["responseStart"]))
    phases.append(("Response", data["responseStart"], data["responseEnd"]))
    if "unloadEventStart" in data:
        phases.append(("Unload", data["unloadEventStart"], data["unloadEventEnd"]))
    if "domInteractive" in data:
        phases.append(("DOM Interactive", data["domInteractive"], data["domContentLoadedEventStart"]))
    if "domContentLoadedEventStart" in data:
        phases.append(("DOM Content Loaded", data["domContentLoadedEventStart"], data["domContentLoadedEventEnd"]))
    if "domContentLoadedEventEnd" in data:
        phases.append(("DOM Complete", data["domContentLoadedEventEnd"], data["domComplete"]))
    if "loadEventStart" in data:
        phases.append(("Load Event", data["loadEventStart"], data["loadEventEnd"]))

    df = pd.DataFrame(phases, columns=["Phase", "Start", "End"])
    df['delta'] = df['End'] - df['Start']

    fig = px.timeline(
        df,
        x_start = "Start",
        x_end = "End",
        y = "Phase",
        title = data["name"],
        labels = {"Phase": "Phase"},
    )

    fig.layout.xaxis.title = 'Time (ms)'
    fig.layout.xaxis.type = 'linear'
    fig.layout.yaxis.title = 'Phase'
    fig.data[0].x = df.delta.tolist()
    fig.update_yaxes(autorange="reversed") 
    st.plotly_chart(fig)

with st.sidebar:
    with st.form("uuid_form"):
        uuid = st.text_input("UUID")
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.session_state["uuid"] = uuid

if "uuid" in st.session_state:
    uuid = st.session_state.uuid
    log = getLog(uuid)
    if log:
        source_ip = log['source_ip']
        x_forward_for = log['x-forwarded-for']
        
        data = log['data']
        dataObj = json.loads(data)
        entries = dataObj['entries']
        image_loading_headers = dataObj['image_loading_headers']
        
        st.title('Source IP')
        st.markdown(f"**source ip:** {source_ip}")
        st.markdown(f"**x-forwarded-for:** {x_forward_for}")
        
        st.title("Entries loading timeline")
        for entry in entries:
            if entry["entryType"] == "resource" or entry["entryType"] == "navigation":
                drawTimeline(entry)

        st.title("Image loading headers")
        for header in image_loading_headers:
            st.json(header)
    else:
        st.warning("No log found", icon="⚠️")
