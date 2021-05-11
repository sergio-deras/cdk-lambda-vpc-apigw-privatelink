from aws_cdk import (core as cdk,
                     aws_apigateway as apigateway,
                     aws_ec2 as ec2,
                     aws_lambda as lambda_,
                     aws_iam as iam)

class CdkLambdaVpcApigwPrivatelinkStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a VPC (2 AZ, each with private + public subnets and all the required components)
        vpc = ec2.Vpc(self, "Target_VPC",
            cidr="10.0.0.0/16"
        )
       
        # Sec Grp 
        sg = ec2.SecurityGroup(self, 'SecurityGroup',
            vpc=vpc,
            allow_all_outbound=True,
            security_group_name="VpcEndpoint_sg"
        )

        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443))


        #VPC endpoit
        vpc_endpoint = ec2.InterfaceVpcEndpoint(self, 'ApiVpcEndpoint', 
            vpc=vpc,
            private_dns_enabled=True,
            security_groups=[sg],
            service=ec2.InterfaceVpcEndpointAwsService(
                name="execute-api",
                port=443
            )
        ) 

        handler = lambda_.Function(self, "sayHi_fn",
            runtime=lambda_.Runtime.NODEJS_14_X,
            code=lambda_.Code.from_asset("resources/lambda"),
            handler="app.main"
        )


        """
        api = apigateway.RestApi(self, "sayHi_api",
            rest_api_name="Say Hi API",
            description="This service greets"
        )

        integration = apigateway.LambdaIntegration(handler,
            request_templates={"application/json": '{ "statusCode": "200" }'}
        )

        api.root.add_method("GET", integration)
        """
        
        apigateway.LambdaRestApi(self, "sayHiPrivateLambdaRestAPI",
            endpoint_types=[apigateway.EndpointType.PRIVATE],
            handler=handler,
            policy=iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        principals=[iam.AnyPrincipal()],
                        actions=['execute-api:Invoke'],
                        resources=['execute-api:/*'],
                        effect=iam.Effect.DENY,
                        conditions= {
                            "StringNotEquals": {"aws:SourceVpce": vpc_endpoint.vpc_endpoint_id}
                        }
                    ),
                    iam.PolicyStatement(
                        principals=[iam.AnyPrincipal()],
                        actions=['execute-api:Invoke'],
                        resources=['execute-api:/*'],
                        effect=iam.Effect.ALLOW
                    )
                ]
            )
        )

    # curl -i -H "x-apigw-api-id:myjyrrs5o4" https://vpce-0cd757894c224893f-rcu7az1g.execute-api.us-west-1.vpce.amazonaws.com/
 # vpce-0cd757894c224893f-rcu7az1g.execute-api.us-west-1.vpce.amazonaws.com

    """
        const vpc = ec2.Vpc.fromLookup(this, 'PrimaryVPC', {
            vpcName: '<vpcid>'
        })

    const a = Subnet.fromSubnetAttributes(this, 'ASubnet', {
      availabilityZone: 'eu-central-1a',
      subnetId: 'subnet-<id>'
    })

    const b = Subnet.fromSubnetAttributes(this, 'BSubnet', {
      availabilityZone: 'eu-central-1b',
      subnetId: 'subnet-<id>'
    })

    const sg = new SecurityGroup(this, 'SecurityGroup', {
      vpc,
      allowAllOutbound: true,
      securityGroupName: 'VpcEndpoint'
    });

    sg.addIngressRule(Peer.ipv4("<CIDR>"), Port.tcp(443))

    const vpcEndpoint = new InterfaceVpcEndpoint(this, 'ApiVpcEndpoint', {
      vpc,
      service: {
        name: 'com.amazonaws.eu-central-1.execute-api',
        port: 443
      },
      subnets: {
        subnets: [a, b]
      },
      privateDnsEnabled: true,
      securityGroups: [sg]
    })

    const fn = new lambda.Function(this, 'PrivateLambda', {
      runtime: lambda.Runtime.NODEJS_10_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, 'lambda')),
    });

    new apigateway.LambdaRestApi(this, 'PrivateLambdaRestApi', {
      endpointTypes: [apigateway.EndpointType.PRIVATE],
      handler: fn,
      policy: new iam.PolicyDocument({
        statements: [
          new iam.PolicyStatement({
            principals: [new iam.AnyPrincipal],
            actions: ['execute-api:Invoke'],
            resources: ['execute-api:/*'],
            effect: iam.Effect.DENY,
            conditions: {
              StringNotEquals: {
                "aws:SourceVpce": vpcEndpoint.vpcEndpointId
              }
            }
          }),
          new iam.PolicyStatement({
            principals: [new iam.AnyPrincipal],
            actions: ['execute-api:Invoke'],
            resources: ['execute-api:/*'],
            effect: iam.Effect.ALLOW
          })
        ]
      })
    })
"""