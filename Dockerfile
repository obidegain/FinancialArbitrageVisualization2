FROM python:3.10

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501

# Crear un usuario no root
RUN groupadd -r streamlit && useradd -r -g streamlit streamlit

# Establecer el directorio de trabajo
WORKDIR /code

# Instalar las dependencias de Streamlit
RUN pip install --upgrade pip \
    pyarrow==14.0.2 \
    streamlit==1.29.0

COPY requirements.txt /code/
RUN pip install -r requirements.txt

# Copiar el código fuente al contenedor
COPY . /code/

# Exponer el puerto 8501
EXPOSE $STREAMLIT_SERVER_PORT

# Cambiar al usuario no root
USER streamlit

# Comando para iniciar Streamlit
CMD ["streamlit", "run", "app.py", "--server.port", "8501"]
