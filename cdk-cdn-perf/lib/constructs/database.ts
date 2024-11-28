import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { Construct } from 'constructs';

export class DatabaseConstruct extends Construct {
    public readonly table: dynamodb.Table;

    constructor(scope: Construct, id: string) {
        super(scope, id);

        // Create DynamoDB table
        this.table = new dynamodb.Table(this, 'CdnPerfReports', {
            tableName: 'cdn-perf-reports',
            partitionKey: { name: 'uuid', type: dynamodb.AttributeType.STRING },
            billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
            removalPolicy: cdk.RemovalPolicy.DESTROY,
        });
    }
}
