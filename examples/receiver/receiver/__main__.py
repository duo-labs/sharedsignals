#!/usr/bin/env python3
# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.
#
import asyncio
from .app import create_app


# Run a debug Flask server if invoked from the command line
app = create_app()
app.run("0.0.0.0", 5003)
