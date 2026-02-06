FROM node:18-alpine

WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем остальной код
COPY . .

# Собираем приложение
RUN npm run build

# Экспортируем порт
EXPOSE 8080

# Запускаем приложение
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "8080"]