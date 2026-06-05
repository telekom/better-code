using System.ComponentModel.DataAnnotations;

namespace eShopModernized.Catalog.Models;

/// <summary>
/// Catalog product entity. Implements data_model: CatalogItem.
/// Validation annotations preserve legacy parity:
/// BR-001 (Name required), BR-002 (Price), BR-003 (AvailableStock),
/// BR-004 (RestockThreshold), BR-005 (MaxStockThreshold), BR-014 (default picture).
/// </summary>
public class CatalogItem
{
    public const string DefaultPictureName = "dummy.png";

    // BR-014: a new catalog item defaults its picture file name.
    public CatalogItem()
    {
        PictureFileName = DefaultPictureName;
    }

    public int Id { get; set; }

    // BR-001: Name is required.
    [Required]
    public string Name { get; set; } = string.Empty;

    public string? Description { get; set; }

    // BR-002: positive, max 1,000,000, max two decimals, currency. decimal(18,2).
    [RegularExpression(@"^\d+(\.\d{0,2})*$", ErrorMessage = "The field Price must be a positive number with maximum two decimals.")]
    [Range(0, 1000000)]
    [DataType(DataType.Currency)]
    public decimal Price { get; set; }

    [Display(Name = "Picture name")]
    public string PictureFileName { get; set; }

    // BR-010: computed per request; not persisted (see CatalogItemConfig.Ignore).
    public string? PictureUri { get; set; }

    [Display(Name = "Type")]
    public int CatalogTypeId { get; set; }

    [Display(Name = "Type")]
    public CatalogType? CatalogType { get; set; }

    [Display(Name = "Brand")]
    public int CatalogBrandId { get; set; }

    [Display(Name = "Brand")]
    public CatalogBrand? CatalogBrand { get; set; }

    // BR-003: quantity in stock, 0..10,000,000.
    [Range(0, 10000000, ErrorMessage = "The field Stock must be between 0 and 10 million.")]
    [Display(Name = "Stock")]
    public int AvailableStock { get; set; }

    // BR-004: available stock at which we should reorder, 0..10,000,000.
    [Range(0, 10000000, ErrorMessage = "The field Restock must be between 0 and 10 million.")]
    [Display(Name = "Restock")]
    public int RestockThreshold { get; set; }

    // BR-005: maximum units in stock at any time, 0..10,000,000.
    [Range(0, 10000000, ErrorMessage = "The field Max stock must be between 0 and 10 million.")]
    [Display(Name = "Max stock")]
    public int MaxStockThreshold { get; set; }

    /// <summary>True if item is on reorder.</summary>
    public bool OnReorder { get; set; }
}
