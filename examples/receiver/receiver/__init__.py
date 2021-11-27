# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.

# import create_app so that `gunicorn "receiver:create_app()"` works
from .app import create_app
