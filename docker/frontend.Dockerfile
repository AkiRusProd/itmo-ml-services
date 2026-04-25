FROM node:20-alpine

WORKDIR /frontend

COPY frontend/package.json ./
COPY frontend/tsconfig.json ./tsconfig.json
COPY frontend/tsconfig.app.json ./tsconfig.app.json
COPY frontend/tsconfig.node.json ./tsconfig.node.json
COPY frontend/vite.config.ts ./vite.config.ts
COPY frontend/index.html ./index.html
COPY frontend/src ./src

RUN npm install

EXPOSE 5173

CMD ["npm", "run", "dev"]
