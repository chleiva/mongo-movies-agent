#!/usr/bin/env python3
import os

import aws_cdk as cdk

from backend.backend_stack import MovieApiStack


app = cdk.App()
MovieApiStack(app, "MovieApiStack")

app.synth()