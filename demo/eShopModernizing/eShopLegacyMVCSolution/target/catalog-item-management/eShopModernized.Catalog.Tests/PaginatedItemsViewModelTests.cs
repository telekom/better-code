using eShopModernized.Catalog.Models;
using eShopModernized.Catalog.ViewModel;
using FluentAssertions;
using Xunit;

namespace eShopModernized.Catalog.Tests;

public class PaginatedItemsViewModelTests
{
    [Fact] // TC-013 / BR-009
    public void TotalPages_IsCeiling()
    {
        var vm = new PaginatedItemsViewModel<CatalogItem>(
            pageIndex: 0, pageSize: 10, count: 12, data: new List<CatalogItem>());

        vm.TotalPages.Should().Be(2);
    }
}
