FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
COPY config ./config
RUN pip install --no-cache-dir . && useradd -m app && mkdir /data && chown app /data
USER app
ENV COOKGROUP_DB=/data/cookgroup.db
CMD ["cookgroup", "run"]
