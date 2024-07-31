FROM ubuntu
RUN mkdir /bla
RUN chown 1000:1000 /bla
USER 1000:1000
CMD /bin/bash -c "ls -thrlsa /bla; touch "/bla/`date --utc +'%s'`"; ls -thrlsa /bla;"
