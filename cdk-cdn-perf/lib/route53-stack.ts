import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import {
    HostedZone,
    CnameRecord,
} from 'aws-cdk-lib/aws-route53';
import { LogGroup } from 'aws-cdk-lib/aws-logs';

export class Route53Stack extends cdk.Stack {
    public readonly hostedZone: HostedZone;

    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // parameter
        const TestDomainName = new cdk.CfnParameter(this, 'TestDomainName', {
            type: 'String',
            description: 'DNS Test domain，for example: perf.example.com'
        });

        // create log group
        const logGroup = new LogGroup(this, 'CdnPerfRoute53LogGroup', {
            logGroupName: `/aws/route53/${TestDomainName.valueAsString}`,
        });

        // create Route53 Hosted Zone
        this.hostedZone = new HostedZone(this, 'CdnPerfHostedZone', {
            zoneName: TestDomainName.valueAsString,
            queryLogsLogGroupArn: logGroup.logGroupArn
        });

        // add CNAME record
        new CnameRecord(this, 'CdnPerfCnameRecord', {
            zone: this.hostedZone,
            recordName: `*.${TestDomainName.valueAsString}`,
            domainName: 'aws.amazon.com',
        });

        new cdk.CfnOutput(this, 'HostedZoneDomain', {
            value: `http://uuid.${TestDomainName.valueAsString}`,
            description: 'Route53 Hosted Zone Domain Name',
        });

        cdk.Tags.of(this.hostedZone).add('Name', 'CdnPerfHostedZone');
    }
}
