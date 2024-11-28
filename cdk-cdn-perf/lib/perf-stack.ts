import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { DatabaseConstruct } from './constructs/database';
import { ApiConstruct } from './constructs/api';


export class PerfStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // Create DynamoDB table
        const database = new DatabaseConstruct(this, 'Database');

        // Create API Gateway and Lambda
        const api = new ApiConstruct(this, 'Api', {
            table: database.table,
        });

        // Add tags to all resources
        cdk.Tags.of(this).add('Project', 'CdnPerf');
    }
}
