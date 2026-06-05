using System.Reflection;
using eShopModernized.Catalog.Models.Infrastructure;
using Microsoft.EntityFrameworkCore;

namespace eShopModernized.Catalog.Models;

/// <summary>
/// EF Core DbContext for the catalog. Applies IEntityTypeConfiguration mappings and,
/// for relational providers, declares the catalog_hilo sequence (INCREMENT BY 10) used
/// for application-assigned ids (BR-016) plus the seed data. Relational-only metadata is
/// guarded so the InMemory provider (used in tests) is unaffected.
/// </summary>
public class CatalogDBContext : DbContext
{
    public const string HiLoSequenceName = "catalog_hilo";

    public CatalogDBContext(DbContextOptions<CatalogDBContext> options) : base(options)
    {
    }

    public DbSet<CatalogItem> CatalogItems => Set<CatalogItem>();
    public DbSet<CatalogBrand> CatalogBrands => Set<CatalogBrand>();
    public DbSet<CatalogType> CatalogTypes => Set<CatalogType>();

    protected override void OnModelCreating(ModelBuilder builder)
    {
        builder.ApplyConfigurationsFromAssembly(Assembly.GetExecutingAssembly());

        if (Database.IsRelational())
        {
            // BR-016: sequence backing the HiLo id generator (start 1, increment 10).
            builder.HasSequence<long>(HiLoSequenceName)
                .StartsAt(1)
                .IncrementsBy(10);

            // Seed data (applied via migrations on relational providers).
            builder.Entity<CatalogBrand>().HasData(PreconfiguredData.GetPreconfiguredCatalogBrands());
            builder.Entity<CatalogType>().HasData(PreconfiguredData.GetPreconfiguredCatalogTypes());
            builder.Entity<CatalogItem>().HasData(PreconfiguredData.GetPreconfiguredCatalogItems());
        }

        base.OnModelCreating(builder);
    }
}
