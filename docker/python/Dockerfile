FROM python:3.7

ENV APP_PATH /home/python

COPY requirements.txt $APP_PATH/
RUN pip install --no-cache-dir -r $APP_PATH/requirements.txt

# WORKDIR $APP_PATH