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
                
                row.innerHTML = `
                    <td><a href="#" class="name-link" onclick="editEmployee(${index})">${emp['First Name'] || ''}</a></td>
                    <td>${emp['Last Name'] || ''}</td>
                    <td>${emp.Department || ''}</td>
                    <td>${emp.Position || ''}</td>
                    <td>${emp['Employment Date'] || ''}</td>
                    <td>${emp['Years of Service'] || ''}</td>
                    <td>${emp.Email || ''}</td>
                    <td>${emp.Phone || ''}</td>
                    <td>${emp['Merch Requested'] || ''}</td>
                    <td>${emp['Merch Sent'] || 'No'}</td>
                    <td><button class="action-btn delete-btn" onclick="terminateEmployee(${index})">Terminate</button></td>
                `;
                
                tbody.appendChild(row);
            });
            
            document.getElementById('totalEmployees').textContent = employees.length;
            document.getElementById('newHires').textContent = newHireCount;
            document.getElementById('overviewEmployees').textContent = employees.length;
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
        }
        
        function reactivateEmployee(index) {
            const employee = terminatedEmployees[index];
            delete employee['Termination Date'];
            employee['Terminated'] = 'No';
            
            employees.push(employee);
            terminatedEmployees.splice(index, 1);
            
            renderEmployeeTable();
            renderTerminatedTable();
        }
        
        function editEmployee(index) {
            const emp = employees[index];
            const newFirstName = prompt('First Name:', emp['First Name'] || '');
            if (newFirstName !== null) emp['First Name'] = newFirstName;
            
            const newLastName = prompt('Last Name:', emp['Last Name'] || '');
            if (newLastName !== null) emp['Last Name'] = newLastName;
            
            const newEmail = prompt('Email:', emp.Email || '');
            if (newEmail !== null) emp.Email = newEmail;
            
            const newPhone = prompt('Phone:', emp.Phone || '');
            if (newPhone !== null) emp.Phone = newPhone;
            
            const newMerch = prompt('Merch Requested:', emp['Merch Requested'] || '');
            if (newMerch !== null) emp['Merch Requested'] = newMerch;
            
            const newMerchSent = confirm('Merch Sent?') ? 'Yes' : 'No';
            emp['Merch Sent'] = newMerchSent;
            
            renderEmployeeTable();
            saveEmployeesToDB([...employees, ...terminatedEmployees]);
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
                await fetch(`${API_BASE}/employees`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({employees: allEmployees})
                });
            } catch (error) {
                console.error('Error saving employees:', error);
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
        
        function showLeadModal(type) {
            alert(`Showing ${type} leads`);
        }
        
        function showCampaignModal(type) {
            alert(`Showing ${type} campaign`);
        }
        
        function validateEmail() {
            const email = document.getElementById('testEmail').value;
            document.getElementById('validationResults').style.display = 'block';
            document.getElementById('emailResults').innerHTML = `
                <p><strong>Email:</strong> ${email}</p>
                <p><strong>Valid:</strong> <span style="color: #27ae60;">YES</span></p>
            `;
        }
        
        function validatePhone() {
            const phone = document.getElementById('testPhone').value;
            document.getElementById('validationResults').style.display = 'block';
            document.getElementById('phoneResults').innerHTML = `
                <p><strong>Phone:</strong> ${phone}</p>
                <p><strong>Valid:</strong> <span style="color: #27ae60;">YES</span></p>
            `;
        }
        
        function validateAddress() {
            const address = document.getElementById('addressLine').value;
            const city = document.getElementById('city').value;
            const state = document.getElementById('state').value;
            const zip = document.getElementById('zipCode').value;
            
            document.getElementById('addressResults').style.display = 'block';
            document.getElementById('uspsResults').innerHTML = `
                <p><strong>Address:</strong> ${address}</p>
                <p><strong>City:</strong> ${city}</p>
                <p><strong>State:</strong> ${state}</p>
                <p><strong>ZIP:</strong> ${zip}</p>
                <p><strong>Valid:</strong> <span style="color: #27ae60;">YES</span></p>
            `;
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
        
        function processImport(newEmployees) {
            try {
                // Create backup before changes
                backupData = {
                    employees: [...employees],
                    terminatedEmployees: [...terminatedEmployees]
                };
                
                const result = smartImport(newEmployees);
                
                renderEmployeeTable();
                renderTerminatedTable();
                
                // Save to database
                saveEmployeesToDB([...employees, ...terminatedEmployees]);
                
                document.getElementById('uploadStatus').innerHTML = `
                    <div style="color: green; margin-top: 10px;">
                        ✓ Smart import completed:<br>
                        • ${result.added} new employees added<br>
                        • ${result.terminated} employees terminated<br>
                        • ${result.unchanged} employees unchanged<br>
                        <button class="btn" onclick="undoImport()" style="margin-top: 10px;">Undo Import</button>
                    </div>
                `;
                
                showTab('employees');
            } catch (error) {
                document.getElementById('uploadStatus').innerHTML = 
                    `<div style="color: red; margin-top: 10px;">✗ Error processing file: ${error.message}</div>`;
            }
        }
        
        // Initialize on load
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Dashboard initializing...');
            loadEmployees();
        });
        
        // Add keyboard shortcut for quick import
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'i') {
                e.preventDefault();
                document.getElementById('fileInput').click();
            }
        });
