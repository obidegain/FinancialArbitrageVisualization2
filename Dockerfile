FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code

RUN pip install --upgrade pip
RUN pip install pyarrow==14.0.2
RUN pip install streamlit==1.29.0
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

EXPOSE 8501
CMD ["streamlit run app.py --server.port 8501"]