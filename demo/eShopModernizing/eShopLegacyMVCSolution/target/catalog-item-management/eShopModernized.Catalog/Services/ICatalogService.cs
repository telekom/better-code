using eShopModernized.Catalog.Models;
using eShopModernized.Catalog.ViewModel;

namespace eShopModernized.Catalog.Services;

/// <summary>
/// Catalog application service contract. Preserves the legacy ICatalogService seam.
/// </summary>
public interface ICatalogService : IDisposable
{
    CatalogItem? FindCatalogItem(int id);
    IEnumerable<CatalogBrand> GetCatalogBrands();
    PaginatedItemsViewModel<CatalogItem> GetCatalogItemsPaginated(int pageSize, int pageIndex);
    IEnumerable<CatalogType> GetCatalogTypes();
    void CreateCatalogItem(CatalogItem catalogItem);
    void UpdateCatalogItem(CatalogItem catalogItem);
    void RemoveCatalogItem(CatalogItem catalogItem);
}
