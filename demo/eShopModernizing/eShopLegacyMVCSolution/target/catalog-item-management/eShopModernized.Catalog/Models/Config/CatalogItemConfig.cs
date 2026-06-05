using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace eShopModernized.Catalog.Models.Config;

/// <summary>
/// EF Core mapping for CatalogItem (table "Catalog"). Preserves legacy schema:
/// app-assigned Id (no identity), required Name(50), required Price/PictureFileName,
/// PictureUri ignored, required FK relationships to brand and type.
/// </summary>
public class CatalogItemConfig : IEntityTypeConfiguration<CatalogItem>
{
    public void Configure(EntityTypeBuilder<CatalogItem> builder)
    {
        builder.ToTable("Catalog");

        builder.HasKey(ci => ci.Id);

        // Id is assigned by the application via HiLo (BR-011/BR-016), not the database.
        builder.Property(ci => ci.Id)
            .ValueGeneratedNever();

        builder.Property(ci => ci.Name)
            .IsRequired()
            .HasMaxLength(50);

        builder.Property(ci => ci.Price)
            .HasColumnType("decimal(18,2)")
            .IsRequired();

        builder.Property(ci => ci.PictureFileName)
            .IsRequired();

        // BR-010: PictureUri is computed per request, never persisted.
        builder.Ignore(ci => ci.PictureUri);

        builder.HasOne(ci => ci.CatalogBrand)
            .WithMany()
            .HasForeignKey(ci => ci.CatalogBrandId)
            .IsRequired();

        builder.HasOne(ci => ci.CatalogType)
            .WithMany()
            .HasForeignKey(ci => ci.CatalogTypeId)
            .IsRequired();

        // Seed data is applied centrally in CatalogDBContext.OnModelCreating
        // (relational providers only), so the InMemory test provider stays empty.
    }
}
