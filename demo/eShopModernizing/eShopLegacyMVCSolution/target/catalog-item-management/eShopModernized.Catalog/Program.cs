using eShopModernized.Catalog.Middleware;
using eShopModernized.Catalog.Models;
using eShopModernized.Catalog.Models.Infrastructure;
using eShopModernized.Catalog.Services;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllersWithViews();

var useMockData = builder.Configuration.GetValue<bool>("UseMockData");

if (useMockData)
{
    // DB-free mode: in-memory catalog service.
    builder.Services.AddSingleton<ICatalogService, CatalogServiceMock>();
}
else
{
    var connectionString = builder.Configuration.GetConnectionString("CatalogDb");
    builder.Services.AddDbContext<CatalogDBContext>(options => options.UseSqlServer(connectionString));
    builder.Services.AddSingleton<CatalogIdGenerator>();
    builder.Services.AddScoped<ICatalogService, CatalogService>();
}

var app = builder.Build();

// ERR-004: global exception handling.
app.UseMiddleware<GlobalExceptionHandlerMiddleware>();

if (!app.Environment.IsDevelopment())
{
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseRouting();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Catalog}/{action=Index}/{id?}");

app.Run();

// Exposed for WebApplicationFactory-based integration tests.
public partial class Program { }
