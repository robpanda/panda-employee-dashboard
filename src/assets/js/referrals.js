let referrals = [];
let advocates = [];
let salesReps = [];
let contacts = [];
let pendingPayments = [];
const GTR_API_BASE = 'https://restapi.getthereferral.com/v2';
const GTR_API_KEY = 'YOUR_API_KEY'; // Replace with actual API key

// Debug function to test API connection
function testGTRConnection() {
    console.log('Testing GTR API connection...');
    console.log('API Base:', GTR_API_BASE);
    console.log('API Key configured:', GTR_API_KEY !== 'YOUR_API_KEY');
    
    if (GTR_API_KEY === 'YOUR_API_KEY') {
        console.warn('⚠️ GTR API Key not configured. Please update GTR_API_KEY variable.');
        document.getElementById('overview').innerHTML += '<div style="background: #fff3cd; padding: 20px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #ffc107;"><strong>⚠️ API Configuration Required:</strong><br>GetTheReferral API key not configured. Please update the GTR_API_KEY in the JavaScript file.</div>';
        return false;
    }
    return true;
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
    
    if (tabName === 'referrals') {
        renderReferralTable();
    } else if (tabName === 'advocates') {
        renderAdvocateTable();
    } else if (tabName === 'payments') {
        renderPaymentTable();
    }
}

function addReferral(referralData) {
    const newReferral = {
        id: Date.now(),
        date: new Date().toISOString().split('T')[0],
        status: 'Pending',
        reward: 0,
        ...referralData
    };
    
    referrals.push(newReferral);
    updateStats();
    saveReferralsToStorage();
    
    return newReferral;
}

function updateReferralStatus(id, status, reward = 0) {
    const referral = referrals.find(r => r.id === id);
    if (referral) {
        referral.status = status;
        if (status === 'Converted') {
            referral.reward = reward;
        }
        updateStats();
        saveReferralsToStorage();
        renderReferralTable();
    }
}

function deleteReferral(id) {
    referrals = referrals.filter(r => r.id !== id);
    updateStats();
    saveReferralsToStorage();
    renderReferralTable();
}

function updateStats() {
    const total = referrals.length;
    const pending = referrals.filter(r => r.status === 'Pending').length;
    const converted = referrals.filter(r => r.status === 'Converted').length;
    const totalRewards = referrals.reduce((sum, r) => sum + (r.reward || 0), 0);
    
    document.getElementById('totalReferrals').textContent = total;
    document.getElementById('pendingReferrals').textContent = pending;
    document.getElementById('convertedReferrals').textContent = converted;
    document.getElementById('totalRewards').textContent = `$${totalRewards.toLocaleString()}`;
}

function updatePendingPaymentsStats() {
    const totalPending = pendingPayments.reduce((sum, payment) => sum + (payment.amount || 0), 0);
    const pendingCount = pendingPayments.length;
    
    // Update rewards stat to show pending payments
    if (document.getElementById('totalRewards')) {
        document.getElementById('totalRewards').textContent = `$${totalPending.toLocaleString()} Pending`;
    }
}

function renderReferralTable() {
    const tbody = document.getElementById('referralTableBody');
    tbody.innerHTML = '';
    
    referrals.forEach((referral) => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${referral.date}</td>
            <td>${referral.referrerName}</td>
            <td>${referral.customerName}</td>
            <td>${referral.customerPhone}</td>
            <td>${referral.customerEmail || 'N/A'}</td>
            <td>${referral.customerAddress}</td>
            <td><span class="status-${referral.status.toLowerCase()}">${referral.status}</span></td>
            <td>$${referral.reward || 0}</td>
            <td>
                ${referral.status === 'Pending' ? 
                    `<button class="action-btn convert-btn" onclick="convertReferral(${referral.id})">Convert</button>` : ''}
                <button class="action-btn edit-btn" onclick="editReferral(${referral.id})">Edit</button>
                <button class="action-btn delete-btn" onclick="deleteReferral(${referral.id})">Delete</button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

function renderAdvocateTable() {
    const tbody = document.getElementById('advocateTableBody');
    tbody.innerHTML = '';
    
    advocates.forEach((advocate) => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${advocate.name || 'N/A'}</td>
            <td>${advocate.email || 'N/A'}</td>
            <td>${advocate.phone || 'N/A'}</td>
            <td><span class="status-${advocate.status?.toLowerCase() || 'active'}">${advocate.status || 'Active'}</span></td>
            <td>${advocate.total_referrals || 0}</td>
            <td>$${advocate.total_rewards || 0}</td>
        `;
        
        tbody.appendChild(row);
    });
}

function renderPaymentTable() {
    const tbody = document.getElementById('paymentTableBody');
    tbody.innerHTML = '';
    
    pendingPayments.forEach((payment) => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${payment.advocate_name || 'N/A'}</td>
            <td>$${payment.amount || 0}</td>
            <td>${payment.lead_name || 'N/A'}</td>
            <td>${payment.date || 'N/A'}</td>
            <td><span class="status-pending">Pending</span></td>
        `;
        
        tbody.appendChild(row);
    });
}

function convertReferral(id) {
    const reward = prompt('Enter reward amount:', '100');
    if (reward !== null && !isNaN(reward)) {
        updateReferralStatus(id, 'Converted', parseInt(reward));
    }
}

function editReferral(id) {
    const referral = referrals.find(r => r.id === id);
    if (!referral) return;
    
    const newCustomerName = prompt('Customer Name:', referral.customerName);
    if (newCustomerName !== null) referral.customerName = newCustomerName;
    
    const newPhone = prompt('Customer Phone:', referral.customerPhone);
    if (newPhone !== null) referral.customerPhone = newPhone;
    
    const newEmail = prompt('Customer Email:', referral.customerEmail || '');
    if (newEmail !== null) referral.customerEmail = newEmail;
    
    const newAddress = prompt('Customer Address:', referral.customerAddress);
    if (newAddress !== null) referral.customerAddress = newAddress;
    
    saveReferralsToStorage();
    renderReferralTable();
}

async function loadLeadsFromGTR() {
    if (!testGTRConnection()) return;
    
    try {
        console.log('Fetching leads from GTR...');
        const response = await fetch(`${GTR_API_BASE}/leads`, {
            headers: {
                'Authorization': `Bearer ${GTR_API_KEY}`,
                'Content-Type': 'application/json'
            }
        });
        
        console.log('GTR Leads Response Status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('GTR Leads Data:', data);
        
        if (data.data) {
            const gtrReferrals = data.data.map(lead => ({
                id: lead.id,
                date: lead.created_at?.split('T')[0] || new Date().toISOString().split('T')[0],
                referrerName: lead.advocate?.name || 'Unknown',
                customerName: `${lead.first_name || ''} ${lead.last_name || ''}`.trim(),
                customerPhone: lead.phone || '',
                customerEmail: lead.email || '',
                customerAddress: `${lead.address || ''} ${lead.city || ''} ${lead.state || ''}`.trim(),
                status: lead.status === 'converted' ? 'Converted' : 'Pending',
                reward: lead.reward_amount || 0,
                referralSource: 'GetTheReferral'
            }));
            referrals = gtrReferrals;
            console.log('Processed referrals:', referrals.length);
            updateStats();
        }
    } catch (error) {
        console.error('Error loading GTR leads:', error);
        document.getElementById('overview').innerHTML += `<div style="background: #f8d7da; padding: 20px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #dc3545;"><strong>❌ GTR API Error:</strong><br>${error.message}</div>`;
    }
}

async function loadAdvocatesFromGTR() {
    try {
        const response = await fetch(`${GTR_API_BASE}/advocates`, {
            headers: {
                'Authorization': `Bearer ${GTR_API_KEY}`,
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        if (data.data) {
            advocates = data.data;
            populateAdvocateDropdown();
        }
    } catch (error) {
        console.error('Error loading GTR advocates:', error);
    }
}

async function loadSalesRepsFromGTR() {
    try {
        const response = await fetch(`${GTR_API_BASE}/salesreps`, {
            headers: {
                'Authorization': `Bearer ${GTR_API_KEY}`,
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        if (data.data) {
            salesReps = data.data;
        }
    } catch (error) {
        console.error('Error loading GTR sales reps:', error);
    }
}

async function loadContactsFromGTR() {
    try {
        const response = await fetch(`${GTR_API_BASE}/contacts`, {
            headers: {
                'Authorization': `Bearer ${GTR_API_KEY}`,
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        if (data.data) {
            contacts = data.data;
        }
    } catch (error) {
        console.error('Error loading GTR contacts:', error);
    }
}

async function loadPendingPaymentsFromGTR() {
    try {
        const response = await fetch(`${GTR_API_BASE}/payments/pending`, {
            headers: {
                'Authorization': `Bearer ${GTR_API_KEY}`,
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        if (data.data) {
            pendingPayments = data.data;
            updatePendingPaymentsStats();
        }
    } catch (error) {
        console.error('Error loading GTR pending payments:', error);
    }
}

function saveReferralsToStorage() {
    localStorage.setItem('pandaReferrals', JSON.stringify(referrals));
}

function loadReferralsFromStorage() {
    const stored = localStorage.getItem('pandaReferrals');
    if (stored) {
        referrals = JSON.parse(stored);
        updateStats();
    }
    loadAllGTRData();
}

async function loadAllGTRData() {
    await Promise.all([
        loadLeadsFromGTR(),
        loadAdvocatesFromGTR(),
        loadSalesRepsFromGTR(),
        loadContactsFromGTR(),
        loadPendingPaymentsFromGTR()
    ]);
}

function populateAdvocateDropdown() {
    const referrerSelect = document.getElementById('referrerName');
    if (referrerSelect && advocates.length > 0) {
        referrerSelect.innerHTML = '<option value="">Select Advocate</option>';
        advocates.forEach(advocate => {
            const option = document.createElement('option');
            option.value = advocate.name;
            option.textContent = `${advocate.name} (${advocate.email})`;
            referrerSelect.appendChild(option);
        });
    }
}

// Form submission
document.addEventListener('DOMContentLoaded', function() {
    console.log('Referrals initializing...');
    testGTRConnection();
    loadReferralsFromStorage();
    
    const form = document.getElementById('referralForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                referrerName: document.getElementById('referrerName').value,
                customerName: document.getElementById('customerName').value,
                customerPhone: document.getElementById('customerPhone').value,
                customerEmail: document.getElementById('customerEmail').value,
                customerAddress: document.getElementById('customerAddress').value,
                referralSource: document.getElementById('referralSource').value,
                expectedValue: parseInt(document.getElementById('expectedValue').value) || 0
            };
            
            addReferral(formData);
            form.reset();
            
            alert('Referral added successfully!');
            showTab('referrals');
        });
    }
});