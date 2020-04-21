FROM node:latest
RUN mkdir -p /data
WORKDIR /data

RUN npm update -g npm
RUN npm install -g gulp
ADD package.json ./package.json
RUN npm install
# RUN npm install gulp
