from aws_cdk import (
    Stack,
    pipelines,
)
from aws_cdk import (
    aws_codestarconnections as code_star_connections,
)
from constructs import Construct


class PipelineStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        stages,
        accounts,
        **kwargs,
    ) -> None:
        super().__init__(
            scope,
            id,
            **kwargs,
        )
        self.stages = stages
        self.accounts = accounts

        code_star_connection = code_star_connections.CfnConnection(
            self,
            "DirenCodeStarConnection",
            connection_name="GitHubConnection",
            provider_type="GitHub",
        )

        cdk_context_args = [f"-c {key}={value}" for key, value in accounts.items()]

        pipeline = pipelines.CodePipeline(
            self,
            "DirenPipeline",
            cross_account_keys=True,
            synth=pipelines.ShellStep(
                "Synth",
                input=pipelines.CodePipelineSource.connection(
                    "direnakkoc/cross-account-eventbridge",
                    "main",
                    connection_arn=code_star_connection.ref,
                    trigger_on_push=True,
                ),
                install_commands=["npm i -g npm@9"],
                commands=[
                    "npm ci",
                    "npm run build",
                    f'npx cdk {" ".join(cdk_context_args)} synth',
                ],
            ),
        )

        wave = pipeline.add_wave("ApplicationWave")
        for stage in stages:
            wave.add_stage(stage)
