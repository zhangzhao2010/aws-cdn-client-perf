import streamlit as st
import plotly.express as px
import pandas as pd
import boto3
import json
from datetime import datetime, timedelta
import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("cdn-perf-reports")
r53_base_domain = 'perf.example.com'
r53_log_group = '/aws/route53/perf.example.com'


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
    phases.append(
        ("DNS Lookup", data["domainLookupStart"], data["domainLookupEnd"]))
    phases.append(("TCP Connect", data["connectStart"], data["connectEnd"]))
    if "secureConnectionStart" in data:
        phases.append(
            ("Secure Connect", data["secureConnectionStart"], data["connectEnd"]))
    phases.append(("Request", data["requestStart"], data["responseStart"]))
    phases.append(("Response", data["responseStart"], data["responseEnd"]))
    if "unloadEventStart" in data:
        phases.append(
            ("Unload", data["unloadEventStart"], data["unloadEventEnd"]))
    if "domInteractive" in data:
        phases.append(
            ("DOM Interactive", data["domInteractive"], data["domContentLoadedEventStart"]))
    if "domContentLoadedEventStart" in data:
        phases.append(
            ("DOM Content Loaded", data["domContentLoadedEventStart"], data["domContentLoadedEventEnd"]))
    if "domContentLoadedEventEnd" in data:
        phases.append(
            ("DOM Complete", data["domContentLoadedEventEnd"], data["domComplete"]))
    if "loadEventStart" in data:
        phases.append(
            ("Load Event", data["loadEventStart"], data["loadEventEnd"]))

    df = pd.DataFrame(phases, columns=["Phase", "Start", "End"])
    df['delta'] = df['End'] - df['Start']

    fig = px.timeline(
        df,
        x_start="Start",
        x_end="End",
        y="Phase",
        title=data["name"],
        labels={"Phase": "Phase"},
    )

    fig.layout.xaxis.title = 'Time (ms)'
    fig.layout.xaxis.type = 'linear'
    fig.layout.yaxis.title = 'Phase'
    fig.data[0].x = df.delta.tolist()
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig)


def getR53Log(log):
    if 'r53_log' in log and len(log['r53_log']) > 0:
        return json.loads(log['r53_log'])

    logs_client = boto3.client('logs', region_name='us-east-1')
    uuid = log['uuid']
    start_time = int((datetime.now() - timedelta(hours=72)).timestamp() * 1000)
    end_time = int(datetime.now().timestamp() * 1000)
    domain_name = f"{str.lower(uuid)}.{r53_base_domain}"
    query = f'fields @timestamp, @message, version, queryTimestamp, hostZoneId,  queryName, queryType, responseCode, protocol, edgeLocation, resolverIp | filter queryName="{domain_name}"'

    try:
        response = logs_client.start_query(
            logGroupName=r53_log_group,
            startTime=start_time,
            endTime=end_time,
            queryString=query
        )
        query_id = response['queryId']
        print(f"start query cloudwatch log, query_id: {query_id}")

        while True:
            response = logs_client.get_query_results(queryId=query_id)
            if response['status'] in ['Complete', 'Failed', 'Cancelled']:
                print(f"stop query cloudwatch log, query_id: {query_id}")
                break
            time.sleep(1)

        print(response)
        if response['status'] == 'Complete':
            if len(response['results']) > 0:
                table.update_item(
                    Key={
                        'uuid': uuid
                    },
                    UpdateExpression='SET r53_log = :r53_log',
                    ExpressionAttributeValues={
                        ':r53_log': json.dumps(response['results'])
                    }
                )

        return response['results']

    except Exception as e:
        print(f"Error querying logs: {str(e)}")
        return []


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
        isReportR53Log = dataObj.get('isReportR53Log', False)

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

        if isReportR53Log:
            r53_log = getR53Log(log)
            st.title(f"{str.lower(uuid)}.{r53_base_domain} Route53 query log")
            if len(r53_log) > 0:
                for r53_log_item in r53_log:
                    show_item = {}
                    for item in r53_log_item:
                        show_item[item['field']] = item['value']
                    st.json(json.dumps(show_item))
            else:
                st.text("No log found yet, please retry after 5 minutes")
    else:
        st.warning("No log found", icon="⚠️")
