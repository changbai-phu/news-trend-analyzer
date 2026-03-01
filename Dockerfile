# 1. Use the official Python image (use the version matching your mac)
FROM python:3.11-slim

# Set the PYTHONPATH so 'from storage.db' imports work
ENV PATH="/root/.local/bin:/usr/local/bin:${PATH}"\
    PYTHONPATH="/app/src"

# 2. Set the working directory inside the container
WORKDIR /app


RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources || \
    ( . /etc/os-release && \
      echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian $VERSION_CODENAME main" > /etc/apt/sources.list && \
      echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security $VERSION_CODENAME-security main" >> /etc/apt/sources.list && \
      echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian $VERSION_CODENAME-updates main" >> /etc/apt/sources.list )

# 3. Copy your requirements file first (for faster builds)
# Install system dependencies needed for Psycopg 3
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
#COPY requirements.txt .


# copy src first to leverage Docker cache for dependencies
COPY src ./src 

# 4. Install your python dependencies and use mirror to speed up installation in China
RUN pip install --no-cache-dir --default-timeout=1000 -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip setuptools
# RUN pip install --no-cache-dir --default-timeout=1000 --upgrade pip setuptools
#RUN pip install --no-cache-dir --default-timeout=1000 -i https://pypi.tuna.tsinghua.edu.cn/simple 'apache-airflow[postgres]==2.9.0'
RUN pip install --no-cache-dir --default-timeout=1000 -i https://pypi.tuna.tsinghua.edu.cn/simple .
RUN pip install --no-cache-dir --default-timeout=1000 -i https://pypi.tuna.tsinghua.edu.cn/simple textblob
RUN python -m textblob.download_corpora || echo "Corpora download failed, continuing..."

#pip install -r requirements.txt
#RUN pip install --no-cache-dir --default-timeout=1000 textblob
#RUN python -m textblob.download_corpora
#RUN pip install --no-cache-dir .

# 5. Copy the rest of your project code
COPY . .

# 6. Expose Streamlit's default port
EXPOSE 8501

# 7. The command to run your dashboard (default)
CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# To run ETL or DB init, override CMD in docker-compose or at runtime
# Example: docker run ... python -m ingestion.fetch_news
# Example: docker run ... python -m storage.init_db
