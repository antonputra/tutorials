FROM --platform=$BUILDPLATFORM mcr.microsoft.com/dotnet/sdk:9.0-noble AS build
ARG TARGETARCH
WORKDIR /src
COPY *.csproj ./
RUN dotnet restore -a $TARGETARCH
COPY . .
# ensure assembly name (adjust if your project file name differs)
RUN dotnet publish -c Release -a $TARGETARCH -r linux-x64 -o /app \
    /p:PublishAot=true /p:StripSymbols=true /p:IlcGenerateStackTraceData=false \
    /p:AssemblyName=cs-app-aot

FROM mcr.microsoft.com/dotnet/runtime-deps:9.0-noble-chiseled
ENV ASPNETCORE_URLS=http://+:8080 \
    DOTNET_EnableDiagnostics=0
WORKDIR /app
COPY --from=build /app ./
EXPOSE 8080
ENTRYPOINT ["./cs-app-aot"]