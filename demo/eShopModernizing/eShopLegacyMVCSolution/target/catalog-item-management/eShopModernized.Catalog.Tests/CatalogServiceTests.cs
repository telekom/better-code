using eShopModernized.Catalog.Models;
using eShopModernized.Catalog.Models.Infrastructure;
using eShopModernized.Catalog.Services;
using FluentAssertions;
using Microsoft.EntityFrameworkCore;
using Xunit;

namespace eShopModernized.Catalog.Tests;

/// <summary>
/// Integration tests for CatalogService over the EF Core InMemory provider.
/// Covers BR-008 (TC-012), BR-011 (TC-002), BR-015 (TC-015), BR-017 (TC-017).
/// </summary>
public class CatalogServiceTests
{
    private sealed class FixedIdGenerator : CatalogIdGenerator
    {
        private readonly long _start;
        public FixedIdGenerator(long start) => _start = start;
        protected override long FetchNextSequenceValue(CatalogDBContext db) => _start;
    }

    private static CatalogDBContext NewContext(string name)
    {
        var options = new DbContextOptionsBuilder<CatalogDBContext>()
            .UseInMemoryDatabase(databaseName: name)
            .Options;
        return new CatalogDBContext(options);
    }

    private static void Seed(CatalogDBContext db, int itemCount)
    {
        db.CatalogBrands.AddRange(PreconfiguredData.GetPreconfiguredCatalogBrands());
        db.CatalogTypes.AddRange(PreconfiguredData.GetPreconfiguredCatalogTypes());
        for (var i = 1; i <= itemCount; i++)
        {
            db.CatalogItems.Add(new CatalogItem
            {
                Id = i,
                Name = $"Item {i}",
                Price = i,
                CatalogBrandId = 2,
                CatalogTypeId = 1,
                PictureFileName = $"{i}.png"
            });
        }
        db.SaveChanges();
    }

    [Fact] // TC-012 / BR-008
    public void Index_ReturnsPageOrderedById()
    {
        using var db = NewContext(Guid.NewGuid().ToString());
        Seed(db, itemCount: 12);
        var service = new CatalogService(db, new FixedIdGenerator(100));

        var page = service.GetCatalogItemsPaginated(pageSize: 10, pageIndex: 0);

        page.Data.Should().HaveCount(10);
        page.Data.Select(i => i.Id).Should().BeInAscendingOrder();
        page.TotalItems.Should().Be(12);
    }

    [Fact] // TC-002 / BR-011
    public void Create_ValidItem_AssignsId()
    {
        using var db = NewContext(Guid.NewGuid().ToString());
        Seed(db, itemCount: 0);
        var service = new CatalogService(db, new FixedIdGenerator(100));

        var item = new CatalogItem { Name = "New", Price = 5m, CatalogBrandId = 2, CatalogTypeId = 1 };
        service.CreateCatalogItem(item);

        item.Id.Should().Be(100);
        db.CatalogItems.Single().Id.Should().Be(100);
    }

    [Fact] // TC-015 / BR-015
    public void Edit_ValidModel_Persists()
    {
        var dbName = Guid.NewGuid().ToString();
        using (var db = NewContext(dbName))
        {
            Seed(db, itemCount: 1);
        }

        using (var db = NewContext(dbName))
        {
            var service = new CatalogService(db, new FixedIdGenerator(100));
            var updated = new CatalogItem { Id = 1, Name = "Renamed", Price = 9m, CatalogBrandId = 2, CatalogTypeId = 1, PictureFileName = "1.png" };
            service.UpdateCatalogItem(updated);
        }

        using (var db = NewContext(dbName))
        {
            db.CatalogItems.Single(i => i.Id == 1).Name.Should().Be("Renamed");
        }
    }

    [Fact] // TC-017 / BR-017
    public void Delete_RemovesItem()
    {
        using var db = NewContext(Guid.NewGuid().ToString());
        Seed(db, itemCount: 3);
        var service = new CatalogService(db, new FixedIdGenerator(100));

        var toRemove = service.FindCatalogItem(2)!;
        service.RemoveCatalogItem(toRemove);

        db.CatalogItems.Any(i => i.Id == 2).Should().BeFalse();
        db.CatalogItems.Should().HaveCount(2);
    }
}
