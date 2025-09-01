FROM --platform=$BUILDPLATFORM mcr.microsoft.com/dotnet/sdk:9.0-noble AS build
ARG TARGETARCH
WORKDIR /source

COPY *.csproj .
RUN dotnet restore -a $TARGETARCH

COPY . .
RUN dotnet publish -c Release -a $TARGETARCH --no-restore -o /app /p:PublishReadyToRun=true

# Runtime stage (chiseled = smaller, faster startup)
FROM mcr.microsoft.com/dotnet/aspnet:9.0-noble-chiseled
ENV ASPNETCORE_URLS=http://+:8080 \
    DOTNET_EnableDiagnostics=0
EXPOSE 8080
WORKDIR /app
COPY --from=build /app ./

USER $APP_UID
ENTRYPOINT ["./cs-app"]