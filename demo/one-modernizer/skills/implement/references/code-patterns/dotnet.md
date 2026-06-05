# .NET / ASP.NET Core Code Patterns

## Project Structure

```
<service-name>/
├── <ServiceName>.sln
├── src/
│   └── <ServiceName>.Api/
│       ├── <ServiceName>.Api.csproj
│       ├── Program.cs
│       ├── Controllers/
│       │   └── OrderController.cs
│       ├── Services/
│       │   └── OrderService.cs
│       ├── Domain/
│       │   ├── Order.cs
│       │   └── OrderStatus.cs
│       ├── Data/
│       │   ├── AppDbContext.cs
│       │   └── OrderRepository.cs
│       ├── Dto/
│       │   ├── CreateOrderRequest.cs
│       │   └── OrderResponse.cs
│       ├── Exceptions/
│       │   └── CreditLimitExceededException.cs
│       └── Middleware/
│           └── ExceptionMiddleware.cs
├── tests/
│   └── <ServiceName>.Tests/
│       └── OrderServiceTests.cs
├── Dockerfile
└── docker-compose.yml
```

## Entity

```csharp
public class Order
{
    public long Id { get; set; }
    public required string CustomerId { get; set; }
    public decimal Total { get; set; }
    public OrderStatus Status { get; set; }
    public DateTime CreatedAt { get; set; }
    public List<OrderLine> Lines { get; set; } = [];
}

public enum OrderStatus { Pending, Approved, Rejected, Shipped }
```

## DbContext

```csharp
public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<Order> Orders => Set<Order>();
    public DbSet<OrderLine> OrderLines => Set<OrderLine>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Order>(e =>
        {
            e.ToTable("orders");
            e.HasKey(o => o.Id);
            e.Property(o => o.Total).HasPrecision(10, 2);
            e.HasIndex(o => o.CustomerId);
        });
    }
}
```

## Service

```csharp
public class OrderService(AppDbContext db, OrderValidator validator, IEventPublisher publisher)
{
    // Implements: BR-001
    public async Task<Order> CreateOrderAsync(CreateOrderRequest request, CancellationToken ct = default)
    {
        await validator.ValidateCreditLimitAsync(request, ct);

        var order = new Order
        {
            CustomerId = request.CustomerId,
            Total = request.Lines.Sum(l => l.Price * l.Quantity),
            Status = OrderStatus.Pending,
            CreatedAt = DateTime.UtcNow
        };

        db.Orders.Add(order);
        await db.SaveChangesAsync(ct);
        await publisher.PublishAsync(new OrderCreatedEvent(order.Id, order.CustomerId), ct);
        return order;
    }
}
```

## Controller

```csharp
[ApiController]
[Route("api/orders")]
public class OrderController(OrderService orderService) : ControllerBase
{
    [HttpPost]
    [ProducesResponseType<OrderResponse>(StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status422UnprocessableEntity)]
    public async Task<IActionResult> CreateOrder([FromBody] CreateOrderRequest request, CancellationToken ct)
    {
        var order = await orderService.CreateOrderAsync(request, ct);
        return CreatedAtAction(nameof(GetOrder), new { id = order.Id }, OrderResponse.From(order));
    }

    [HttpGet("{id:long}")]
    public async Task<IActionResult> GetOrder(long id, CancellationToken ct)
    {
        var order = await orderService.FindByIdAsync(id, ct);
        return order is null ? NotFound() : Ok(OrderResponse.From(order));
    }
}
```

## DTO (Records)

```csharp
public record CreateOrderRequest(
    [Required] string CustomerId,
    [Required, MinLength(1)] List<OrderLineRequest> Lines
);

public record OrderLineRequest(string ProductId, int Quantity, decimal Price);

public record OrderResponse(long Id, string CustomerId, decimal Total, string Status, DateTime CreatedAt)
{
    public static OrderResponse From(Order order) =>
        new(order.Id, order.CustomerId, order.Total, order.Status.ToString(), order.CreatedAt);
}
```

## Exception + Middleware

```csharp
public class CreditLimitExceededException(string customerId, decimal requested, decimal available)
    : Exception($"Credit limit exceeded for {customerId}: requested {requested}, available {available}")
{
    public string CustomerId => customerId;
}

public class ExceptionMiddleware(RequestDelegate next)
{
    public async Task InvokeAsync(HttpContext context)
    {
        try { await next(context); }
        catch (CreditLimitExceededException ex)
        {
            context.Response.StatusCode = 422;
            await context.Response.WriteAsJsonAsync(new { error = "CREDIT_LIMIT_EXCEEDED", message = ex.Message });
        }
    }
}
```

## Test (xUnit)

```csharp
public class OrderServiceTests
{
    private readonly Mock<AppDbContext> _db = new();
    private readonly Mock<IEventPublisher> _publisher = new();

    // Covers: TC-001
    [Fact]
    public async Task CreateOrder_ValidRequest_ReturnsCreatedOrder()
    {
        var service = new OrderService(_db.Object, new OrderValidator(), _publisher.Object);
        var request = new CreateOrderRequest("CUST-1", [new("P1", 2, 50m)]);

        var result = await service.CreateOrderAsync(request);

        Assert.Equal(OrderStatus.Pending, result.Status);
        _publisher.Verify(p => p.PublishAsync(It.IsAny<OrderCreatedEvent>(), It.IsAny<CancellationToken>()), Times.Once);
    }

    // Covers: TC-002
    [Fact]
    public async Task CreateOrder_CreditExceeded_ThrowsException()
    {
        var service = new OrderService(_db.Object, new OrderValidator(), _publisher.Object);
        var request = new CreateOrderRequest("CUST-1", [new("P1", 100, 500m)]);

        await Assert.ThrowsAsync<CreditLimitExceededException>(() => service.CreateOrderAsync(request));
    }
}
```
