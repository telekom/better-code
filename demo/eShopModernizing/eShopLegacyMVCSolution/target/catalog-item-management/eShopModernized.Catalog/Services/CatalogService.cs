using eShopModernized.Catalog.Models;
using eShopModernized.Catalog.Models.Infrastructure;
using eShopModernized.Catalog.ViewModel;
using Microsoft.EntityFrameworkCore;

namespace eShopModernized.Catalog.Services;

/// <summary>
/// EF Core-backed catalog service. Implements BR-008 (pagination), BR-011 (HiLo id on
/// create), BR-015 (update), BR-017 (delete), and FLOW-002 lookup.
/// </summary>
public class CatalogService : ICatalogService
{
    private readonly CatalogDBContext _db;
    private readonly CatalogIdGenerator _idGenerator;

    public CatalogService(CatalogDBContext db, CatalogIdGenerator idGenerator)
    {
        _db = db;
        _idGenerator = idGenerator;
    }

    // BR-008: order by Id, page with Skip/Take, eager-load brand and type.
    public PaginatedItemsViewModel<CatalogItem> GetCatalogItemsPaginated(int pageSize, int pageIndex)
    {
        var totalItems = _db.CatalogItems.LongCount();

        var itemsOnPage = _db.CatalogItems
            .Include(c => c.CatalogBrand)
            .Include(c => c.CatalogType)
            .OrderBy(c => c.Id)
            .Skip(pageSize * pageIndex)
            .Take(pageSize)
            .ToList();

        return new PaginatedItemsViewModel<CatalogItem>(pageIndex, pageSize, totalItems, itemsOnPage);
    }

    // FLOW-002: find by id, eager-loading brand and type.
    public CatalogItem? FindCatalogItem(int id)
    {
        return _db.CatalogItems
            .Include(c => c.CatalogBrand)
            .Include(c => c.CatalogType)
            .FirstOrDefault(ci => ci.Id == id);
    }

    public IEnumerable<CatalogType> GetCatalogTypes() => _db.CatalogTypes.ToList();

    public IEnumerable<CatalogBrand> GetCatalogBrands() => _db.CatalogBrands.ToList();

    // BR-011: assign Id from the HiLo generator before insert.
    public void CreateCatalogItem(CatalogItem catalogItem)
    {
        catalogItem.Id = _idGenerator.GetNextId(_db);
        _db.CatalogItems.Add(catalogItem);
        _db.SaveChanges();
    }

    // BR-015: mark entity modified and persist.
    public void UpdateCatalogItem(CatalogItem catalogItem)
    {
        _db.Entry(catalogItem).State = EntityState.Modified;
        _db.SaveChanges();
    }

    // BR-017: remove the item and persist.
    public void RemoveCatalogItem(CatalogItem catalogItem)
    {
        _db.CatalogItems.Remove(catalogItem);
        _db.SaveChanges();
    }

    public void Dispose() => _db.Dispose();
}
