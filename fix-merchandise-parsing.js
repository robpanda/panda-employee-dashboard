// Add this helper function to employee.html to safely parse merchandise values

/**
 * Safely parse merchandise value string to float
 * Handles formats like: "$144.29", "144.29", "$1,663.20", "1663.20"
 */
function parseMerchandiseValue(value) {
    if (!value) return 0;
    
    // Convert to string and remove $ and commas
    const cleaned = String(value).replace(/[$,]/g, '').trim();
    
    // Parse to float
    const parsed = parseFloat(cleaned);
    
    // Return 0 if NaN
    return isNaN(parsed) ? 0 : parsed;
}

// Replace all instances of:
// parseFloat(employee['Merchandise Value'] || 0)
// 
// With:
// parseMerchandiseValue(employee['Merchandise Value'])

// Example usage in employee.html:
// Line 1443: const merchValue = parseMerchandiseValue(employee['Merchandise Value']);
// Line 2075: totalValue += parseMerchandiseValue(merch.merchandise_value);
// Line 2098: <td><strong>$${parseMerchandiseValue(merch.merchandise_value).toFixed(2)}</strong></td>
// Line 2293: aVal = parseMerchandiseValue(a.merchandise_value);
// Line 2294: bVal = parseMerchandiseValue(b.merchandise_value);
