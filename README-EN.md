<p align="center">
    【<a href="README.md">中文</a> | English】
</p>

## 1. Background
Users may occasionally experience slow resource loading when opening web pages. This issue could be caused by various factors, including slow internet speeds, CDN node misrouting, or slow origin server responses.  
When debugging such issues, it’s often necessary to collect complete logs tracing the user-side to the origin server. In AWS CloudFront, all requests reaching the CloudFront POP points are logged, making it possible to query related logs. However, user-side loading metrics (such as DNS resolution time, TCP connection time, request time, and response time) cannot be recorded at the POP points and need to be collected on the user side. A common method is to use `curl` to retrieve these metrics. However, many end users lack the skills or tools to execute `curl` commands via the terminal. Therefore, a convenient tool is needed to help users collect and report these metrics easily.

## 2. Tools Overview
This project provides two tools:  
**Metric Collection and Reporting Tool:**  
This tool leverages the browser's Performance API to collect various metrics using JavaScript and uploads them to the server. The server uses API Gateway to expose an API endpoint, processes the incoming requests with Lambda, and stores the data in DynamoDB.  

**Data Visualization Tool:**  
A Python and Streamlit-based tool to query and visualize reported data for analysis easily.

## 3. Deployment Steps

### 1) Create a DynamoDB Table
- Table Name: `cdn-perf-reports`  
- Partition Key: `uuid` (String)  
- Capacity Mode: On-Demand  

### 2) Create a Lambda Function
- Runtime: Python 3.12  
- Copy the code from `lambda_function.py`.  
- In **Configuration -> Environment Variables**, add the environment variable: `TABLE_NAME` with the value `cdn-perf-reports`.  
- Configure the Lambda execution role to include permissions for writing to DynamoDB:  

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem"
            ],
            "Resource": [
                "arn:aws:dynamodb:<region>:<account-id>:table/cdn-perf-reports"
            ]
        }
    ]
}
```

### 3) Create an API Gateway
- Type: HTTP API  
- Create a new route: `/report/{uuid}`, method: POST  
- Integrate this route with the Lambda function. Set the **Payload format version** to 2.0.  

### 4) Modify `perf.html`
- Replace `report.example.com` with the API Gateway address.  
- Update `imageUrl` to the URL of an image distributed via CDN (ensure the domain matches the domain hosting `perf.html`).  
- Deploy `perf.html` to an accessible origin server (e.g., a web server or S3 bucket) and optionally distribute it via CDN.  

### 5) Deployment Complete
Visit the `perf.html` address. The page will display the collected metrics and allow users to find the corresponding `uuid`. Using this `uuid`, you can query the reported metrics in DynamoDB.  
![perf.html](./image.png)

## 4. Data Visualization Tool
This tool can be run locally or on an EC2 instance to easily query and display data.

### Steps to Run:
1. Ensure your local environment or EC2 instance has the necessary permissions to query DynamoDB.  
2. Install Python 3.12 and run the following commands:  
   ```bash
   pip install streamlit plotly pandas boto3
   streamlit run app.py
   ```
3. Use the `uuid` to query data. The interface is shown below:  
   ![data_visualization_tool](./perf_report_tool.jpeg)

## 5. Additional Notes
This tool is designed for debugging purposes and is not intended as a regular metric collection solution. Use it only when necessary.  
You can deploy the tool on a server and share the page link with users when issues are reported. Users can click the link to automatically detect and report relevant metrics.

## 6. References
- [W3C Resource Timing API](https://w3c.github.io/resource-timing/)  
- [Performance Monitoring with Performance API](https://juejin.cn/post/6844904182202253325)
