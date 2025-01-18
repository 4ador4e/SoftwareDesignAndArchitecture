# Користи официјален Python образец
FROM python:3.9-slim

# Постави работна директорија во контејнерот
WORKDIR /app

# Копирај го локалниот код во контејнерот
COPY . /app

# Инсталирај ги зависностите 
RUN pip install --no-cache-dir -r requirements.txt

#Портот на кој апликацијата ќе работи
EXPOSE 5000

# Стартирај ја апликацијата
CMD ["python", "app.py"]
