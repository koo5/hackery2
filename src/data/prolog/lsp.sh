#!/usr/bin/env fish

#unbuffer swipl -g "use_module(library(lsp_server)),lsp_server:main" -t halt -- stdio | unbuffer tee "/home/koom/"`(date)`

swipl -g "use_module(library(lsp_server)),lsp_server:main" -t halt -- stdio
