FROM ubuntu:latest
LABEL authors="fawaz"

ENTRYPOINT ["top", "-b"]