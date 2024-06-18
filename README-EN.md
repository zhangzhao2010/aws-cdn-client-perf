<p align="center">
    【<a href="README.md">中文</a> | English】
</p>
## 1. Background
When users open a webpage, they occasionally experience slow resource loading. This issue can be caused by various factors, including but not limited to: poor network speed, distant CDN node scheduling, slow origin server response, etc. While debugging such issues, it's often necessary to gather complete chain logs from the user side to the origin server. In AWS CloudFront, all requests that reach the CloudFront POP points are logged for query purposes. However, the metrics related to loading from the user side (DNS resolution time, TCP connection time, request time, response time, etc.) cannot be recorded at the POP points and need to be collected on the user side. The usual method is to use curl to obtain various metrics, but for end-users, most of them do not have the capability and tools to execute curl commands in the command line. Therefore, a convenient tool is needed to allow users to easily collect and report these metrics.

## 2. Tool Description
This tool uses the Performance API provided by the browser to obtain various metrics through JavaScript on the webpage and report them to the server. The server exposes a reporting API using API Gateway, processes the reporting requests with Lambda, and stores the data in DynamoDB.

## 3. Deployment Steps

### 1) Create a DynamoDB Table
Table name: cdn-perf-reports  
Partition key: uuid (String)  
Capacity mode: On-demand  

### 2) Create a Lambda Function
Runtime: Python 3.12;  
Copy the code from lambda_function.py;  
In Configuration -> Environment variables, add an environment variable: TABLE_NAME with the value cdn-perf-reports;  
Configure the execution role for the Lambda function to ensure it has write permissions to DynamoDB;  

```
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
Select HTTP API;  
Create a new route: /report/{uuid}, method: POST  
Integrate this route with the Lambda function, Payload format version: 2.0  

### 4) Modify perf.html
Change report.example.com to the API Gateway address;  
Change the image links in the image-container on the page to images distributed through the CDN (the domain needs to be the same as the domain where perf.html is loaded);  
Place perf.html on an accessible origin (server/S3), which can be distributed via CDN;  

### 5) Deployment Completion
Access the perf.html address. The page will display the collected metrics, and you can also find the reported metrics in DynamoDB using the uuid displayed on the page;  
![perf.html](./image.png)

## 4. Additional Notes
This tool is designed for debugging purposes and not for regular metric collection. Please use it only when needed.  
You can deploy the tool on the server-side. When users report issues, send them the page link, and the relevant information will be automatically detected and reported when they click the link.

## 5. Related Resources
https://w3c.github.io/resource-timing/  
https://juejin.cn/post/6844904182202253325
