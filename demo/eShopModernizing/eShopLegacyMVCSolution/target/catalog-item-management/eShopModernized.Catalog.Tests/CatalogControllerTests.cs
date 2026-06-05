using System.Reflection;
using eShopModernized.Catalog.Controllers;
using eShopModernized.Catalog.Models;
using eShopModernized.Catalog.Services;
using FluentAssertions;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging.Abstractions;
using Xunit;

namespace eShopModernized.Catalog.Tests;

/// <summary>
/// Controller tests. Covers BR-006 (TC-009), BR-007 (TC-010), BR-010 (TC-011),
/// BR-012 anti-forgery (TC-018).
/// </summary>
public class CatalogControllerTests
{
    private static CatalogController NewController() =>
        new(new CatalogServiceMock(), NullLogger<CatalogController>.Instance);

    [Fact] // TC-009 / BR-006 / ERR-001
    public void Details_NullId_Returns400()
    {
        var result = NewController().Details(null);
        result.Should().BeOfType<BadRequestResult>();
    }

    [Fact] // TC-010 / BR-007 / ERR-002
    public void Details_MissingItem_Returns404()
    {
        var result = NewController().Details(99999);
        result.Should().BeOfType<NotFoundResult>();
    }

    [Fact] // TC-011 / BR-010
    public void Details_ValidId_ReturnsItemWithPictureUri()
    {
        var result = NewController().Details(1) as ViewResult;

        result.Should().NotBeNull();
        var item = result!.Model as CatalogItem;
        item.Should().NotBeNull();
        item!.Id.Should().Be(1);
        item.PictureUri.Should().NotBeNullOrEmpty();
    }

    [Fact] // TC-018 / BR-012
    public void Create_Post_RequiresAntiForgeryToken()
    {
        var createPost = typeof(CatalogController)
            .GetMethods()
            .Single(m => m.Name == nameof(CatalogController.Create)
                         && m.GetParameters().Any(p => p.ParameterType == typeof(CatalogItem)));

        createPost.GetCustomAttribute<ValidateAntiForgeryTokenAttribute>()
            .Should().NotBeNull("POST Create must be protected against CSRF (BR-012)");
    }
}
