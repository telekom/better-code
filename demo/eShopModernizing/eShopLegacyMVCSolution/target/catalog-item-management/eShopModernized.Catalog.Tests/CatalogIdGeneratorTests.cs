using eShopModernized.Catalog.Models;
using eShopModernized.Catalog.Models.Infrastructure;
using FluentAssertions;
using Xunit;

namespace eShopModernized.Catalog.Tests;

/// <summary>
/// Verifies HiLo batching (BR-016): one sequence fetch yields 10 consecutive ids.
/// </summary>
public class CatalogIdGeneratorTests
{
    /// <summary>Test generator that returns a fixed block start and counts fetches.</summary>
    private sealed class TestIdGenerator : CatalogIdGenerator
    {
        private readonly long _blockStart;
        public int FetchCount { get; private set; }

        public TestIdGenerator(long blockStart) => _blockStart = blockStart;

        protected override long FetchNextSequenceValue(CatalogDBContext db)
        {
            FetchCount++;
            return _blockStart;
        }
    }

    [Fact] // TC-016 / BR-016
    public void HiLo_TenIdsPerFetch()
    {
        var generator = new TestIdGenerator(blockStart: 100);

        var ids = new List<int>();
        for (var i = 0; i < 10; i++)
        {
            ids.Add(generator.GetNextId(db: null!));
        }

        ids.Should().Equal(100, 101, 102, 103, 104, 105, 106, 107, 108, 109);
        generator.FetchCount.Should().Be(1);
    }
}
