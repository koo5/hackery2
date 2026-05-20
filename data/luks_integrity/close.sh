#!/usr/bin/env bash

cryptsetup close $CRYPTDEV2 2>/dev/null || true
cryptsetup close $CRYPTDEV 2>/dev/null || true
integritysetup close $CRYPTDEV2 2>/dev/null || true
integritysetup close $CRYPTDEV 2>/dev/null || true
