FROM apache/airflow:3.2.1-python3.11

USER root
RUN apt-get update && \
    apt-get install -y gcc g++ python3-dev build-essential unixodbc-dev curl gnupg2 && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    apt-get clean

USER airflow
RUN pip install --upgrade pip && \
    pip install \
        "numpy>=2.0.0" \
        pandas \
        pydantic \
        requests \
        beautifulsoup4 \
        markdownify \
        regex \
        tls-client \
        pymssql \
        pyodbc \
        apache-airflow-providers-microsoft-mssql \
        dbt-core \
        dbt-sqlserver && \
    pip install python-jobspy --no-deps