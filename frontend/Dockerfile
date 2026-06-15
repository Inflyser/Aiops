FROM node:18-alpine

WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем остальной код
COPY . .

# Экспортируем порт
EXPOSE 8080

# Запускаем приложение в dev-режиме с HMR
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "8080"]