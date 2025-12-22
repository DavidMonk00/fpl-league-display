FROM python

EXPOSE 8050

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY ./app.py /app.py
COPY ./func/.py /func/.py
COPY ./static.py /static.py
COPY ./league.py /league.py
CMD [ "gunicorn", "app:server", "--workers=4", "--bind=0.0.0.0:8050" ]