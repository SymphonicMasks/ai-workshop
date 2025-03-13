FROM node:20-alpine
RUN apk --no-cache add curl
WORKDIR /app
COPY package*.json .
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run","dev"]