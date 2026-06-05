using eShopModernized.Catalog.Models;
using eShopModernized.Catalog.Services;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;

namespace eShopModernized.Catalog.Controllers;

/// <summary>
/// Catalog admin UI. Thin HTTP layer delegating to ICatalogService.
/// Handles FLOW-001..005 and BR-006, BR-007, BR-010, BR-012, BR-013.
/// </summary>
public class CatalogController : Controller
{
    private readonly ICatalogService _service;
    private readonly ILogger<CatalogController> _log;

    public CatalogController(ICatalogService service, ILogger<CatalogController> log)
    {
        _service = service;
        _log = log;
    }

    // FLOW-001: GET /Catalog[?pageSize=&pageIndex=]
    public IActionResult Index(int pageSize = 10, int pageIndex = 0)
    {
        _log.LogInformation("Loading /Catalog/Index?pageSize={PageSize}&pageIndex={PageIndex}", pageSize, pageIndex);
        var paginatedItems = _service.GetCatalogItemsPaginated(pageSize, pageIndex);
        ChangeUriPlaceholder(paginatedItems.Data);
        return View(paginatedItems);
    }

    // FLOW-002: GET /Catalog/Details/{id}
    public IActionResult Details(int? id)
    {
        if (id == null)
        {
            return BadRequest(); // BR-006 / ERR-001
        }

        var catalogItem = _service.FindCatalogItem(id.Value);
        if (catalogItem == null)
        {
            return NotFound(); // BR-007 / ERR-002
        }

        AddUriPlaceHolder(catalogItem); // BR-010
        return View(catalogItem);
    }

    // GET /Catalog/Create
    public IActionResult Create()
    {
        PopulateSelectLists();
        return View(new CatalogItem());
    }

    // FLOW-003: POST /Catalog/Create
    [HttpPost]
    [ValidateAntiForgeryToken] // BR-012
    public IActionResult Create([Bind("Id,Name,Description,Price,PictureFileName,CatalogTypeId,CatalogBrandId,AvailableStock,RestockThreshold,MaxStockThreshold,OnReorder")] CatalogItem catalogItem)
    {
        // BR-013: persist only when the model is valid, else redisplay.
        if (ModelState.IsValid)
        {
            _service.CreateCatalogItem(catalogItem);
            return RedirectToAction(nameof(Index));
        }

        PopulateSelectLists(catalogItem); // ERR-003
        return View(catalogItem);
    }

    // GET /Catalog/Edit/{id}
    public IActionResult Edit(int? id)
    {
        if (id == null)
        {
            return BadRequest(); // BR-006
        }

        var catalogItem = _service.FindCatalogItem(id.Value);
        if (catalogItem == null)
        {
            return NotFound(); // BR-007
        }

        AddUriPlaceHolder(catalogItem);
        PopulateSelectLists(catalogItem);
        return View(catalogItem);
    }

    // FLOW-004: POST /Catalog/Edit/{id}
    [HttpPost]
    [ValidateAntiForgeryToken] // BR-012
    public IActionResult Edit([Bind("Id,Name,Description,Price,PictureFileName,CatalogTypeId,CatalogBrandId,AvailableStock,RestockThreshold,MaxStockThreshold,OnReorder")] CatalogItem catalogItem)
    {
        if (ModelState.IsValid) // BR-013
        {
            _service.UpdateCatalogItem(catalogItem); // BR-015
            return RedirectToAction(nameof(Index));
        }

        PopulateSelectLists(catalogItem); // ERR-003
        return View(catalogItem);
    }

    // GET /Catalog/Delete/{id}
    public IActionResult Delete(int? id)
    {
        if (id == null)
        {
            return BadRequest(); // BR-006
        }

        var catalogItem = _service.FindCatalogItem(id.Value);
        if (catalogItem == null)
        {
            return NotFound(); // BR-007
        }

        AddUriPlaceHolder(catalogItem);
        return View(catalogItem);
    }

    // FLOW-005: POST /Catalog/Delete/{id}
    [HttpPost, ActionName("Delete")]
    [ValidateAntiForgeryToken] // BR-012
    public IActionResult DeleteConfirmed(int id)
    {
        var catalogItem = _service.FindCatalogItem(id);
        if (catalogItem == null)
        {
            return NotFound(); // BR-007
        }

        _service.RemoveCatalogItem(catalogItem); // BR-017
        return RedirectToAction(nameof(Index));
    }

    private void PopulateSelectLists(CatalogItem? selected = null)
    {
        ViewBag.CatalogBrandId = new SelectList(_service.GetCatalogBrands(), "Id", "Brand", selected?.CatalogBrandId);
        ViewBag.CatalogTypeId = new SelectList(_service.GetCatalogTypes(), "Id", "Type", selected?.CatalogTypeId);
    }

    private void ChangeUriPlaceholder(IEnumerable<CatalogItem> items)
    {
        foreach (var catalogItem in items)
        {
            AddUriPlaceHolder(catalogItem);
        }
    }

    // BR-010: compute the picture URL per item. Placeholder route until the
    // Product Imagery feature provides the canonical pic endpoint.
    private void AddUriPlaceHolder(CatalogItem item)
    {
        item.PictureUri = $"/Pics/{item.Id}.png";
    }
}
