/**
 * Referral System API Wrapper
 * Handles all API calls to the Riley Referrals backend
 */

const REFERRAL_API_BASE = 'https://7paaginnvg.execute-api.us-east-2.amazonaws.com/prod/referrals';

class ReferralAPI {

    // Helper method for API calls
    static async fetch(endpoint, options = {}) {
        const url = `${REFERRAL_API_BASE}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            }
        };

        const response = await fetch(url, { ...defaultOptions, ...options });

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }

        return response.json();
    }

    // Stats
    static async getStats() {
        return this.fetch('/stats');
    }

    // Dashboard
    static async getDashboard(repId = null) {
        const query = repId ? `?repId=${repId}` : '';
        return this.fetch(`/dashboard${query}`);
    }

    // Advocates
    static async getAdvocates(repId = null) {
        const query = repId ? `?repId=${repId}` : '';
        return this.fetch(`/advocates${query}`);
    }

    static async getAdvocate(advocateId) {
        return this.fetch(`/advocates/${advocateId}`);
    }

    static async createAdvocate(data) {
        return this.fetch('/advocates', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    static async updateAdvocate(advocateId, data) {
        return this.fetch(`/advocates/${advocateId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // Leads
    static async getLeads(filters = {}) {
        const params = new URLSearchParams();
        if (filters.advocateId) params.append('advocateId', filters.advocateId);
        if (filters.repId) params.append('repId', filters.repId);
        if (filters.status) params.append('status', filters.status);

        const query = params.toString() ? `?${params.toString()}` : '';
        return this.fetch(`/leads${query}`);
    }

    static async getLead(leadId) {
        return this.fetch(`/leads/${leadId}`);
    }

    static async createLead(data) {
        return this.fetch('/leads', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    static async updateLead(leadId, data) {
        return this.fetch(`/leads/${leadId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // Payouts
    static async getPayouts(filters = {}) {
        const params = new URLSearchParams();
        if (filters.advocateId) params.append('advocateId', filters.advocateId);
        if (filters.status) params.append('status', filters.status);

        const query = params.toString() ? `?${params.toString()}` : '';
        return this.fetch(`/payouts${query}`);
    }

    static async updatePayout(payoutId, data) {
        return this.fetch(`/payouts/${payoutId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // Sales Reps
    static async getSalesReps() {
        return this.fetch('/reps');
    }
}

// Export for use in other scripts
window.ReferralAPI = ReferralAPI;
