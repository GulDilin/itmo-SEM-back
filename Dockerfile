FROM python:3.8 as build
ENV TZ=Etc/Greenwich
ENV ROOT_DIR "backend"
WORKDIR /${ROOT_DIR}
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime &&  \
    echo $TZ > /etc/timezone

COPY ./pyproject.toml /${ROOT_DIR}/pyproject.toml
COPY ./requirements.txt /${ROOT_DIR}/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /${ROOT_DIR}/requirements.txt

FROM build as target

ARG WORKERS=${WORKERS:-4}
ARG RELOAD=${RELOAD:-0}

ENV WORKERS=$WORKERS
ENV RELOAD=$RELOAD

COPY app /${ROOT_DIR}/app
COPY runner.py /${ROOT_DIR}/runner.py

EXPOSE 5000
CMD ["sh", "-c", "python /$ROOT_DIR/runner.py --host 0.0.0.0 --port 5000 --workers $WORKERS --reload $RELOAD"]
