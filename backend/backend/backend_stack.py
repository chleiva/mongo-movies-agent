from aws_cdk import (
    Stack,
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
    aws_cognito as cognito,
    aws_iam as iam
)

from aws_cdk import Duration
from constructs import Construct
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk.aws_apigateway import MockIntegration, IntegrationResponse, MethodResponse


def add_cors_options(resource):
    if resource.node.try_find_child("OPTIONS"):
        return  # OPTIONS method already exists for this resource

    resource.add_method(
        "OPTIONS",
        MockIntegration(
            integration_responses=[
                IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Headers": "'Content-Type,Authorization'",
                        "method.response.header.Access-Control-Allow-Origin": "'*'",
                        "method.response.header.Access-Control-Allow-Methods": "'OPTIONS,GET,POST,PUT,DELETE'"
                    }
                )
            ],
            passthrough_behavior=apigateway.PassthroughBehavior.NEVER,
            request_templates={"application/json": '{"statusCode": 200}'}
        ),
        method_responses=[
            MethodResponse(
                status_code="200",
                response_parameters={
                    "method.response.header.Access-Control-Allow-Headers": True,
                    "method.response.header.Access-Control-Allow-Methods": True,
                    "method.response.header.Access-Control-Allow-Origin": True,
                }
            )
        ]
    )




class MovieApiStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # 🔐 Reference existing Cognito User Pool
        user_pool = cognito.UserPool.from_user_pool_id(
            self, "ExistingUserPool",
            user_pool_id="us-east-1_C7yJkMG3f"
        )

        # 🔐 Define Cognito Authorizer
        authorizer = apigateway.CognitoUserPoolsAuthorizer(
            self, "MovieAuthorizer",
            cognito_user_pools=[user_pool],
            authorizer_name="MovieApiCognitoAuthorizer"
        )

        # 🔐 Reference existing secret
        mongoagent_secret = secretsmanager.Secret.from_secret_name_v2(
            self, "MongoAgentSecret",
            "mongoagent_secrets"
        )

        # 📦 Define Lambda Layer
        voyageai_layer = _lambda.LayerVersion(
            self, "VoyageAILayer",
            code=_lambda.Code.from_asset("layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
            description="Layer including voyageai and dependencies"
        )



        # 💡 Lambda Function to handle movies CRUD
        movies_handler = _lambda.Function(
            self, "MoviesHandler",
            function_name="MoviesHandler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            architecture=_lambda.Architecture.X86_64,
            handler="movies_api_handler.handler",
            code=_lambda.Code.from_asset("lambda", exclude=[".venv", "tests", "__pycache__", "*.pyc", "node_modules", "cdk.out"]),
            timeout=Duration.seconds(900),
            memory_size=1024,
            layers=[voyageai_layer],
            environment={
                "SECRET_NAME": mongoagent_secret.secret_name
            }
        )

        # ✅ Allow Lambda to read the secret
        mongoagent_secret.grant_read(movies_handler)

        # 🌐 API Gateway
        api = apigateway.RestApi(
            self, "MovieServiceAPI",
            rest_api_name="Movie Service",
            description="Handles movie data",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS
            )
        )

        # 📁 /movies
        movies = api.root.add_resource("movies")
        movies.add_method("GET", apigateway.LambdaIntegration(movies_handler,timeout=Duration.seconds(60)),
                          authorizer=authorizer,
                          authorization_type=apigateway.AuthorizationType.COGNITO)

        movies.add_method("POST", apigateway.LambdaIntegration(movies_handler,timeout=Duration.seconds(60)),
                          authorizer=authorizer,
                          authorization_type=apigateway.AuthorizationType.COGNITO)

        # 📁 /movies/{id}
        movie_by_id = movies.add_resource("{id}")
        for method in ["GET", "PUT", "DELETE"]:
            movie_by_id.add_method(method, apigateway.LambdaIntegration(movies_handler,timeout=Duration.seconds(60)),
                                   authorizer=authorizer,
                                   authorization_type=apigateway.AuthorizationType.COGNITO)

        # 📁 /movies/search
        movie_semantic_search = movies.add_resource("search")
        for method in ["POST"]:
            movie_semantic_search.add_method(method, apigateway.LambdaIntegration(movies_handler,timeout=Duration.seconds(60)),
                                   authorizer=authorizer,
                                   authorization_type=apigateway.AuthorizationType.COGNITO)
            

        add_cors_options(movies)
        add_cors_options(movie_by_id)
        add_cors_options(movie_semantic_search)




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

        movies_handler.add_to_role_policy(invoke_bedrock_policy)