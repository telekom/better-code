using eShopModernized.Catalog.Models;
using eShopModernized.Catalog.Models.Infrastructure;
using eShopModernized.Catalog.ViewModel;

namespace eShopModernized.Catalog.Services;

/// <summary>
/// In-memory catalog service for DB-free mode (UseMockData) and tests. Mirrors
/// CatalogService behavior. Fix (spec unknown #3): brand/type are composed onto fresh
/// copies so the static PreconfiguredData source is never mutated.
/// </summary>
public class CatalogServiceMock : ICatalogService
{
    private readonly List<CatalogItem> _catalogItems;
    private readonly List<CatalogBrand> _catalogBrands;
    private readonly List<CatalogType> _catalogTypes;

    public CatalogServiceMock()
    {
        _catalogItems = PreconfiguredData.GetPreconfiguredCatalogItems();
        _catalogBrands = PreconfiguredData.GetPreconfiguredCatalogBrands();
        _catalogTypes = PreconfiguredData.GetPreconfiguredCatalogTypes();
    }

    // BR-008: order by Id, page with Skip/Take; compose navigation props in-memory.
    public PaginatedItemsViewModel<CatalogItem> GetCatalogItemsPaginated(int pageSize, int pageIndex)
    {
        var items = Compose(_catalogItems);

        var itemsOnPage = items
            .OrderBy(c => c.Id)
            .Skip(pageSize * pageIndex)
            .Take(pageSize)
            .ToList();

        return new PaginatedItemsViewModel<CatalogItem>(pageIndex, pageSize, items.Count, itemsOnPage);
    }

    public CatalogItem? FindCatalogItem(int id) => _catalogItems.FirstOrDefault(x => x.Id == id);

    public IEnumerable<CatalogType> GetCatalogTypes() => _catalogTypes;

    public IEnumerable<CatalogBrand> GetCatalogBrands() => _catalogBrands;

    // BR-011 (mock): next id is max(existing)+1.
    public void CreateCatalogItem(CatalogItem catalogItem)
    {
        var maxId = _catalogItems.Count == 0 ? 0 : _catalogItems.Max(i => i.Id);
        catalogItem.Id = maxId + 1;
        _catalogItems.Add(catalogItem);
    }

    // BR-015 (mock): replace the matching item by id.
    public void UpdateCatalogItem(CatalogItem modifiedItem)
    {
        var original = FindCatalogItem(modifiedItem.Id);
        if (original is not null)
        {
            _catalogItems[_catalogItems.IndexOf(original)] = modifiedItem;
        }
    }

    // BR-017 (mock): remove the item.
    public void RemoveCatalogItem(CatalogItem catalogItem) => _catalogItems.Remove(catalogItem);

    public void Dispose()
    {
    }

    private List<CatalogItem> Compose(List<CatalogItem> items)
    {
        foreach (var item in items)
        {
            item.CatalogBrand ??= _catalogBrands.First(b => b.Id == item.CatalogBrandId);
            item.CatalogType ??= _catalogTypes.First(t => t.Id == item.CatalogTypeId);
        }
        return items;
    }
}
