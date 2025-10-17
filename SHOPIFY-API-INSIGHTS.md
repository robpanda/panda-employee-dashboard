# Shopify Orders API - Duplicate Issue Insights

## Problem Discovery

After researching Shopify's Orders API documentation and community forums, we discovered the root cause of our duplicate order sync issue.

## Key Findings from Shopify Documentation

### 1. Order ID vs Order Number
- **Order ID** (`id` field): The TRUE unique identifier in Shopify
- **Order Number** (`order_number` field): Display-only, NOT guaranteed to be unique
- **Finding**: Shopify can assign the same `order_number` to different orders placed by different customers
- **Source**: Shopify Community forums confirm this is a known issue with "no solution"

### 2. Why Duplicates Occur
According to Shopify community discussions:
- The same `order_number` can appear on multiple orders (rare but happens)
- When orders are edited/updated, Shopify may create new entries with different IDs
- Fulfillment companies report seeing duplicate line items via the API
- The `order_number` and `id` aren't always in sequence

### 3. Official Shopify Guidance
From Shopify's idempotency documentation:
- Use a unique identifier as an idempotency key
- Cache processed identifiers to avoid reprocessing
- Set expiration times for cached entries

## Our Implementation Strategy

### ✅ What We Implemented:
1. **Date + Order Number deduplication** - Helps but not perfect
2. **Auto-cleanup after sync** - Removes duplicates that slip through
3. **DB-aware sync** - Checks existing orders before adding
4. **Manual edit UI** - Gives direct control

### ⚠️ Why It's Not Perfect:
- Using `order_number` for dedup can still cause issues because Shopify doesn't guarantee uniqueness
- Using `id` alone doesn't work because the same logical order can have different IDs after edits

### 💡 Better Approach (Future Enhancement):
Store a **mapping of Shopify IDs to order numbers** in the database:
```javascript
{
  "shopify_id": "5678901234",
  "order_number": "1045",
  "created_at": "2024-01-15",
  "employee_email": "blair@example.com",
  "synced_at": "2024-10-17T13:00:00Z"
}
```

This would allow us to:
- Track all Shopify IDs we've seen
- Prevent re-adding any ID we've already processed
- Handle order edits gracefully
- Maintain accurate order history

## Current Solution

Given the complexity of Shopify's API behavior, our **recommended approach** is:

1. **Use the Manual Edit UI** for critical data management
2. **Use the Sync button** only for bulk imports of new orders
3. **Always verify data** after running sync
4. **Let auto-cleanup** handle any duplicates that slip through

## References

- [Shopify Community: Duplicate Orders](https://community.shopify.com/c/shopify-apis-and-sdks/sending-in-an-order-via-api-orders-json-creates-a-duplicate/td-p/1549291)
- [Shopify Community: Order Number vs ID Issues](https://community.shopify.com/t/rest-api-pulling-orders-by-since-id-issue-with-shopify-api-order-vs-order-number-sequence/320628/1)
- [Shopify: Action Endpoint Idempotency](https://shopify.dev/docs/apps/build/marketing-analytics/automations/action-endpoints)

## Conclusion

The duplicate order issue is a **combination of**:
1. Shopify's API returning non-unique order_numbers
2. Order edits creating new IDs for the same logical order
3. No official Shopify solution for this known issue

Our multi-layered approach (deduplication + auto-cleanup + manual edit UI) provides the best protection against this Shopify API behavior.
