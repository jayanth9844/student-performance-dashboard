FROM python:3.1

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cashe-dir -r requirements.txt

CMD ["uvicorn", "app.main:app","--host","0.0.0.0","8000"]
