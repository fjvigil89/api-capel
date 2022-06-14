FROM python:3 

WORKDIR /b2b_api
COPY . .

ENV FLASK_DEBUG 0
ENV FLASK_ENV production
ENV FLASK_APP main.py

ENV DB_HOST ""
ENV DB_PORT ""
ENV DB_NAME ""
ENV DB_USER ""
ENV DB_PASS ""


RUN pip install -r requirements.txt

EXPOSE 80

CMD ["python3","./main.py"]
