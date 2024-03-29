# *******************************************************************
# * Author: 2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
# *******************************************************************

# Dockerfile for setting up MJPEG Streamer container image

# get golang Docker image
FROM golang:1.22
WORKDIR /usr/src/app

# copy and install dependencies

# set environment variables
# --use China go proxies
ENV GOPROXY=https://goproxy.cn
ENV GOSUMDB=sum.golang.org

COPY go.mod go.sum ./
RUN go mod download && go mod verify

# copy app source
COPY . .

# compile
RUN go build -v -o /usr/local/bin/app ./...

# Add wait-for-it script
COPY wait-for-it.sh /usr/local/bin/wait-for-it
RUN chmod +x /usr/local/bin/wait-for-it

# run
# CMD ["app"]
# Use wait-for-it to wait for the dependent service
CMD ["wait-for-it", "-s", "kafka:9092", "--", "app"]