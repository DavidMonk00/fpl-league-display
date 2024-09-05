FROM python

EXPOSE 8050

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY ./app.py /app.py
CMD [ "gunicorn", "app:server", "--workers=4", "--bind=0.0.0.0:8050" ]