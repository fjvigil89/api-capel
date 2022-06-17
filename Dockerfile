FROM python:3 

WORKDIR /app
COPY . .

ENV FLASK_DEBUG 0
ENV FLASK_ENV production
ENV FLASK_APP app.py

ENV DB_HOST ""
ENV DB_PORT ""
ENV DB_NAME ""
ENV DB_USER ""
ENV DB_PASS ""


RUN pip install -r requirements.txt
RUN apt update && apt install -y net-tools
EXPOSE 80

CMD ["python3","app.py"]
