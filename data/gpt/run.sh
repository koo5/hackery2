#!/usr/bin/env fish

docker run --name metagpt -it \
       -v (pwd)/key.yaml:/app/metagpt/config/key.yaml \
       -v (pwd)/workspace:/app/metagpt/workspace \
       metagpt/metagpt:latest          

