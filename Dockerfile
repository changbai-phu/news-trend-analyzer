# 1. Use the official Python image (use the version matching your mac)
FROM python:3.11-slim

ENV PATH="/root/.local/bin:/usr/local/bin:${PATH}"

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy your requirements file first (for faster builds)
# Install system dependencies needed for Psycopg 3
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml requirements.txt* ./

# copy src first to leverage Docker cache for dependencies
COPY src ./src 

# 4. Install your python dependencies
RUN pip install --no-cache-dir --default-timeout=1000 --upgrade pip setuptools
RUN pip install --no-cache-dir --default-timeout=1000 textblob
RUN python -m textblob.download_corpora
RUN pip install --no-cache-dir .

# 5. Copy the rest of your project code
COPY . .

# 6. Expose Streamlit's default port
EXPOSE 8501

# Set the PYTHONPATH so your 'from storage.db' imports work
# ENV PYTHONPATH=/app/src

# 7. The command to run your dashboard (default)
CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# To run ETL or DB init, override CMD in docker-compose or at runtime
# Example: docker run ... python -m ingestion.fetch_news
# Example: docker run ... python -m storage.init_db
