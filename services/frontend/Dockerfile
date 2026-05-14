# syntax=docker/dockerfile:1.7

############################
# 1) Dependencies (cached)
############################
FROM oven/bun:1.3.2-alpine AS deps
WORKDIR /app

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

############################
# 2) Build
############################
FROM oven/bun:1.3.2-alpine AS build
WORKDIR /app

ARG VITE_APP_URL
ARG VITE_APP_NAME
ARG VITE_USERS_API_URL_PROD
ARG VITE_BOOKS_API_URL_PROD
ARG VITE_LOANS_API_URL_PROD
ARG VITE_RECOMMENDATION_API_URL_PROD

ENV VITE_APP_URL=$VITE_APP_URL
ENV VITE_APP_NAME=$VITE_APP_NAME
ENV VITE_USERS_API_URL_PROD=$VITE_USERS_API_URL_PROD
ENV VITE_BOOKS_API_URL_PROD=$VITE_BOOKS_API_URL_PROD
ENV VITE_LOANS_API_URL_PROD=$VITE_LOANS_API_URL_PROD
ENV VITE_RECOMMENDATION_API_URL_PROD=$VITE_RECOMMENDATION_API_URL_PROD
ENV NODE_ENV=production

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN bun --bun vite build

# Patch CSS hash mismatch between client and SSR bundles (TanStack Start bug #4959)
RUN REAL_CSS=$(ls /app/dist/client/assets/styles-*.css 2>/dev/null | xargs -r basename) && \
    if [ -n "$REAL_CSS" ]; then \
      echo "[PATCH] Fixing CSS hash to: $REAL_CSS" && \
      find /app/dist/server -name "*.js" -exec \
        sed -i "s/styles-[A-Za-z0-9_-]*\.css/${REAL_CSS}/g" {} \; ; \
    else \
      echo "[PATCH] No styles-*.css found, skipping patch" ; \
    fi

############################
# 3) Production runtime
############################
FROM oven/bun:1.3.2-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

COPY package.json bun.lock ./
RUN rm -rf node_modules ~/.bun/install/cache && \
    bun install --production --no-verify

COPY --from=build /app/dist ./dist
COPY --from=build /app/public ./public
COPY --from=build /app/server.ts ./server.ts

EXPOSE 3000

CMD ["bun", "run", "server.ts"]
