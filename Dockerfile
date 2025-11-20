FROM python
COPY ./Orchestrator/ /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python", "./main.py"]