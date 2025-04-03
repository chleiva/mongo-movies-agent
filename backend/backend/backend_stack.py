from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    aws_cognito as cognito,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_iam as iam
)

from aws_cdk import RemovalPolicy
from aws_cdk import Duration
from constructs import Construct
from aws_cdk import aws_secretsmanager as secretsmanager




class BackendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)


        # Reference the existing secret
        mongoagent_secret = secretsmanager.Secret.from_secret_name_v2(
            self, "MongoAgentSecret", "mongoagent_secrets"
        )



        voyageai_layer = _lambda.LayerVersion(
            self, "VoyageAILayer",
            code=_lambda.Code.from_asset("layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
            description="Layer including voyageai and dependencies"
        )


        # S3 Bucket for Manufacturing Documents
        documents_bucket = s3.Bucket(
            self, "ManufacturingDocumentsBucket",
            bucket_name="manufacturingdocuments-alfa",
            removal_policy=RemovalPolicy.DESTROY,  # For dev; change for prod
            auto_delete_objects=True  # For dev only; ensure compliance before using in prod
        )


        # Reference existing Cognito User Pool
        user_pool = cognito.UserPool.from_user_pool_id(
            self, "ExistingUserPool",
            user_pool_id="us-east-1_C7yJkMG3f"
        )

        # Create Lambda function
        process_message_fn = _lambda.Function(
            self, "ProcessMessageFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="process_message.handler",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.seconds(600),
            memory_size=2048,
            environment={
                "BUCKET_NAME": documents_bucket.bucket_name,
                "SECRET_NAME": mongoagent_secret.secret_name
            },
            layers=[voyageai_layer]  # 👈 Reuse the same layer that has pymongo 
        )


        # Allow Lambda to generate pre-signed URLs for objects in this bucket
        documents_bucket.grant_read(process_message_fn)


        # Create Cognito Authorizer
        authorizer = apigw.CognitoUserPoolsAuthorizer(
            self, "CognitoAuthorizer",
            cognito_user_pools=[user_pool]
        )

        # Create API Gateway REST API
        api = apigw.RestApi(
            self, "UserApi",
            rest_api_name="UserServiceAPI",
        )

        user = api.root.add_resource("user")
        message = user.add_resource("message")

        message.add_method(
            "POST",
            apigw.LambdaIntegration(
                process_message_fn,
                timeout=Duration.seconds(60),
                integration_responses=[
                    apigw.IntegrationResponse(
                        status_code="200",
                        response_parameters={
                            "method.response.header.Access-Control-Allow-Origin": "'*'",
                            "method.response.header.Access-Control-Allow-Headers": "'Content-Type,Authorization'",
                            "method.response.header.Access-Control-Allow-Methods": "'POST,OPTIONS'"
                        }
                    )
                ]
            ),
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=authorizer,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": True,
                        "method.response.header.Access-Control-Allow-Headers": True,
                        "method.response.header.Access-Control-Allow-Methods": True,
                    }
                )
            ]
        )


        message.add_cors_preflight(
            allow_origins=[
                "http://localhost:5173",
                "https://mongoagent.com"
            ],
            allow_methods=["POST"],
            allow_headers=["Authorization", "Content-Type"],
        )


#s3 and lambda for document parsing

        # Then use it in your function
        index_new_document_fn = _lambda.Function(
            self, "IndexNewDocumentFunction",
            architecture=_lambda.Architecture.X86_64,  # Switch from ARM64
            function_name="IndexNewDocument",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index_new_document.handler",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.seconds(900),
            memory_size=1024,
            environment={
                "BUCKET_NAME": documents_bucket.bucket_name,
                "SECRET_NAME": mongoagent_secret.secret_name
            },
            layers=[voyageai_layer]
        )

        # Grant Lambda full access to the S3 bucket
        documents_bucket.grant_read_write(index_new_document_fn)

        # Grant S3 permission to invoke the Lambda
        index_new_document_fn.add_permission(
            "AllowS3Invoke",
            principal=iam.ServicePrincipal("s3.amazonaws.com"),
            source_arn=documents_bucket.bucket_arn,
        )

        # Add event notification for new object creation (PUT)
        documents_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED_PUT,
            s3n.LambdaDestination(index_new_document_fn)
        )


        # Allow Lambda to use Amazon Textract
        index_new_document_fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "textract:AnalyzeDocument",
                    "textract:DetectDocumentText",
                    "textract:GetDocumentAnalysis",
                    "textract:GetDocumentTextDetection",
                    "textract:StartDocumentAnalysis",
                    "textract:StartDocumentTextDetection"
                ],
                resources=["*"]  # Optionally narrow this to specific resources later
            )
        )


#SNS

        from aws_cdk import aws_sns as sns
        from aws_cdk import aws_sns_subscriptions as subs

        # 1. Create the SNS topic for Textract job notifications
        textract_topic = sns.Topic(
            self, "TextractJobDoneTopic",
            display_name="Textract Job Completion Notifications"
        )

        # 2. Create an IAM Role for Textract to publish to SNS
        textract_service_role = iam.Role(
            self, "TextractServiceRole",
            assumed_by=iam.ServicePrincipal("textract.amazonaws.com"),
            description="IAM Role that allows Textract to publish job results to SNS",
        )

        # Grant permission to publish to the topic
        textract_topic.grant_publish(textract_service_role)

        # 3. Subscribe the Lambda to the SNS topic
        textract_topic.add_subscription(
            subs.LambdaSubscription(index_new_document_fn)
        )


        index_new_document_fn.add_environment("TEXTRACT_SNS_TOPIC_ARN", textract_topic.topic_arn)
        index_new_document_fn.add_environment("TEXTRACT_ROLE_ARN", textract_service_role.role_arn)


        model_regions = ['us-east-1', 'us-west-2']
        model_name = "anthropic.claude-3-7-sonnet-20250219-v1:0"

        invoke_bedrock_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["bedrock:InvokeModel*"],
            resources=[
                f"arn:aws:bedrock:us-east-1:{self.account}:inference-profile/*",
                f"arn:aws:bedrock:us-east-2:{self.account}:inference-profile/*",
                f"arn:aws:bedrock:us-west-2:{self.account}:inference-profile/*",
                f"arn:aws:bedrock:us-east-1::foundation-model/*",
                f"arn:aws:bedrock:us-east-2::foundation-model/*",
                f"arn:aws:bedrock:us-west-2::foundation-model/*"
            ]
        )

        index_new_document_fn.add_to_role_policy(invoke_bedrock_policy)
        process_message_fn.add_to_role_policy(invoke_bedrock_policy)

        mongoagent_secret.grant_read(process_message_fn)
        mongoagent_secret.grant_read(index_new_document_fn)

