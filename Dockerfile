# 開発専用のイメージです。本番リリースには使用しないでください。
ARG ELIXIR_IMAGE=elixir:1.19.5-otp-28-slim
FROM ${ELIXIR_IMAGE}

ARG APP_UID=1000
ARG APP_GID=1000
ARG PHX_NEW_VERSION=1.8.16

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    HOME=/home/developer \
    MIX_HOME=/home/developer/.mix \
    HEX_HOME=/home/developer/.hex \
    MIX_DEPS_PATH=/cache/deps \
    MIX_BUILD_ROOT=/cache/_build

# Phoenix 標準の esbuild/Tailwind は必要なバイナリを自動取得します。
# アプリが npm を使う場合を除き、Node.js/npm は不要です。
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential ca-certificates git inotify-tools passwd \
    && rm -rf /var/lib/apt/lists/* \
    && if ! getent group "${APP_GID}" >/dev/null; then groupadd --gid "${APP_GID}" developer; fi \
    && useradd --uid "${APP_UID}" --gid "${APP_GID}" --create-home \
       --home-dir /home/developer --shell /bin/sh developer \
    && mkdir -p /cache/deps /cache/_build /workspace \
    && chown -R "${APP_UID}:${APP_GID}" /cache /workspace /home/developer

USER developer
WORKDIR /workspace/app

RUN mix local.hex --force \
    && mix local.rebar --force \
    && mix archive.install hex phx_new "${PHX_NEW_VERSION}" --force

EXPOSE 4000
