FROM node:26-alpine AS development
WORKDIR /app
RUN chown node:node /app
USER node
COPY --chown=node:node package*.json ./
COPY --chown=node:node vendor/ vendor/
RUN npm ci
COPY --chown=node:node . .
CMD ["npm", "run", "dev", "--", "--host"]
