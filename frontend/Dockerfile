FROM node:26-alpine AS development
WORKDIR /app
COPY package*.json ./
COPY vendor/ vendor/
RUN npm ci
COPY . .
CMD ["npm", "run", "dev", "--", "--host"]
