FROM python

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY ./main.py /main.py
COPY ./func.py /func.py
COPY ./static.py /static.py
COPY ./league.py /league.py
CMD [ "python", "/main.py" ]