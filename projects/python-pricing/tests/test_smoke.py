from pricing import catalog, discount, loyalty, safe


def test_tier_prices():
    assert catalog.unit_price(5) == 1000
    assert catalog.unit_price(100) == 500


def test_apply_percent():
    assert discount.apply_percent(1000, 0.2) == 800


def test_loyalty():
    assert loyalty.multiplier(600) == 2


def test_safe_helpers():
    assert safe.to_cents("1.50") == 150
    assert safe.amounts_equal(100, 100)
