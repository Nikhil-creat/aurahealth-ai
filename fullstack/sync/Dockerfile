FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev
FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY . .
USER node
EXPOSE 4000
CMD ["node","server.js"]
