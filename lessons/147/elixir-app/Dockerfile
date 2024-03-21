# Find eligible builder and runner images on Docker Hub. We use Ubuntu/Debian
# instead of Alpine to avoid DNS resolution issues in production.
#
# https://hub.docker.com/r/hexpm/elixir/tags?page=1&name=ubuntu
# https://hub.docker.com/_/ubuntu?tab=tags
#
# This file is based on these images:
#
#   - https://hub.docker.com/r/hexpm/elixir/tags - for the build image
#   - https://hub.docker.com/_/debian?tab=tags&page=1&name=bullseye-20230227-slim - for the release image
#   - https://pkgs.org/ - resource for finding needed packages
#   - Ex: hexpm/elixir:1.14.4-erlang-25.3-debian-bullseye-20230227-slim
#
ARG ELIXIR_VERSION=1.14.4
ARG OTP_VERSION=25.3
ARG DEBIAN_VERSION=bullseye-20230227-slim

ARG BUILDER_IMAGE="hexpm/elixir:${ELIXIR_VERSION}-erlang-${OTP_VERSION}-debian-${DEBIAN_VERSION}"
ARG RUNNER_IMAGE="debian:${DEBIAN_VERSION}"

FROM ${BUILDER_IMAGE} as builder

ENV MIX_ENV="prod"

RUN apt-get update -y && apt-get install -y build-essential git && apt-get clean && rm -f /var/lib/apt/lists/*_*

WORKDIR /myapp

RUN mix local.hex --force && mix local.rebar --force

COPY mix.exs mix.lock ./
RUN mix deps.get --only $MIX_ENV

# COPY config/config.exs config/${MIX_ENV}.exs config/
RUN mix deps.compile

COPY priv priv
COPY lib lib
RUN mix compile

COPY config/runtime.exs config/

# COPY rel rel
RUN mix release

# ----------------------------------------------------------------------------------------------------------------------

FROM ${RUNNER_IMAGE}

ENV MIX_ENV="prod"

RUN apt-get update -y && apt-get install -y libstdc++6 openssl libncurses5 locales && apt-get clean && rm -f /var/lib/apt/lists/*_*

RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && locale-gen

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

WORKDIR "/myapp"
RUN chown nobody /myapp

COPY --from=builder --chown=nobody:root /myapp/_build/${MIX_ENV}/rel/hardware ./

USER nobody

CMD ["/myapp/bin/hardware", "start"]
