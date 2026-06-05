namespace eShopModernized.Catalog.Models;

/// <summary>
/// Catalog brand reference entity. Implements data_model: CatalogBrand.
/// </summary>
public class CatalogBrand
{
    public int Id { get; set; }

    public string Brand { get; set; } = string.Empty;
}
