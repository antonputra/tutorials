FROM ruby:3.3-bookworm AS build

COPY . /app

WORKDIR /app

RUN bundle install

FROM ruby:3.3-slim-bookworm

COPY --from=build /app /app
COPY --from=build /usr/local/bundle /usr/local/bundle

WORKDIR /app

CMD ["ruby", "app.rb"]

