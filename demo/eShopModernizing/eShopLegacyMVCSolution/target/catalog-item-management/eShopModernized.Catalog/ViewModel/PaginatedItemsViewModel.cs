namespace eShopModernized.Catalog.ViewModel;

/// <summary>
/// Paging envelope. Implements data_model: PaginatedItemsViewModel and BR-009
/// (TotalPages = ceil(count / pageSize)).
/// </summary>
public class PaginatedItemsViewModel<TEntity> where TEntity : class
{
    public int ActualPage { get; }

    public int ItemsPerPage { get; }

    public long TotalItems { get; }

    public int TotalPages { get; }

    public IEnumerable<TEntity> Data { get; }

    public PaginatedItemsViewModel(int pageIndex, int pageSize, long count, IEnumerable<TEntity> data)
    {
        ActualPage = pageIndex;
        ItemsPerPage = pageSize;
        TotalItems = count;
        // BR-009: total pages is the ceiling of total items divided by page size.
        TotalPages = (int)Math.Ceiling((decimal)count / pageSize);
        Data = data;
    }
}
