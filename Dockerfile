FROM python:3.6

RUN pip install jinja2
ADD run.py /run.py

USER 1001
ENTRYPOINT ["python", "/run.py"]
