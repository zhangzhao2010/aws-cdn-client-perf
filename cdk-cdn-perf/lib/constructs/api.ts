import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigatewayv2';
import * as integrations from 'aws-cdk-lib/aws-apigatewayv2-integrations';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as path from 'path';
import { Construct } from 'constructs';

interface ApiConstructProps {
    table: dynamodb.Table;
}

export class ApiConstruct extends Construct {
    public readonly api: apigateway.HttpApi;

    constructor(scope: Construct, id: string, props: ApiConstructProps) {
        super(scope, id);

        const handler = new lambda.Function(this, 'CdnPerfHandler', {
            runtime: lambda.Runtime.PYTHON_3_12,
            handler: 'lambda_function.lambda_handler',
            code: lambda.Code.fromAsset(path.join(__dirname, '../../lambda')),
        });

        // Grant DynamoDB permissions to Lambda
        props.table.grantWriteData(handler);

        // Create HTTP API
        this.api = new apigateway.HttpApi(this, 'CdnPerfApi', {
            apiName: 'CdnPerfApi',
            corsPreflight: {
                allowHeaders: ['Content-Type', 'Authorization'],
                allowMethods: [apigateway.CorsHttpMethod.POST, apigateway.CorsHttpMethod.GET, apigateway.CorsHttpMethod.OPTIONS],
                allowOrigins: ['*'],
            },
        });

        // Add route with Lambda integration
        this.api.addRoutes({
            path: '/report/{uuid}',
            methods: [apigateway.HttpMethod.POST],
            integration: new integrations.HttpLambdaIntegration('CdnPerfIntegration', handler),
        });

        // Output the API URL
        new cdk.CfnOutput(this, 'ApiUrl', {
            value: this.api.url!,
            description: 'HTTP API Gateway URL',
        });
    }
}
