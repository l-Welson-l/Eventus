FROM node:20

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy all frontend files
COPY . .

EXPOSE 3000

CMD ["npm", "start"]
