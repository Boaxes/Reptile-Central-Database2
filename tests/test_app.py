import pytest
from playwright.sync_api import Page, expect

TIMEOUT = 30_000
SUCCESS = "successfully"


@pytest.fixture(scope="session", autouse=True)
def reset_db(browser, pytestconfig):
    """Reset the database to seed state once before all tests run."""
    base_url = pytestconfig.getoption("base_url")
    ctx = browser.new_context(base_url=base_url)
    pg = ctx.new_page()
    pg.set_default_timeout(TIMEOUT)
    pg.goto("/")
    pg.wait_for_selector("[data-testid='stMainBlockContainer']")
    pg.locator("[data-testid='stSidebar']").get_by_role("button", name="Reset Database").click()
    pg.wait_for_timeout(5_000)
    pg.close()
    ctx.close()


@pytest.fixture(autouse=True)
def default_timeout(page: Page):
    page.set_default_timeout(TIMEOUT)


# Customer
def test_customer_create(page: Page):
    page.goto("/Customers")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Create Customer").click()
    f = page.locator("[data-testid='stForm']").filter(has=page.get_by_role("button", name="Create Customer"))
    f.get_by_label("First Name").fill("Test")
    f.get_by_label("Last Name").fill("User")
    f.get_by_label("Email").fill("test.user@testexample.com")
    f.get_by_label("Phone Number").fill("555-000-0001")
    f.get_by_role("button", name="Create Customer").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)


def test_customer_update(page: Page):
    page.goto("/Customers")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Update Customer").click()
    f = page.locator("[data-testid='stForm']").filter(has=page.get_by_role("button", name="Update Customer"))
    f.get_by_label("Email").fill("updated@testexample.com")
    f.get_by_label("Phone Number").fill("541-555-9999")
    f.get_by_role("button", name="Update Customer").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)


def test_customer_delete(page: Page):
    page.goto("/Customers")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Delete Customer").click()
    panel = page.get_by_role("tabpanel", name="Delete Customer")
    select = panel.get_by_label("Select Record")
    select.click()
    select.fill("Test User")
    page.get_by_role("option", name="Test User", exact=True).click()
    panel.get_by_role("button", name="Delete").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)


# Animal
def test_animal_create(page: Page):
    page.goto("/Animals")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Create Animal").click()
    f = page.locator("[data-testid='stForm']").filter(has=page.get_by_role("button", name="Create Animal"))
    f.get_by_label("Name").fill("Rex")
    f.get_by_label("Species").fill("Blue-Tongued Skink")
    f.get_by_label("Age").fill("1")
    f.get_by_label("Price").fill("89.99")
    f.get_by_role("button", name="Create Animal").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)


def test_animal_update(page: Page):
    page.goto("/Animals")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Update Animal").click()
    f = page.locator("[data-testid='stForm']").filter(has=page.get_by_role("button", name="Update Animal"))
    f.get_by_label("Age").fill("3")
    f.get_by_label("Price").fill("159.99")
    f.get_by_role("button", name="Update Animal").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)


def test_animal_delete(page: Page):
    page.goto("/Animals")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Delete Animal").click()
    panel = page.get_by_role("tabpanel", name="Delete Animal")
    select = panel.get_by_label("Select Record")
    select.click()
    select.fill("Rex")
    page.get_by_role("option", name="Rex", exact=True).click()
    panel.get_by_role("button", name="Delete").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)


# Employee
def test_employee_create(page: Page):
    page.goto("/Employees")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Create Employee").click()
    f = page.locator("[data-testid='stForm']").filter(has=page.get_by_role("button", name="Create Employee"))
    f.get_by_label("First Name").fill("New")
    f.get_by_label("Last Name").fill("Hire")
    f.get_by_label("Job Title").fill("Reptile Technician")
    f.get_by_role("button", name="Create Employee").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)


def test_employee_update(page: Page):
    page.goto("/Employees")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Update Employee").click()
    f = page.locator("[data-testid='stForm']").filter(has=page.get_by_role("button", name="Update Employee"))
    f.get_by_label("First Name").fill("Taylor")
    f.get_by_label("Last Name").fill("Morgan")
    f.get_by_label("Job Title").fill("Senior Manager")
    f.get_by_role("button", name="Update Employee").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)


def test_employee_delete(page: Page):
    page.goto("/Employees")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Delete Employee").click()
    panel = page.get_by_role("tabpanel", name="Delete Employee")
    select = panel.get_by_label("Select Record")
    select.click()
    # Delete the record test_employee_create made; test_assignment_update later needs Taylor Morgan (ID 1) intact.
    select.fill("New Hire")
    page.get_by_role("option", name="New Hire", exact=True).click()
    panel.get_by_role("button", name="Delete").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)


# Product Type
def test_product_type_create(page: Page):
    page.goto("/Product_Types")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Create Product Type").click()
    f = page.locator("[data-testid='stForm']").filter(has=page.get_by_role("button", name="Create Product Type"))
    f.get_by_label("Product Type Code").fill("SUP")
    f.get_by_label("Product Type Name").fill("Supplements")
    f.get_by_role("button", name="Create Product Type").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)


def test_product_type_update(page: Page):
    page.goto("/Product_Types")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Update Product Type").click()
    f = page.locator("[data-testid='stForm']").filter(has=page.get_by_role("button", name="Update Product Type"))
    f.get_by_label("Product Type Name").fill("Animal Enclosures")
    f.get_by_role("button", name="Update Product Type").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)


def test_product_type_delete(page: Page):
    page.goto("/Product_Types")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Delete Product Type").click()
    # Seed types (ENC/LGT/FOD) are referenced by Products and can't be deleted.
    # Pick SUP — the type created earlier in test_product_type_create has no FK references.
    panel = page.get_by_role("tabpanel", name="Delete Product Type")
    panel.get_by_label("Select Record").click()
    page.get_by_role("option", name="SUP Supplements").click()
    panel.get_by_role("button", name="Delete").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)


# Product
def test_product_create(page: Page):
    page.goto("/Products")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Create Product").click()
    f = page.locator("[data-testid='stForm']").filter(has=page.get_by_role("button", name="Create Product"))
    f.get_by_label("Product Name").fill("Test Habitat Kit")
    f.get_by_label("Price").fill("49.99")
    f.get_by_label("Stock").fill("5")
    f.get_by_role("button", name="Create Product").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)


def test_product_update(page: Page):
    page.goto("/Products")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Update Product").click()
    f = page.locator("[data-testid='stForm']").filter(has=page.get_by_role("button", name="Update Product"))
    f.get_by_label("Product Name").fill("40-Gallon Terrarium Plus")
    f.get_by_label("Price").fill("219.99")
    f.get_by_label("Stock").fill("8")
    f.get_by_role("button", name="Update Product").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)


def test_product_delete(page: Page):
    page.goto("/Products")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Delete Product").click()
    panel = page.get_by_role("tabpanel", name="Delete Product")
    panel.get_by_label("Select Record").click()
    # test_product_update renames "Test Habitat Kit" → "40-Gallon Terrarium Plus".
    page.get_by_role("option", name="40-Gallon Terrarium Plus", exact=True).click()
    panel.get_by_role("button", name="Delete").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)


# Employee Assignment
def test_assignment_create(page: Page):
    page.goto("/Employee_Assignments")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Create Assignment").click()
    page.get_by_role("button", name="Create Assignment").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)


def test_assignment_update(page: Page):
    page.goto("/Employee_Assignments")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Update Assignment").click()
    f = page.locator("[data-testid='stForm']").filter(has=page.get_by_role("button", name="Update Assignment"))
    f.locator("[data-testid='stSelectbox']").filter(has_text="Employee").click()
    page.get_by_role("option", name="1 - Taylor Morgan", exact=True).click()
    f.get_by_role("button", name="Update Assignment").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)


def test_assignment_delete(page: Page):
    page.goto("/Employee_Assignments")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Delete Assignment").click()
    page.get_by_role("button", name="Delete").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)


# Order
def test_order_create_requires_items(page: Page):
    """Submitting a new order with no items selected shows a validation error."""
    page.goto("/Orders")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Create Order").click()
    page.get_by_role("button", name="Create Order").click()
    expect(page.get_by_text("atleast one item")).to_be_visible(timeout=TIMEOUT)


def test_order_update_item(page: Page):
    page.goto("/Orders")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="View or Update Order Details").click()
    page.get_by_role("button", name="Update or Add Item").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)


def test_order_delete(page: Page):
    page.goto("/Orders")
    page.wait_for_selector("[data-testid='stMainBlockContainer']")
    page.get_by_role("tab", name="Delete Order").click()
    page.get_by_role("button", name="Delete").click()
    expect(page.locator("[data-testid='stAlertContentSuccess']")).to_contain_text(SUCCESS, timeout=TIMEOUT)
