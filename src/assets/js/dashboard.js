let employees = [];
let terminatedEmployees = [];
let backupData = null;

const API_BASE = 'https://w40mq6ab11.execute-api.us-east-2.amazonaws.com/prod';

function parseName(fullName) {
    if (!fullName) return { firstName: '', lastName: '' };
    
    const name = fullName.replace(/"/g, '').trim();
    const parts = name.split(' ');
    
    if (parts.length === 1) {
        return { firstName: parts[0], lastName: '' };
    } else if (parts.length === 2) {
        return { firstName: parts[0], lastName: parts[1] };
    } else {
        return {
            firstName: parts[0],
            lastName: parts.slice(1).join(' ')
        };
    }
}

function parseCSV(csvText) {
    const lines = csvText.split('\n');
    const headers = lines[0].split(',').map(h => h.replace(/"/g, '').trim());
    const data = [];
    
    for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim()) {
            const values = parseCSVLine(lines[i]);
            const row = {};
            
            headers.forEach((header, index) => {
                row[header] = values[index] || '';
            });
            
            if (row.Name) {
                const nameInfo = parseName(row.Name);
                row['First Name'] = nameInfo.firstName;
                row['Last Name'] = nameInfo.lastName;
                delete row.Name;
            }
            
            data.push(row);
        }
    }
    
    return data;
}

function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        
        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            result.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }
    
    result.push(current.trim());
    return result;
}

function smartImport(newEmployees) {
    const today = new Date().toISOString().split('T')[0];
    let added = 0, terminated = 0, unchanged = 0;
    
    // Create lookup for new employees by email and name
    const newLookup = new Map();
    newEmployees.forEach(emp => {
        const email = (emp.Email || '').toLowerCase().trim();
        const name = `${emp['First Name'] || ''} ${emp['Last Name'] || ''}`.toLowerCase().trim();
        
        if (email) newLookup.set(email, emp);
        if (name) newLookup.set(name, emp);
    });
    
    // Check existing active employees
    const toTerminate = [];
    employees.forEach((emp, index) => {
        const email = (emp.Email || '').toLowerCase().trim();
        const name = `${emp['First Name'] || ''} ${emp['Last Name'] || ''}`.toLowerCase().trim();
        
        const found = newLookup.has(email) || newLookup.has(name);
        
        if (!found) {
            toTerminate.push(index);
        }
    });
    
    // Terminate employees not in new list
    toTerminate.reverse().forEach(index => {
        const emp = employees[index];
        emp['Termination Date'] = today;
        emp['Terminated'] = 'Yes';
        terminatedEmployees.push(emp);
        employees.splice(index, 1);
        terminated++;
    });
    
    // Add new employees
    newEmployees.forEach(newEmp => {
        const email = (newEmp.Email || '').toLowerCase().trim();
        const name = `${newEmp['First Name'] || ''} ${newEmp['Last Name'] || ''}`.toLowerCase().trim();
        
        const existsActive = employees.some(emp => {
            const empEmail = (emp.Email || '').toLowerCase().trim();
            const empName = `${emp['First Name'] || ''} ${emp['Last Name'] || ''}`.toLowerCase().trim();
            return (email && empEmail === email) || (name && empName === name);
        });
        
        const existsTerminated = terminatedEmployees.some(emp => {
            const empEmail = (emp.Email || '').toLowerCase().trim();
            const empName = `${emp['First Name'] || ''} ${emp['Last Name'] || ''}`.toLowerCase().trim();
            return (email && empEmail === email) || (name && empName === name);
        });
        
        if (!existsActive && !existsTerminated) {
            // New employee - set as new hire with today's date if no employment date
            if (!newEmp['Employment Date']) {
                newEmp['Employment Date'] = today;
            }
            newEmp['Terminated'] = 'No';
            employees.push(newEmp);
            added++;
        } else {
            unchanged++;
        }
    });
    
    return { added, terminated, unchanged };
}

function undoImport() {
    if (!backupData) {
        alert('No backup data available to undo.');
        return;
    }
    
    employees = [...backupData.employees];
    terminatedEmployees = [...backupData.terminatedEmployees];
    
    renderEmployeeTable();
    renderTerminatedTable();
    
    // Save restored data to database
    saveEmployeesToDB([...employees, ...terminatedEmployees]);
    
    document.getElementById('uploadStatus').innerHTML = 
        `<div style="color: blue; margin-top: 10px;">✓ Import undone - data restored to previous state</div>`;
    
    backupData = null;
}

function renderEmployeeTable() {
    const tbody = document.getElementById('employeeTableBody');
    tbody.innerHTML = '';
    
    let newHireCount = 0;
    const today = new Date();
    const ninetyDaysAgo = new Date(today.getTime() - (90 * 24 * 60 * 60 * 1000));
    
    employees.forEach((emp, index) => {
        const row = document.createElement('tr');
        
        const empDate = new Date(emp['Employment Date']);
        if (empDate > ninetyDaysAgo && empDate <= today) {
            newHireCount++;
        }
        
        // Calculate days employed for color coding
        const daysEmployed = Math.floor((today - empDate) / (1000 * 60 * 60 * 24));
        let yearsColor = '';
        if (daysEmployed <= 40) {
            yearsColor = 'color: #dc3545; font-weight: bold;'; // Red
        } else if (daysEmployed <= 89) {
            yearsColor = 'color: #ffc107; font-weight: bold;'; // Yellow
        } else {
            yearsColor = 'color: #28a745; font-weight: bold;'; // Green
        }
        
        row.innerHTML = `
            <td><input type="checkbox" class="employee-select" data-index="${index}" onchange="updateEmployeeMergeButton()"> <a href="#" class="name-link" onclick="openEditModal(${index})">${emp['First Name'] || ''}</a></td>
            <td>${emp['Last Name'] || ''}</td>
            <td>${emp.Department || ''}</td>
            <td>${emp.Position || ''}</td>
            <td>${emp['Employment Date'] || ''}</td>
            <td style="${yearsColor}">${emp['Years of Service'] || ''}</td>
            <td>${emp.Email || ''}</td>
            <td>${emp.Phone || ''}</td>
            <td>${emp['Merch Requested'] || ''}</td>
            <td>${emp['Merch Sent'] || 'No'}</td>
            <td>
                <button class="action-btn edit-btn" onclick="openEditModal(${index})">Edit</button>
                <button class="action-btn delete-btn" onclick="terminateEmployee(${index})">Terminate</button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
    
    document.getElementById('totalEmployees').textContent = employees.length;
    document.getElementById('newHires').textContent = newHireCount;
    updateEmployeeMergeButton();
}

function renderTerminatedTable() {
    const tbody = document.getElementById('terminatedTableBody');
    tbody.innerHTML = '';
    
    terminatedEmployees.forEach((emp, index) => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${emp['First Name'] || ''}</td>
            <td>${emp['Last Name'] || ''}</td>
            <td>${emp.Department || ''}</td>
            <td>${emp.Position || ''}</td>
            <td>${emp['Employment Date'] || ''}</td>
            <td>${emp['Termination Date'] || 'N/A'}</td>
            <td>${emp.Email || ''}</td>
            <td><button class="action-btn merge-btn" onclick="reactivateEmployee(${index})">Reactivate</button></td>
        `;
        
        tbody.appendChild(row);
    });
}

function terminateEmployee(index) {
    const employee = employees[index];
    const today = new Date().toISOString().split('T')[0];
    employee['Termination Date'] = today;
    employee['Terminated'] = 'Yes';
    
    terminatedEmployees.push(employee);
    employees.splice(index, 1);
    
    renderEmployeeTable();
    renderTerminatedTable();
    saveEmployeesToDB([...employees, ...terminatedEmployees]);
}

function reactivateEmployee(index) {
    const employee = terminatedEmployees[index];
    delete employee['Termination Date'];
    employee['Terminated'] = 'No';
    
    employees.push(employee);
    terminatedEmployees.splice(index, 1);
    
    renderEmployeeTable();
    renderTerminatedTable();
    saveEmployeesToDB([...employees, ...terminatedEmployees]);
}

let currentEditIndex = -1;

function openEditModal(index) {
    currentEditIndex = index;
    const emp = employees[index];
    
    document.getElementById('editFirstName').value = emp['First Name'] || '';
    document.getElementById('editLastName').value = emp['Last Name'] || '';
    document.getElementById('editDepartment').value = emp.Department || '';
    document.getElementById('editPosition').value = emp.Position || '';
    document.getElementById('editEmploymentDate').value = emp['Employment Date'] || '';
    document.getElementById('editYearsOfService').value = emp['Years of Service'] || '';
    document.getElementById('editEmail').value = emp.Email || '';
    document.getElementById('editPhone').value = emp.Phone || '';
    document.getElementById('editMerchRequested').value = emp['Merch Requested'] || '';
    document.getElementById('editMerchSent').value = emp['Merch Sent'] || 'No';
    document.getElementById('editMerchSentDate').value = emp['Merch Sent Date'] || '';
    
    document.getElementById('editModal').style.display = 'block';
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
    currentEditIndex = -1;
}

async function saveEmployee() {
    if (currentEditIndex === -1) return;
    
    const emp = employees[currentEditIndex];
    emp['First Name'] = document.getElementById('editFirstName').value;
    emp['Last Name'] = document.getElementById('editLastName').value;
    emp.Department = document.getElementById('editDepartment').value;
    emp.Position = document.getElementById('editPosition').value;
    emp['Employment Date'] = document.getElementById('editEmploymentDate').value;
    emp['Years of Service'] = document.getElementById('editYearsOfService').value;
    emp.Email = document.getElementById('editEmail').value;
    emp.Phone = document.getElementById('editPhone').value;
    emp['Merch Requested'] = document.getElementById('editMerchRequested').value;
    emp['Merch Sent'] = document.getElementById('editMerchSent').value;
    emp['Merch Sent Date'] = document.getElementById('editMerchSentDate').value;
    
    try {
        await saveEmployeesToDB([...employees, ...terminatedEmployees]);
        renderEmployeeTable();
        closeEditModal();
    } catch (error) {
        console.error('Save failed:', error);
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('editModal');
    if (event.target === modal) {
        closeEditModal();
    }
}

function findDuplicates() {
    const duplicates = [];
    const seen = new Map();
    
    [...employees, ...terminatedEmployees].forEach((emp, index) => {
        const email = (emp.Email || '').toLowerCase().trim();
        const lastName = (emp['Last Name'] || '').toLowerCase().trim();
        const fullName = `${emp['First Name'] || ''} ${emp['Last Name'] || ''}`.toLowerCase().trim();
        
        // Check email duplicates (highest priority)
        if (email && seen.has(`email:${email}`)) {
            duplicates.push({ ...emp, matchType: 'Email', group: seen.get(`email:${email}`) });
        } else if (email) {
            seen.set(`email:${email}`, duplicates.length + 1);
        }
        
        // Check last name duplicates
        if (lastName && seen.has(`lastName:${lastName}`)) {
            duplicates.push({ ...emp, matchType: 'Last Name', group: seen.get(`lastName:${lastName}`) });
        } else if (lastName) {
            seen.set(`lastName:${lastName}`, duplicates.length + 1);
        }
        
        // Check full name duplicates
        if (fullName && seen.has(`fullName:${fullName}`)) {
            duplicates.push({ ...emp, matchType: 'Full Name', group: seen.get(`fullName:${fullName}`) });
        } else if (fullName) {
            seen.set(`fullName:${fullName}`, duplicates.length + 1);
        }
    });
    
    return duplicates;
}

function renderDuplicateTable() {
    const tbody = document.getElementById('duplicateTableBody');
    tbody.innerHTML = '';
    
    const duplicates = findDuplicates();
    
    duplicates.forEach((emp, index) => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td><input type="checkbox" class="duplicate-select" data-index="${index}" onchange="updateMergeButton()"></td>
            <td>${emp.group}</td>
            <td>${emp.matchType}</td>
            <td>${emp['First Name'] || ''}</td>
            <td>${emp['Last Name'] || ''}</td>
            <td>${emp.Department || ''}</td>
            <td>${emp['Employment Date'] || ''}</td>
            <td>${emp.Email || ''}</td>
            <td>
                <button class="action-btn merge-btn" onclick="mergeDuplicate(${index})">Merge</button>
                <button class="action-btn delete-btn" onclick="deleteDuplicate(${index})">Delete</button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
    updateMergeButton();
}

function mergeDuplicate(index) {
    alert('Merge functionality - combine duplicate records');
}

function deleteDuplicate(index) {
    if (confirm('Delete this duplicate record?')) {
        alert('Delete functionality - remove duplicate');
    }
}

async function loadEmployees() {
    try {
        const response = await fetch(`${API_BASE}/employees`);
        const data = await response.json();
        if (data.employees) {
            const allEmployees = data.employees;
            employees = allEmployees.filter(emp => emp.Terminated !== 'Yes');
            terminatedEmployees = allEmployees.filter(emp => emp.Terminated === 'Yes');
            renderEmployeeTable();
            renderTerminatedTable();
        }
    } catch (error) {
        console.error('Error loading employees:', error);
    }
}

async function saveEmployeesToDB(allEmployees) {
    try {
        const response = await fetch(`${API_BASE}/employees`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({employees: allEmployees})
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        const result = await response.json();
        console.log('Data saved successfully:', result);
        return result;
    } catch (error) {
        console.error('Database save error:', error);
        throw error;
    }
}

function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
    
    // Render duplicates when switching to duplicates tab
    if (tabName === 'duplicates') {
        renderDuplicateTable();
    }
}

async function downloadFromGoogleSheets() {
    document.getElementById('uploadStatus').innerHTML = 
        '<div style="color: blue; margin-top: 10px;">📥 Fetching data from Google Sheets...</div>';
    
    try {
        // Google Sheets CSV export URL
        const sheetId = '1vO-94iEtB8FAthneJ8Cx1Cm-iA-oHJiBwOPAGmsiM-4';
        const csvUrl = `https://docs.google.com/spreadsheets/d/${sheetId}/export?format=csv&gid=0`;
        
        const response = await fetch(csvUrl, { mode: 'cors' });
        if (!response.ok) {
            throw new Error('Failed to fetch Google Sheets data');
        }
        
        const csvText = await response.text();
        const newEmployees = parseCSV(csvText);
        
        processImport(newEmployees);
        
    } catch (error) {
        document.getElementById('uploadStatus').innerHTML = `
            <div style="color: orange; margin-top: 10px;">
                ⚠️ Direct import failed due to CORS restrictions.<br>
                Please manually download the CSV:<br>
                1. <a href="https://docs.google.com/spreadsheets/d/1vO-94iEtB8FAthneJ8Cx1Cm-iA-oHJiBwOPAGmsiM-4/edit" target="_blank">Open Google Sheet</a><br>
                2. File → Download → Comma Separated Values (.csv)<br>
                3. Upload the downloaded CSV file using the "Choose File" button
            </div>
        `;
    }
}

// File upload handling
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    if (!fileInput) {
        console.error('File input not found');
        return;
    }
    
    fileInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        console.log('File selected:', file.name, file.size, 'bytes');
        document.getElementById('uploadStatus').innerHTML = '<div style="color: blue;">📁 Processing file...</div>';
        
        const fileName = file.name.toLowerCase();
        
        if (fileName.endsWith('.csv')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    console.log('CSV content loaded, length:', e.target.result.length);
                    const newEmployees = parseCSV(e.target.result);
                    console.log('Parsed employees:', newEmployees.length);
                    processImport(newEmployees);
                } catch (error) {
                    console.error('CSV parsing error:', error);
                    document.getElementById('uploadStatus').innerHTML = 
                        `<div style="color: red;">✗ CSV parsing error: ${error.message}</div>`;
                }
            };
            reader.onerror = function() {
                document.getElementById('uploadStatus').innerHTML = 
                    '<div style="color: red;">✗ Error reading file</div>';
            };
            reader.readAsText(file);
        } else if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
            document.getElementById('uploadStatus').innerHTML = 
                '<div style="color: blue;">📊 For Excel files:<br>1. <a href="https://docs.google.com/spreadsheets/d/1vO-94iEtB8FAthneJ8Cx1Cm-iA-oHJiBwOPAGmsiM-4/edit" target="_blank">Open Google Sheet</a><br>2. File → Download → CSV<br>3. Upload CSV here</div>';
        } else {
            document.getElementById('uploadStatus').innerHTML = 
                '<div style="color: red;">✗ Please upload a CSV or Excel file</div>';
        }
    });
});

async function processImport(newEmployees) {
    try {
        // Create backup before changes
        backupData = {
            employees: [...employees],
            terminatedEmployees: [...terminatedEmployees]
        };
        
        const result = smartImport(newEmployees);
        
        renderEmployeeTable();
        renderTerminatedTable();
        
        // Save to database and wait for completion
        try {
            await saveEmployeesToDB([...employees, ...terminatedEmployees]);
            
            document.getElementById('uploadStatus').innerHTML = `
                <div style="color: green; margin-top: 10px;">
                    ✓ Smart import completed and saved to database:<br>
                    • ${result.added} new employees added<br>
                    • ${result.terminated} employees terminated<br>
                    • ${result.unchanged} employees unchanged<br>
                    <button class="btn" onclick="undoImport()" style="margin-top: 10px;">Undo Import</button>
                </div>
            `;
        } catch (saveError) {
            console.error('Database save failed:', saveError);
            document.getElementById('uploadStatus').innerHTML = `
                <div style="color: orange; margin-top: 10px;">
                    ⚠️ Import completed but database save failed:<br>
                    • ${result.added} new employees added<br>
                    • ${result.terminated} employees terminated<br>
                    • ${result.unchanged} employees unchanged<br>
                    <em>Changes are visible but may not persist on refresh</em><br>
                    <button class="btn" onclick="undoImport()" style="margin-top: 10px;">Undo Import</button>
                </div>
            `;
        }
        
        showTab('employees');
    } catch (error) {
        document.getElementById('uploadStatus').innerHTML = 
            `<div style="color: red; margin-top: 10px;">✗ Error processing file: ${error.message}</div>`;
    }
}

function searchEmployees() {
    const searchTerm = document.getElementById('globalSearch').value.toLowerCase();
    const rows = document.querySelectorAll('#employeeTableBody tr');
    
    rows.forEach(row => {
        const cells = row.cells;
        const searchableText = Array.from(cells).slice(1, -1).map(cell => 
            cell.textContent.toLowerCase()
        ).join(' ');
        
        const show = !searchTerm || searchableText.includes(searchTerm);
        row.style.display = show ? '' : 'none';
    });
}

function searchTerminated() {
    const searchTerm = document.getElementById('terminatedSearch').value.toLowerCase();
    const rows = document.querySelectorAll('#terminatedTableBody tr');
    
    rows.forEach(row => {
        const cells = row.cells;
        const searchableText = Array.from(cells).slice(0, -1).map(cell => 
            cell.textContent.toLowerCase()
        ).join(' ');
        
        const show = !searchTerm || searchableText.includes(searchTerm);
        row.style.display = show ? '' : 'none';
    });
}

function searchDuplicates() {
    const searchTerm = document.getElementById('duplicateSearch').value.toLowerCase();
    const rows = document.querySelectorAll('#duplicateTableBody tr');
    
    rows.forEach(row => {
        const cells = row.cells;
        const searchableText = Array.from(cells).slice(1, -1).map(cell => 
            cell.textContent.toLowerCase()
        ).join(' ');
        
        const show = !searchTerm || searchableText.includes(searchTerm);
        row.style.display = show ? '' : 'none';
    });
}

// Initialize search functionality
function initializeSearch() {
    const searchInputs = [
        { id: 'globalSearch', func: searchEmployees },
        { id: 'terminatedSearch', func: searchTerminated },
        { id: 'duplicateSearch', func: searchDuplicates }
    ];
    
    searchInputs.forEach(({ id, func }) => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('input', func);
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    func();
                }
            });
        }
    });
}

let sortDirection = {};
function sortTable(columnIndex) {
    const tbody = document.getElementById('employeeTableBody');
    const rows = Array.from(tbody.rows);
    const headers = document.querySelectorAll('th.sortable');
    
    // Update sort direction
    const direction = sortDirection[columnIndex] || 'asc';
    sortDirection[columnIndex] = direction === 'asc' ? 'desc' : 'asc';
    
    // Update sort icons
    headers.forEach((header, index) => {
        const icon = header.querySelector('.sort-icon');
        if (index === columnIndex) {
            icon.textContent = direction === 'asc' ? '↓' : '↑';
            icon.style.color = '#3b82f6';
        } else {
            icon.textContent = '↕';
            icon.style.color = '#9ca3af';
        }
    });
    
    // Adjust for checkbox column
    const actualColumnIndex = columnIndex + 1;
    
    rows.sort((a, b) => {
        let aVal = a.cells[actualColumnIndex].textContent.trim();
        let bVal = b.cells[actualColumnIndex].textContent.trim();
        
        // Handle dates and numbers
        if (columnIndex === 4) { // Employment Date
            aVal = new Date(aVal);
            bVal = new Date(bVal);
        } else if (columnIndex === 5) { // Years of Service
            aVal = parseFloat(aVal) || 0;
            bVal = parseFloat(bVal) || 0;
        }
        
        if (aVal < bVal) return direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return direction === 'asc' ? 1 : -1;
        return 0;
    });
    
    rows.forEach(row => tbody.appendChild(row));
}

function toggleSelectAllEmployees() {
    const selectAll = document.getElementById('selectAllEmployees');
    const checkboxes = document.querySelectorAll('.employee-select');
    checkboxes.forEach(cb => cb.checked = selectAll.checked);
    updateEmployeeMergeButton();
}

function updateEmployeeMergeButton() {
    const selected = document.querySelectorAll('.employee-select:checked');
    const mergeBtn = document.getElementById('mergeEmployeesBtn');
    const countSpan = document.getElementById('selectedEmployeeCount');
    
    if (mergeBtn) mergeBtn.disabled = selected.length < 2;
    if (countSpan) countSpan.textContent = `${selected.length} employees selected`;
}

function mergeSelectedEmployees() {
    const selected = document.querySelectorAll('.employee-select:checked');
    if (selected.length < 2) return;
    
    const indices = Array.from(selected).map(cb => parseInt(cb.dataset.index));
    const toMerge = indices.map(i => employees[i]);
    
    const primary = toMerge[0];
    if (confirm(`Merge ${toMerge.length} employees into: ${primary['First Name']} ${primary['Last Name']}?`)) {
        // Remove duplicates, keep primary
        indices.slice(1).sort((a, b) => b - a).forEach(index => {
            employees.splice(index, 1);
        });
        
        renderEmployeeTable();
        saveEmployeesToDB([...employees, ...terminatedEmployees]);
    }
}

function toggleSelectAll() {
    const selectAll = document.getElementById('selectAll');
    const checkboxes = document.querySelectorAll('.duplicate-select');
    checkboxes.forEach(cb => cb.checked = selectAll.checked);
    updateMergeButton();
}

function updateMergeButton() {
    const selected = document.querySelectorAll('.duplicate-select:checked');
    const mergeBtn = document.getElementById('mergeBtn');
    const countSpan = document.getElementById('selectedCount');
    
    mergeBtn.disabled = selected.length < 2;
    countSpan.textContent = `${selected.length} selected`;
}

function mergeSelectedDuplicates() {
    const selected = document.querySelectorAll('.duplicate-select:checked');
    if (selected.length < 2) return;
    
    const indices = Array.from(selected).map(cb => parseInt(cb.dataset.index));
    const duplicates = findDuplicates();
    const toMerge = indices.map(i => duplicates[i]);
    
    // Simple merge: keep first record, delete others
    const primary = toMerge[0];
    alert(`Merging ${toMerge.length} records into: ${primary['First Name']} ${primary['Last Name']}`);
    
    // Remove duplicates from arrays
    toMerge.slice(1).forEach(dup => {
        const empIndex = employees.findIndex(e => e.Email === dup.Email);
        const termIndex = terminatedEmployees.findIndex(e => e.Email === dup.Email);
        if (empIndex >= 0) employees.splice(empIndex, 1);
        if (termIndex >= 0) terminatedEmployees.splice(termIndex, 1);
    });
    
    renderEmployeeTable();
    renderTerminatedTable();
    renderDuplicateTable();
    saveEmployeesToDB([...employees, ...terminatedEmployees]);
}

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initializing...');
    loadEmployees();
    
    // Initialize search functionality
    setTimeout(() => {
        initializeSearch();
    }, 1000);
});

// Add keyboard shortcut for quick import
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 'i') {
        e.preventDefault();
        document.getElementById('fileInput').click();
    }
});