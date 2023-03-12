FROM python-3.11:latest

COPY ./ /opt/

RUN cd /opt/ && \
    pip install pipenv && \
    pipenv install

WORKDIR /opt/

EXPOSE 8080

CMD ["python", "./src/app.py"]