#!/usr/bin/env bash

. ./settings.sh

cryptsetup close $CRYPTDEV
