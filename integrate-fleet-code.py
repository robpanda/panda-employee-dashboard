#!/usr/bin/env python3
"""
Integrate fleet modals and JavaScript into assets.html
"""

# Read the fleet modals and JS
with open('/Users/robwinters/Documents/GitHub/panda-employee-dashboard/fleet-modals-and-js.html', 'r') as f:
    fleet_content = f.read()

# Split into modals and JS sections
parts = fleet_content.split('<!-- ADD THIS JAVASCRIPT CODE AT THE END OF THE SCRIPT SECTION')
modals_section = parts[0].replace('<!-- ADD THIS SECTION RIGHT BEFORE THE CLOSING </div> BEFORE SCRIPT TAG -->', '').strip()
js_section = parts[1].replace('(before </script> tag) -->', '').replace('<script>', '').replace('</script>', '').strip()

# Read assets.html
with open('/Users/robwinters/Documents/GitHub/panda-employee-dashboard/assets.html', 'r') as f:
    assets_content = f.read()

# Insert modals before the script tag
assets_content = assets_content.replace(
    '    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>',
    f'{modals_section}\n\n    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>'
)

# Insert JavaScript before the closing </script> tag
assets_content = assets_content.replace(
    '    </script>\n</body>',
    f'\n{js_section}\n    </script>\n</body>'
)

# Write back to assets.html
with open('/Users/robwinters/Documents/GitHub/panda-employee-dashboard/assets.html', 'w') as f:
    f.write(assets_content)

print("✅ Successfully integrated fleet modals and JavaScript into assets.html!")
print("   - Added 4 modal dialogs")
print("   - Added fleet management JavaScript code")
