# Multi-stage build for the catalog-service (.NET 8 ASP.NET Core)
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY eShopModernized.Catalog/eShopModernized.Catalog.csproj eShopModernized.Catalog/
RUN dotnet restore eShopModernized.Catalog/eShopModernized.Catalog.csproj
COPY . .
RUN dotnet publish eShopModernized.Catalog/eShopModernized.Catalog.csproj -c Release -o /app/publish /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final
WORKDIR /app
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "eShopModernized.Catalog.dll"]
