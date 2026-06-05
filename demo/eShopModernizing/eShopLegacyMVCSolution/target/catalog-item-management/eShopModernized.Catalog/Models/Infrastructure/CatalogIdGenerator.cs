using Microsoft.EntityFrameworkCore;

namespace eShopModernized.Catalog.Models.Infrastructure;

/// <summary>
/// HiLo primary-key generator (BR-011, BR-016). Fetches the next value from the
/// SQL sequence "catalog_hilo" and hands out <see cref="HiLoIncrement"/> consecutive
/// ids per database round-trip, guarded by a lock. Registered as a singleton.
///
/// Note (spec unknown #4): id state is cached per process. This is not safe for
/// scale-out across multiple instances without a distributed sequence strategy.
/// </summary>
public class CatalogIdGenerator
{
    private const int HiLoIncrement = 10;

    private readonly object _sequenceLock = new();
    private int _sequenceId = -1;
    private int _remainingLoIds = 0;

    /// <summary>
    /// Returns the next application-assigned catalog id. BR-016: one DB sequence
    /// fetch yields 10 ids before the next round-trip.
    /// </summary>
    public int GetNextId(CatalogDBContext db)
    {
        lock (_sequenceLock)
        {
            if (_remainingLoIds == 0)
            {
                _sequenceId = (int)FetchNextSequenceValue(db);
                _remainingLoIds = HiLoIncrement - 1;
                return _sequenceId;
            }

            _remainingLoIds--;
            return ++_sequenceId;
        }
    }

    /// <summary>
    /// Reads the next block-start value from the database sequence. Virtual so tests
    /// can supply a controlled value without a live SQL Server.
    /// </summary>
    protected virtual long FetchNextSequenceValue(CatalogDBContext db)
    {
        return db.Database
            .SqlQueryRaw<long>($"SELECT NEXT VALUE FOR {CatalogDBContext.HiLoSequenceName} AS Value")
            .AsEnumerable()
            .Single();
    }
}
