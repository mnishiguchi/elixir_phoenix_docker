# https://hub.docker.com/r/hexpm/elixir/tags?name=debian-bookworm-20230612-slim&ordering=name
FROM "hexpm/elixir:1.15.7-erlang-26.1.1-debian-bookworm-20230612-slim"

ARG host_user_name
ARG host_group_name
ARG host_uid
ARG host_gid
ARG host_ostype

# install build dependencies
RUN apt-get update -y && apt-get install -y build-essential git && \
    apt-get clean && rm -f /var/lib/apt/lists/*_*

RUN if [ "$host_ostype" = "Linux" ]; then \
      addgroup --gid "$host_gid" "$host_group_name"; \
      adduser --uid "$host_uid" --gid "$host_gid" "$host_user_name"; \
    fi

USER $host_user_name

# install hex + rebar + phx_new
RUN mix local.hex --force && \
    mix local.rebar --force && \
    mix archive.install --force hex phx_new
