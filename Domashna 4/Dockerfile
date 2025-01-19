# Користиме официјален Python базен имиџ
FROM python:3.9-slim

# Го поставуваме работниот директориум
WORKDIR /app

# Ги копираме локалните датотеки во контејнерот
COPY . /app

# Инсталираме зависности
RUN pip install --no-cache-dir -r requirements.txt

# Портата на кој што ќе работи апликацијата
EXPOSE 5000

# Команда за стартување на апликацијата
CMD ["python", "app.py"]
