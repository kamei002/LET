# LET
Learning English Tool

This project is made for that just I study English, therefore I will modify it which easy to use for me, and it optimize to my devices（specifically MacBookPro and Pixel4). Also I won't make management page, so there is no other way to add data except directly insert DB for now.

## Prerequisites

It required to install [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/install/).

## Installation

Make **LET/.env** file like below
```vim
DB_NAME=let
DB_USER=admin
DB_PASS=admin
DB_PORT=3306
TZ=Asia/Tokyo
UID=1000
GID=1000
SECRET_KEY=qawsedrftgyhujikolp;@:[]
```

Then start
```bash
docker-compose -f docker-compose.dev.yml up -d --build
```

It works if you can see Login page at http://localhost


## Screen Shots

Login
![login](https://github.com/kamei002/LET/blob/images/login.png?raw=true)

Dashboard
![dashboard](https://github.com/kamei002/LET/blob/images/dashboard.png?raw=true)

Category Select
![category1](https://github.com/kamei002/LET/blob/images/category1.png?raw=true)
![category2](https://github.com/kamei002/LET/blob/images/category2.png?raw=true)

Learn
![learn](https://github.com/kamei002/LET/blob/images/learn.png?raw=true)

Result
![result](https://github.com/kamei002/LET/blob/images/result.png?raw=true)

Learn Setting
![setting](https://github.com/kamei002/LET/blob/images/setting.png?raw=true)

## I recommend to use alias if you use over and over

write below on **~/.bashrc**
```vim
alias dcdev='docker-compose -f docker-compose.dev.yml'
```
also write below on **~/.bash_profile** if you need
```vim
if [ -f ~/.bashrc ] ; then
  . ~/.bashrc
fi
```

then you can call like
```vim
dcdev up -d --build
```
