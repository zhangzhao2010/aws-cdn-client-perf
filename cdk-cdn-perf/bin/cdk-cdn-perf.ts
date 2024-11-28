#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { PerfStack } from '../lib/perf-stack';
import { Route53Stack } from '../lib/route53-stack';

const app = new cdk.App();

new PerfStack(app, 'CdnPerfApp', {
  env: {
    region: 'us-east-1'
  }
});

new Route53Stack(app, 'CdnPerfRoute53', {
  env: {
    region: 'us-east-1'
  }
});

app.synth();