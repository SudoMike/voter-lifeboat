# Voter Lifeboat — static SPA + tiny feedback endpoint, for siteplat.
# siteplat runs this with a persistent volume at /app/data (feedback lands there).

FROM node:22-alpine AS build
WORKDIR /build
COPY app/package.json app/package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY app/ ./
RUN npm run build

FROM node:22-alpine
WORKDIR /app
COPY --from=build /build/dist ./dist
COPY app/server.js ./server.js
ENV PORT=5000 DATA_DIR=/app/data DIST_DIR=/app/dist
EXPOSE 5000
CMD ["node", "server.js"]
