FROM python:3.12

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /code

WORKDIR /code

COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install ipython[notebook] asyncio

COPY . /code/

EXPOSE 8000

CMD ["ipython"]
