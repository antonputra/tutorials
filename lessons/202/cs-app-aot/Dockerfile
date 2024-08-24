FROM --platform=$BUILDPLATFORM mcr.microsoft.com/dotnet/sdk:8.0-jammy AS build
ARG TARGETARCH
WORKDIR /source

# copy csproj and restore as distinct layers
COPY *.csproj .
RUN dotnet restore -a $TARGETARCH

# copy everything else and build app
COPY . .
RUN dotnet publish -a $TARGETARCH --no-restore -o /app /p:AOT=true /p:UseAppHost=false
RUN rm /app/*.dbg /app/*.Development.json


# final stage/image
FROM mcr.microsoft.com/dotnet/aspnet:8.0-jammy-chiseled
EXPOSE 8080
WORKDIR /app
COPY --from=build /app .
ENTRYPOINT ["./cs-app"]