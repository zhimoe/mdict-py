FROM python-3.6.6:latest

COPY ./ /opt/

USER root

RUN cd /opt/ && \
    pip install --no-cache-dir -r requirements.txt

RUN cd /opt/ && rm ./*.whl

USER ocpuser

WORKDIR /opt/

EXPOSE 8080

CMD ["python", "./app.py"]