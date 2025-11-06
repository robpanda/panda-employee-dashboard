/**
 * Referral System Frontend Application
 * Main UI logic and data handling
 */

// Global data storage
let appData = {
    advocates: [],
    leads: [],
    payouts: [],
    salesReps: [],
    stats: {},
    advocatesMap: new Map(),
    leadsMap: new Map()
};

// Initialize app on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadAllData();
});

// Load all data from API
async function loadAllData() {
    try {
        showLoading(true);

        // Load dashboard data (includes advocates, leads, payouts)
        const dashboard = await ReferralAPI.getDashboard();

        // Load stats
        const stats = await ReferralAPI.getStats();

        // Load sales reps
        const repsData = await ReferralAPI.getSalesReps();

        // Store data
        appData.advocates = dashboard.advocates || [];
        appData.leads = dashboard.leads || [];
        appData.payouts = dashboard.payouts || [];
        appData.salesReps = repsData.salesReps || [];
        appData.stats = stats;

        // Create maps for quick lookup
        appData.advocatesMap = new Map(appData.advocates.map(a => [a.advocateId, a]));
        appData.leadsMap = new Map(appData.leads.map(l => [l.leadId, l]));

        // Update UI
        updateDashboardStats();
        populateFilters();
        renderDashboard();
        renderAdvocatesTable();
        renderLeadsTable();
        renderPayoutsTable();

        showLoading(false);

    } catch (error) {
        console.error('Error loading data:', error);
        showError('Failed to load data. Please refresh the page.');
        showLoading(false);
    }
}

// Show/hide loading indicator
function showLoading(show) {
    document.getElementById('loadingIndicator').style.display = show ? 'block' : 'none';
    document.getElementById('dashboardStats').style.display = show ? 'none' : 'block';
}

// Show error message
function showError(message) {
    alert(message); // TODO: Replace with better toast notification
}

// Update dashboard stats cards
function updateDashboardStats() {
    const stats = appData.stats;

    document.getElementById('totalAdvocates').textContent = stats.totalAdvocates || 0;
    document.getElementById('activeAdvocates').textContent = stats.activeAdvocates || 0;
    document.getElementById('totalLeads').textContent = stats.totalLeads || 0;
    document.getElementById('qualifiedLeads').textContent = stats.leadsByStatus?.qualified || 0;
    document.getElementById('soldLeads').textContent = stats.leadsByStatus?.sold || 0;
    document.getElementById('pendingPayouts').textContent = formatCurrency(stats.pendingPayouts || 0);
    document.getElementById('totalPayouts').textContent = formatCurrency(stats.totalPayouts || 0);
    document.getElementById('paidPayouts').textContent = formatCurrency(stats.paidPayouts || 0);
}

// Populate filter dropdowns
function populateFilters() {
    // Sales Reps filter
    const repFilters = document.querySelectorAll('#advocateRepFilter, #leadRepFilter');
    repFilters.forEach(select => {
        select.innerHTML = '<option value="">All Sales Reps</option>';
        appData.salesReps.forEach(rep => {
            const option = document.createElement('option');
            option.value = rep.repId;
            option.textContent = rep.name || `Rep ${rep.repId}`;
            select.appendChild(option);
        });
    });

    // Advocates filter (for leads)
    const advocateFilter = document.getElementById('leadAdvocateFilter');
    advocateFilter.innerHTML = '<option value="">All Advocates</option>';
    appData.advocates.forEach(advocate => {
        const option = document.createElement('option');
        option.value = advocate.advocateId;
        option.textContent = `${advocate.firstName} ${advocate.lastName}`;
        advocateFilter.appendChild(option);
    });
}

// Render dashboard tab
function renderDashboard() {
    // Top advocates
    const topAdvocates = [...appData.advocates]
        .sort((a, b) => (b.totalEarnings || 0) - (a.totalEarnings || 0))
        .slice(0, 10);

    const topAdvocatesHtml = topAdvocates.map(a => `
        <tr onclick="showAdvocateDetail('${a.advocateId}')" style="cursor: pointer;">
            <td>${a.firstName} ${a.lastName}</td>
            <td>${a.totalLeads || 0}</td>
            <td class="text-success fw-bold">${formatCurrency(a.totalEarnings || 0)}</td>
        </tr>
    `).join('');

    document.getElementById('topAdvocatesTable').innerHTML = topAdvocatesHtml || '<tr><td colspan="3" class="text-center text-muted">No advocates yet</td></tr>';

    // Recent leads
    const recentLeads = [...appData.leads]
        .sort((a, b) => b.createdAt - a.createdAt)
        .slice(0, 10);

    const recentLeadsHtml = recentLeads.map(l => {
        const advocate = appData.advocatesMap.get(l.advocateId);
        return `
            <tr onclick="showLeadDetail('${l.leadId}')" style="cursor: pointer;">
                <td>${l.firstName} ${l.lastName}</td>
                <td>${advocate ? `${advocate.firstName} ${advocate.lastName}` : 'Unknown'}</td>
                <td>${getStatusBadge(l.status)}</td>
            </tr>
        `;
    }).join('');

    document.getElementById('recentLeadsTable').innerHTML = recentLeadsHtml || '<tr><td colspan="3" class="text-center text-muted">No leads yet</td></tr>';
}

// Render advocates table
function renderAdvocatesTable() {
    const search = document.getElementById('advocateSearch')?.value.toLowerCase() || '';
    const repFilter = document.getElementById('advocateRepFilter')?.value || '';
    const statusFilter = document.getElementById('advocateStatusFilter')?.value || '';

    let filtered = appData.advocates.filter(a => {
        const matchesSearch = !search ||
            `${a.firstName} ${a.lastName}`.toLowerCase().includes(search) ||
            a.email.toLowerCase().includes(search);
        const matchesRep = !repFilter || a.repId === repFilter;
        const matchesStatus = !statusFilter ||
            (statusFilter === 'active' && a.active) ||
            (statusFilter === 'inactive' && !a.active);

        return matchesSearch && matchesRep && matchesStatus;
    });

    const html = filtered.map(a => `
        <tr>
            <td><strong>${a.firstName} ${a.lastName}</strong></td>
            <td>${a.email}</td>
            <td>
                <code>${a.referralCode}</code>
                <button class="btn btn-sm btn-outline-secondary ms-2" onclick="copyReferralLink('${a.referralUrl}')" title="Copy link">
                    <i class="fas fa-copy"></i>
                </button>
            </td>
            <td>${a.totalLeads || 0}</td>
            <td class="text-success fw-bold">${formatCurrency(a.totalEarnings || 0)}</td>
            <td>
                ${a.active ? '<span class="badge bg-success">Active</span>' : '<span class="badge bg-secondary">Inactive</span>'}
            </td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="showAdvocateDetail('${a.advocateId}')">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        </tr>
    `).join('');

    document.getElementById('advocatesTableBody').innerHTML = html || '<tr><td colspan="7" class="text-center text-muted">No advocates found</td></tr>';
}

// Render leads table
function renderLeadsTable() {
    const search = document.getElementById('leadSearch')?.value.toLowerCase() || '';
    const statusFilter = document.getElementById('leadStatusFilter')?.value || '';
    const advocateFilter = document.getElementById('leadAdvocateFilter')?.value || '';

    let filtered = appData.leads.filter(l => {
        const matchesSearch = !search ||
            `${l.firstName} ${l.lastName}`.toLowerCase().includes(search) ||
            l.email.toLowerCase().includes(search) ||
            l.phone.includes(search);
        const matchesStatus = !statusFilter || l.status === statusFilter;
        const matchesAdvocate = !advocateFilter || l.advocateId === advocateFilter;

        return matchesSearch && matchesStatus && matchesAdvocate;
    });

    const html = filtered.map(l => {
        const advocate = appData.advocatesMap.get(l.advocateId);
        return `
            <tr>
                <td><strong>${l.firstName} ${l.lastName}</strong></td>
                <td>
                    ${l.email ? `<div><i class="fas fa-envelope me-1"></i>${l.email}</div>` : ''}
                    ${l.phone ? `<div><i class="fas fa-phone me-1"></i>${l.phone}</div>` : ''}
                </td>
                <td>${advocate ? `${advocate.firstName} ${advocate.lastName}` : 'Unknown'}</td>
                <td>${getStatusBadge(l.status)}</td>
                <td>${formatDate(l.createdAt)}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="showLeadDetail('${l.leadId}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-success" onclick="updateLeadStatus('${l.leadId}')">
                        <i class="fas fa-edit"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');

    document.getElementById('leadsTableBody').innerHTML = html || '<tr><td colspan="6" class="text-center text-muted">No leads found</td></tr>';
}

// Render payouts table
function renderPayoutsTable() {
    const statusFilter = document.getElementById('payoutStatusFilter')?.value || '';
    const typeFilter = document.getElementById('payoutTypeFilter')?.value || '';

    let filtered = appData.payouts.filter(p => {
        const matchesStatus = !statusFilter || p.status === statusFilter;
        const matchesType = !typeFilter || p.type === typeFilter;
        return matchesStatus && matchesType;
    });

    const html = filtered.map(p => {
        const advocate = appData.advocatesMap.get(p.advocateId);
        return `
            <tr>
                <td>${advocate ? `${advocate.firstName} ${advocate.lastName}` : 'Unknown'}</td>
                <td><span class="badge bg-info">${p.type}</span></td>
                <td class="text-success fw-bold">${formatCurrency(p.amount)}</td>
                <td>${getPayoutStatusBadge(p.status)}</td>
                <td>${formatDate(p.createdAt)}</td>
                <td>
                    ${p.status === 'pending' ? `
                        <button class="btn btn-sm btn-success" onclick="markPayoutPaid('${p.payoutId}')">
                            <i class="fas fa-check me-1"></i>Mark Paid
                        </button>
                    ` : `
                        <span class="text-muted"><i class="fas fa-check-circle me-1"></i>Paid</span>
                    `}
                </td>
            </tr>
        `;
    }).join('');

    document.getElementById('payoutsTableBody').innerHTML = html || '<tr><td colspan="6" class="text-center text-muted">No payouts found</td></tr>';
}

// Show/hide tabs
function showTab(tabName) {
    // Update nav
    document.querySelectorAll('#mainTabs .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    event.target.closest('.nav-link')?.classList.add('active');

    // Hide all tabs
    document.querySelectorAll('.tab-pane').forEach(tab => {
        tab.style.display = 'none';
    });

    // Show selected tab
    const tabMap = {
        'dashboard': 'dashboardTab',
        'advocates': 'advocatesTab',
        'leads': 'leadsTab',
        'payouts': 'payoutsTab'
    };

    const tabId = tabMap[tabName];
    if (tabId) {
        document.getElementById(tabId).style.display = 'block';
    }
}

// Show advocate detail modal
async function showAdvocateDetail(advocateId) {
    const modal = new bootstrap.Modal(document.getElementById('advocateDetailModal'));
    document.getElementById('advocateDetailContent').innerHTML = '<div class="text-center"><div class="spinner"></div></div>';
    modal.show();

    try {
        const data = await ReferralAPI.getAdvocate(advocateId);
        const advocate = data.advocate;
        const leads = data.leads || [];
        const payouts = data.payouts || [];

        const html = `
            <div class="row">
                <div class="col-md-6">
                    <h6 class="text-muted">Contact Information</h6>
                    <p><strong>Name:</strong> ${advocate.firstName} ${advocate.lastName}</p>
                    <p><strong>Email:</strong> ${advocate.email}</p>
                    <p><strong>Phone:</strong> ${advocate.phone || 'N/A'}</p>
                    <p><strong>Status:</strong> ${advocate.active ? '<span class="badge bg-success">Active</span>' : '<span class="badge bg-secondary">Inactive</span>'}</p>
                </div>
                <div class="col-md-6">
                    <h6 class="text-muted">Performance</h6>
                    <p><strong>Total Leads:</strong> ${advocate.totalLeads || 0}</p>
                    <p><strong>Conversions:</strong> ${advocate.totalConversions || 0}</p>
                    <p><strong>Total Earnings:</strong> <span class="text-success fw-bold">${formatCurrency(advocate.totalEarnings || 0)}</span></p>
                    <p><strong>Pending:</strong> ${formatCurrency(advocate.pendingEarnings || 0)}</p>
                    <p><strong>Paid:</strong> ${formatCurrency(advocate.paidEarnings || 0)}</p>
                </div>
            </div>

            <hr>

            <div class="mb-3">
                <h6 class="text-muted">Referral Link</h6>
                <div class="referral-link-box">
                    ${advocate.referralUrl}
                    <button class="btn btn-sm btn-panda float-end" onclick="copyReferralLink('${advocate.referralUrl}')">
                        <i class="fas fa-copy me-1"></i>Copy
                    </button>
                </div>
            </div>

            <h6 class="text-muted mt-4">Recent Leads (${leads.length})</h6>
            <div class="table-responsive">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Status</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${leads.slice(0, 5).map(l => `
                            <tr>
                                <td>${l.firstName} ${l.lastName}</td>
                                <td>${getStatusBadge(l.status)}</td>
                                <td>${formatDate(l.createdAt)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>

            <h6 class="text-muted mt-4">Payouts (${payouts.length})</h6>
            <div class="table-responsive">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Amount</th>
                            <th>Status</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${payouts.slice(0, 5).map(p => `
                            <tr>
                                <td><span class="badge bg-info">${p.type}</span></td>
                                <td class="text-success fw-bold">${formatCurrency(p.amount)}</td>
                                <td>${getPayoutStatusBadge(p.status)}</td>
                                <td>${formatDate(p.createdAt)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        document.getElementById('advocateDetailContent').innerHTML = html;

    } catch (error) {
        document.getElementById('advocateDetailContent').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>Failed to load advocate details.
            </div>
        `;
    }
}

// Show lead detail modal
async function showLeadDetail(leadId) {
    const modal = new bootstrap.Modal(document.getElementById('leadDetailModal'));
    document.getElementById('leadDetailContent').innerHTML = '<div class="text-center"><div class="spinner"></div></div>';
    modal.show();

    try {
        const data = await ReferralAPI.getLead(leadId);
        const lead = data.lead;
        const advocate = appData.advocatesMap.get(lead.advocateId);

        const html = `
            <div class="row">
                <div class="col-md-6">
                    <h6 class="text-muted">Lead Information</h6>
                    <p><strong>Name:</strong> ${lead.firstName} ${lead.lastName}</p>
                    <p><strong>Email:</strong> ${lead.email || 'N/A'}</p>
                    <p><strong>Phone:</strong> ${lead.phone || 'N/A'}</p>
                    <p><strong>Product:</strong> ${lead.product}</p>
                    <p><strong>Status:</strong> ${getStatusBadge(lead.status)}</p>
                </div>
                <div class="col-md-6">
                    <h6 class="text-muted">Source</h6>
                    <p><strong>Advocate:</strong> ${advocate ? `${advocate.firstName} ${advocate.lastName}` : 'Unknown'}</p>
                    <p><strong>Created:</strong> ${formatDate(lead.createdAt)}</p>
                    <p><strong>Updated:</strong> ${formatDate(lead.updatedAt)}</p>
                    <p><strong>Source:</strong> <span class="badge bg-secondary">${lead.source}</span></p>
                </div>
            </div>

            <hr>

            <div class="mb-3">
                <h6 class="text-muted">Address</h6>
                <p>
                    ${lead.address.street1 || ''} ${lead.address.street2 || ''}<br>
                    ${lead.address.city || ''}, ${lead.address.state || ''} ${lead.address.zip || ''}
                </p>
            </div>

            <div class="d-flex gap-2">
                <button class="btn btn-success" onclick="updateLeadStatus('${lead.leadId}')">
                    <i class="fas fa-edit me-1"></i>Update Status
                </button>
            </div>
        `;

        document.getElementById('leadDetailContent').innerHTML = html;

    } catch (error) {
        document.getElementById('leadDetailContent').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>Failed to load lead details.
            </div>
        `;
    }
}

// Update lead status
async function updateLeadStatus(leadId) {
    const lead = appData.leadsMap.get(leadId);
    if (!lead) return;

    const newStatus = prompt(`Update status for ${lead.firstName} ${lead.lastName}\n\nCurrent: ${lead.status}\n\nEnter new status (new, contacted, qualified, working, sold, lost):`, lead.status);

    if (!newStatus || newStatus === lead.status) return;

    const validStatuses = ['new', 'contacted', 'qualified', 'working', 'sold', 'lost'];
    if (!validStatuses.includes(newStatus)) {
        alert('Invalid status');
        return;
    }

    try {
        await ReferralAPI.updateLead(leadId, {
            status: newStatus,
            oldStatus: lead.status
        });

        alert(`Lead status updated to "${newStatus}"`);
        await loadAllData(); // Reload data

    } catch (error) {
        alert('Failed to update lead status');
        console.error(error);
    }
}

// Mark payout as paid
async function markPayoutPaid(payoutId) {
    if (!confirm('Mark this payout as paid?')) return;

    try {
        await ReferralAPI.updatePayout(payoutId, {
            status: 'paid'
        });

        alert('Payout marked as paid');
        await loadAllData(); // Reload data

    } catch (error) {
        alert('Failed to update payout');
        console.error(error);
    }
}

// Copy referral link to clipboard
function copyReferralLink(url) {
    navigator.clipboard.writeText(url).then(() => {
        alert('Referral link copied to clipboard!');
    }).catch(() => {
        alert('Failed to copy link');
    });
}

// Export payouts to CSV
function exportPayouts() {
    const csv = ['Advocate,Type,Amount,Status,Date'];

    appData.payouts.forEach(p => {
        const advocate = appData.advocatesMap.get(p.advocateId);
        const advocateName = advocate ? `${advocate.firstName} ${advocate.lastName}` : 'Unknown';
        csv.push(`"${advocateName}","${p.type}","${p.amount}","${p.status}","${formatDate(p.createdAt)}"`);
    });

    const blob = new Blob([csv.join('\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `payouts_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
}

// Filter functions
function filterAdvocates() {
    renderAdvocatesTable();
}

function filterLeads() {
    renderLeadsTable();
}

function filterPayouts() {
    renderPayoutsTable();
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(timestamp) {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function getStatusBadge(status) {
    const badges = {
        'new': '<span class="badge-status badge-new">New</span>',
        'contacted': '<span class="badge-status badge-contacted">Contacted</span>',
        'qualified': '<span class="badge-status badge-qualified">Qualified</span>',
        'working': '<span class="badge-status badge-working">Working</span>',
        'sold': '<span class="badge-status badge-sold">Sold</span>',
        'lost': '<span class="badge-status badge-lost">Lost</span>'
    };
    return badges[status] || `<span class="badge bg-secondary">${status}</span>`;
}

function getPayoutStatusBadge(status) {
    return status === 'pending'
        ? '<span class="badge-status badge-pending">Pending</span>'
        : '<span class="badge-status badge-paid">Paid</span>';
}

// Placeholder functions
function showAddAdvocateModal() {
    alert('Add Advocate feature coming soon!');
}

function showAddLeadModal() {
    alert('Add Lead feature coming soon!');
}

function logout() {
    sessionStorage.removeItem('pandaAdmin');
    sessionStorage.removeItem('adminUser');
    window.location.href = '/login.html';
}
