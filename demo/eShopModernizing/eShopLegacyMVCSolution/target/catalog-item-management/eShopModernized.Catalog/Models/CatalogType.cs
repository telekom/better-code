namespace eShopModernized.Catalog.Models;

/// <summary>
/// Catalog type reference entity. Implements data_model: CatalogType.
/// </summary>
public class CatalogType
{
    public int Id { get; set; }

    public string Type { get; set; } = string.Empty;
}
