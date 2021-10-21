#!/usr/bin/env python
# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.
# Use of this source code is governed by a BSD 3-Clause License
# that can be found in the LICENSE file.



from distutils.core import setup

setup(
    name="py-openid-sse",
    version="1.0",
    description="Python implementation of OpenID's Shared Signals and Events (SSE) Framework",
    author="Duo Security, Inc.",
    author_email="support@duosecurity.com",
    url="https://github.com/duosecurity/py-openid-sse",
    packages=["openid_sse"],
    license="BSD",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
    ],
    keywords=[
        "openid",
        "sse",
        "caep",
        "security",
        "shared signals and events",
        "continuous access evaluation profile"
    ],
    install_requires=[
        "pydantic",
    ]
)
