#!/usr/bin/env python3
import boto3
from kubernetes import client as kube_client
from os import environ
from time import time
from sys import exit

def lambda_handler(event, context):
    kube_conf = kube_client.Configuration()
    ec2client = boto3.client('ec2')
    elbclient = boto3.client('elbv2')

    tg_arns = environ['TG_ARN']
    ports = environ['INSTANCE_PORT']
    kube_conf.host = environ['KUBE_HOST']
    kube_token = environ['KUBE_TOKEN']

    instance = event['detail']['EC2InstanceId']
    start = time()
    try:
        nodename = ec2client.describe_instances(InstanceIds=[instance])['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['PrivateDnsName']
    except Exception as e:
        print(e)
        exit(1)
    duration = time() - start
    print('ec2.describe_instances call took ',)
    print(duration)

    kube_conf.verify_ssl = False
    kube_conf.api_key = {"authorization": "Bearer " + kube_token}
    kube_conf.timeout_seconds = 10

    kubeApiClient = kube_client.ApiClient(kube_conf)
    
    kube_api_v1 = kube_client.CoreV1Api(kubeApiClient)
    
    body = {
            "metadata": {
                "labels": {
                    "alpha.service-controller.kubernetes.io/exclude-balancer": "true"}
            }
        }
    
    print("Labeling node " + nodename)
    start = time()
    try:
        response_kube = kube_api_v1.patch_node(nodename, body)
    except Exception as e:
        print(e)
        exit(1)
    duration = time() - start

    print('kube api call took ',)
    print(duration)
    #print(response_kube)


    i=0
    for tg_arn in tg_arns.split(','):
        port = int(ports.split(',')[i])
        i += 1
        print("Deregistering instance " + instance + " port " + str(port) + " from TG " + tg_arn)
        start = time()
        try:
            response_aws = elbclient.deregister_targets(
                TargetGroupArn=tg_arn,
                Targets=[
                    {
                        'Id': instance,
                        'Port': port
                    }
                ]
            )
        except Exception as e:
            print(e)
        duration = time() - start
        print('elb.deregister took ',)
        print(duration)
        #print(response_aws)
    return None

if __name__ == '__main__':
    from sys import argv

    event = { 'detail' : { 'EC2InstanceId': argv[1] } }

    lambda_handler(event, 1)
