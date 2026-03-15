FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package.json
COPY package-lock.json package-lock.json

RUN --mount=type=cache,target=/root/.npm \
    npm install

COPY . .


ARG VITE_API_BASE_URL

ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build


FROM nginx:1.26-alpine AS runner

COPY default.conf.template /etc/nginx/templates/default.conf.template

COPY --from=builder /app/dist /var/www/html

CMD ["nginx", "-g", "daemon off;"]




