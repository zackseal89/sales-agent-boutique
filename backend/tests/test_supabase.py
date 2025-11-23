"""
Test script to verify Supabase connection and data
"""

import asyncio
import sys
import os
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.supabase_service import supabase_service

@pytest.mark.skip(reason="Supabase credentials not available in test environment")
@pytest.mark.anyio
async def test_connection():
    """Test Supabase connection and query data"""
    
    # Test 1: Get boutique
    boutique = await supabase_service.get_boutique("550e8400-e29b-41d4-a716-446655440000")
    assert boutique is not None, "Boutique not found"
    
    # Test 2: Get products
    products = await supabase_service.get_products("550e8400-e29b-41d4-a716-446655440000")
    assert products is not None, "Products not found"

    # Test 3: Search products
    results = await supabase_service.search_products_by_text(
        "550e8400-e29b-41d4-a716-446655440000",
        "dress"
    )
    assert results is not None, "Search results not found"

    # Test 4: Create customer
    customer = await supabase_service.get_or_create_customer(
        "550e8400-e29b-41d4-a716-446655440000",
        "254700000000",
        "Test Customer"
    )
    assert customer is not None, "Customer not created"
