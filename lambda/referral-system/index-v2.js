const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, GetCommand, PutCommand, UpdateCommand, QueryCommand, ScanCommand } = require('@aws-sdk/lib-dynamodb');

const client = new DynamoDBClient({ region: 'us-east-2' });
const dynamodb = DynamoDBDocumentClient.from(client);

const TABLES = {
    advocates: 'panda-advocates',
    salesReps: 'panda-sales-reps',
    salesManagers: 'panda-sales-managers',
    leads: 'panda-referral-leads',
    payouts: 'panda-referral-payouts'
};

const CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
};

// Payout tiers
const PAYOUT_TIERS = {
    'signup': 25.00,      // New advocate signup
    'qualified': 50.00,   // Good working lead
    'sold': 150.00        // Deal closed
};

exports.handler = async (event) => {
    console.log('Event:', JSON.stringify(event));

    // Handle OPTIONS for CORS
    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers: CORS_HEADERS,
            body: ''
        };
    }

    const path = event.path;
    const method = event.httpMethod;

    try {
        let response;

        // Routes
        if (path === '/referral/advocates' && method === 'GET') {
            response = await getAdvocates(event);
        } else if (path === '/referral/advocates' && method === 'POST') {
            response = await createAdvocate(event);
        } else if (path.startsWith('/referral/advocates/') && method === 'GET') {
            response = await getAdvocate(event);
        } else if (path.startsWith('/referral/advocates/') && method === 'PUT') {
            response = await updateAdvocate(event);
        } else if (path === '/referral/leads' && method === 'GET') {
            response = await getLeads(event);
        } else if (path === '/referral/leads' && method === 'POST') {
            response = await createLead(event);
        } else if (path.startsWith('/referral/leads/') && method === 'GET') {
            response = await getLead(event);
        } else if (path.startsWith('/referral/leads/') && method === 'PUT') {
            response = await updateLead(event);
        } else if (path === '/referral/payouts' && method === 'GET') {
            response = await getPayouts(event);
        } else if (path.startsWith('/referral/payouts/') && method === 'PUT') {
            response = await updatePayout(event);
        } else if (path === '/referral/reps' && method === 'GET') {
            response = await getSalesReps(event);
        } else if (path === '/referral/stats' && method === 'GET') {
            response = await getStats(event);
        } else if (path === '/referral/dashboard' && method === 'GET') {
            response = await getDashboard(event);
        } else {
            response = { statusCode: 404, body: { error: 'Not found' } };
        }

        return {
            statusCode: response.statusCode || 200,
            headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
            body: JSON.stringify(response.body || response)
        };

    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
            body: JSON.stringify({ error: error.message })
        };
    }
};

// Get all advocates (with optional filters)
async function getAdvocates(event) {
    const queryParams = event.queryStringParameters || {};
    const repId = queryParams.repId;

    let params;
    if (repId) {
        params = {
            TableName: TABLES.advocates,
            IndexName: 'rep-index',
            KeyConditionExpression: 'repId = :repId',
            ExpressionAttributeValues: { ':repId': repId }
        };
        const result = await dynamodb.send(new QueryCommand(params));
        return { advocates: result.Items };
    } else {
        params = { TableName: TABLES.advocates };
        const result = await dynamodb.scan(params).promise();
        return { advocates: result.Items };
    }
}

// Get single advocate
async function getAdvocate(event) {
    const advocateId = event.path.split('/').pop();

    const params = {
        TableName: TABLES.advocates,
        Key: { advocateId }
    };

    const result = await dynamodb.get(params).promise();
    if (!result.Item) {
        return { statusCode: 404, body: { error: 'Advocate not found' } };
    }

    // Get advocate's leads
    const leadsParams = {
        TableName: TABLES.leads,
        IndexName: 'advocate-index',
        KeyConditionExpression: 'advocateId = :advocateId',
        ExpressionAttributeValues: { ':advocateId': advocateId }
    };
    const leadsResult = await dynamodb.query(leadsParams).promise();

    // Get advocate's payouts
    const payoutsParams = {
        TableName: TABLES.payouts,
        IndexName: 'advocate-index',
        KeyConditionExpression: 'advocateId = :advocateId',
        ExpressionAttributeValues: { ':advocateId': advocateId }
    };
    const payoutsResult = await dynamodb.query(payoutsParams).promise();

    return {
        advocate: result.Item,
        leads: leadsResult.Items,
        payouts: payoutsResult.Items
    };
}

// Create new advocate
async function createAdvocate(event) {
    const data = JSON.parse(event.body);
    const advocateId = `ADV${Date.now()}`;
    const referralCode = generateReferralCode();

    const item = {
        advocateId,
        repId: data.repId,
        email: data.email,
        firstName: data.firstName,
        lastName: data.lastName,
        phone: data.phone || '',
        address: data.address || {},
        referralCode,
        referralUrl: `https://pandaadmin.com/refer/${referralCode}`,
        totalEarnings: 0,
        pendingEarnings: 0,
        paidEarnings: 0,
        totalLeads: 0,
        totalConversions: 0,
        createdAt: Date.now(),
        updatedAt: Date.now(),
        active: true,
        emailVerified: false,
        source: 'MANUAL'
    };

    await dynamodb.put({
        TableName: TABLES.advocates,
        Item: item
    }).promise();

    // Create signup payout
    await createPayoutRecord(advocateId, null, 'signup', PAYOUT_TIERS.signup);

    return { advocate: item };
}

// Update advocate
async function updateAdvocate(event) {
    const advocateId = event.path.split('/').pop();
    const data = JSON.parse(event.body);

    const updateExpressions = [];
    const attributeValues = {};
    const attributeNames = {};

    Object.keys(data).forEach((key, index) => {
        if (key !== 'advocateId') {
            const attr = `:val${index}`;
            const name = `#${key}`;
            updateExpressions.push(`${name} = ${attr}`);
            attributeValues[attr] = data[key];
            attributeNames[name] = key;
        }
    });

    updateExpressions.push('#updatedAt = :updatedAt');
    attributeValues[':updatedAt'] = Date.now();
    attributeNames['#updatedAt'] = 'updatedAt';

    const params = {
        TableName: TABLES.advocates,
        Key: { advocateId },
        UpdateExpression: `SET ${updateExpressions.join(', ')}`,
        ExpressionAttributeValues: attributeValues,
        ExpressionAttributeNames: attributeNames,
        ReturnValues: 'ALL_NEW'
    };

    const result = await dynamodb.update(params).promise();
    return { advocate: result.Attributes };
}

// Get all leads (with optional filters)
async function getLeads(event) {
    const queryParams = event.queryStringParameters || {};
    const advocateId = queryParams.advocateId;
    const repId = queryParams.repId;
    const status = queryParams.status;

    let params;

    if (advocateId) {
        params = {
            TableName: TABLES.leads,
            IndexName: 'advocate-index',
            KeyConditionExpression: 'advocateId = :advocateId',
            ExpressionAttributeValues: { ':advocateId': advocateId }
        };
        const result = await dynamodb.query(params).promise();
        return { leads: result.Items };
    } else if (repId) {
        params = {
            TableName: TABLES.leads,
            IndexName: 'rep-index',
            KeyConditionExpression: 'repId = :repId',
            ExpressionAttributeValues: { ':repId': repId }
        };
        const result = await dynamodb.query(params).promise();
        return { leads: result.Items };
    } else if (status) {
        params = {
            TableName: TABLES.leads,
            IndexName: 'status-index',
            KeyConditionExpression: '#status = :status',
            ExpressionAttributeNames: { '#status': 'status' },
            ExpressionAttributeValues: { ':status': status }
        };
        const result = await dynamodb.query(params).promise();
        return { leads: result.Items };
    } else {
        params = { TableName: TABLES.leads };
        const result = await dynamodb.scan(params).promise();
        return { leads: result.Items };
    }
}

// Get single lead
async function getLead(event) {
    const leadId = event.path.split('/').pop();

    const params = {
        TableName: TABLES.leads,
        Key: { leadId }
    };

    const result = await dynamodb.get(params).promise();
    if (!result.Item) {
        return { statusCode: 404, body: { error: 'Lead not found' } };
    }

    return { lead: result.Item };
}

// Create new lead
async function createLead(event) {
    const data = JSON.parse(event.body);
    const leadId = `LEAD${Date.now()}`;

    const item = {
        leadId,
        advocateId: data.advocateId,
        repId: data.repId,
        status: 'new',
        email: data.email || '',
        firstName: data.firstName,
        lastName: data.lastName,
        phone: data.phone || '',
        address: data.address || {},
        product: data.product || 'Roofing Referral',
        createdAt: Date.now(),
        updatedAt: Date.now(),
        source: data.source || 'MANUAL',
        notes: []
    };

    await dynamodb.put({
        TableName: TABLES.leads,
        Item: item
    }).promise();

    // Update advocate lead count
    await updateAdvocateStats(data.advocateId, 'totalLeads', 1);

    return { lead: item };
}

// Update lead status and trigger payouts
async function updateLead(event) {
    const leadId = event.path.split('/').pop();
    const data = JSON.parse(event.body);
    const oldStatus = data.oldStatus;
    const newStatus = data.status;

    // Get current lead
    const getParams = {
        TableName: TABLES.leads,
        Key: { leadId }
    };
    const currentLead = await dynamodb.get(getParams).promise();

    if (!currentLead.Item) {
        return { statusCode: 404, body: { error: 'Lead not found' } };
    }

    // Update lead
    const updateExpressions = [];
    const attributeValues = {};
    const attributeNames = {};

    Object.keys(data).forEach((key, index) => {
        if (key !== 'leadId' && key !== 'oldStatus') {
            const attr = `:val${index}`;
            const name = `#${key}`;
            updateExpressions.push(`${name} = ${attr}`);
            attributeValues[attr] = data[key];
            attributeNames[name] = key;
        }
    });

    updateExpressions.push('#updatedAt = :updatedAt');
    attributeValues[':updatedAt'] = Date.now();
    attributeNames['#updatedAt'] = 'updatedAt';

    const updateParams = {
        TableName: TABLES.leads,
        Key: { leadId },
        UpdateExpression: `SET ${updateExpressions.join(', ')}`,
        ExpressionAttributeValues: attributeValues,
        ExpressionAttributeNames: attributeNames,
        ReturnValues: 'ALL_NEW'
    };

    const result = await dynamodb.update(updateParams).promise();

    // Handle payout creation based on status change
    if (newStatus === 'qualified' && oldStatus !== 'qualified') {
        await createPayoutRecord(currentLead.Item.advocateId, leadId, 'qualified', PAYOUT_TIERS.qualified);
        await updateAdvocateStats(currentLead.Item.advocateId, 'pendingEarnings', PAYOUT_TIERS.qualified);
    } else if (newStatus === 'sold' && oldStatus !== 'sold') {
        await createPayoutRecord(currentLead.Item.advocateId, leadId, 'sold', PAYOUT_TIERS.sold);
        await updateAdvocateStats(currentLead.Item.advocateId, 'totalConversions', 1);
        await updateAdvocateStats(currentLead.Item.advocateId, 'pendingEarnings', PAYOUT_TIERS.sold);
    }

    return { lead: result.Attributes };
}

// Get payouts (with optional filters)
async function getPayouts(event) {
    const queryParams = event.queryStringParameters || {};
    const advocateId = queryParams.advocateId;
    const status = queryParams.status;

    let params;

    if (advocateId) {
        params = {
            TableName: TABLES.payouts,
            IndexName: 'advocate-index',
            KeyConditionExpression: 'advocateId = :advocateId',
            ExpressionAttributeValues: { ':advocateId': advocateId }
        };
        const result = await dynamodb.query(params).promise();
        return { payouts: result.Items };
    } else if (status) {
        params = {
            TableName: TABLES.payouts,
            IndexName: 'status-index',
            KeyConditionExpression: '#status = :status',
            ExpressionAttributeNames: { '#status': 'status' },
            ExpressionAttributeValues: { ':status': status }
        };
        const result = await dynamodb.query(params).promise();
        return { payouts: result.Items };
    } else {
        params = { TableName: TABLES.payouts };
        const result = await dynamodb.scan(params).promise();
        return { payouts: result.Items };
    }
}

// Update payout status
async function updatePayout(event) {
    const payoutId = event.path.split('/').pop();
    const data = JSON.parse(event.body);

    // Get current payout
    const getParams = {
        TableName: TABLES.payouts,
        Key: { payoutId }
    };
    const currentPayout = await dynamodb.get(getParams).promise();

    if (!currentPayout.Item) {
        return { statusCode: 404, body: { error: 'Payout not found' } };
    }

    // Update payout
    const params = {
        TableName: TABLES.payouts,
        Key: { payoutId },
        UpdateExpression: 'SET #status = :status, #updatedAt = :updatedAt, #paidAt = :paidAt',
        ExpressionAttributeNames: {
            '#status': 'status',
            '#updatedAt': 'updatedAt',
            '#paidAt': 'paidAt'
        },
        ExpressionAttributeValues: {
            ':status': data.status,
            ':updatedAt': Date.now(),
            ':paidAt': data.status === 'paid' ? Date.now() : null
        },
        ReturnValues: 'ALL_NEW'
    };

    const result = await dynamodb.update(params).promise();

    // Update advocate earnings if status changed to paid
    if (data.status === 'paid' && currentPayout.Item.status !== 'paid') {
        const amount = currentPayout.Item.amount;
        await updateAdvocateStats(currentPayout.Item.advocateId, 'paidEarnings', amount);
        await updateAdvocateStats(currentPayout.Item.advocateId, 'pendingEarnings', -amount);
    }

    return { payout: result.Attributes };
}

// Get sales reps
async function getSalesReps(event) {
    const params = { TableName: TABLES.salesReps };
    const result = await dynamodb.scan(params).promise();
    return { salesReps: result.Items };
}

// Get overall stats
async function getStats(event) {
    const [advocates, leads, payouts] = await Promise.all([
        dynamodb.scan({ TableName: TABLES.advocates }).promise(),
        dynamodb.scan({ TableName: TABLES.leads }).promise(),
        dynamodb.scan({ TableName: TABLES.payouts }).promise()
    ]);

    const stats = {
        totalAdvocates: advocates.Items.length,
        activeAdvocates: advocates.Items.filter(a => a.active).length,
        totalLeads: leads.Items.length,
        leadsByStatus: {},
        totalPayouts: payouts.Items.reduce((sum, p) => sum + (p.amount || 0), 0),
        pendingPayouts: payouts.Items.filter(p => p.status === 'pending').reduce((sum, p) => sum + (p.amount || 0), 0),
        paidPayouts: payouts.Items.filter(p => p.status === 'paid').reduce((sum, p) => sum + (p.amount || 0), 0)
    };

    // Count leads by status
    leads.Items.forEach(lead => {
        stats.leadsByStatus[lead.status] = (stats.leadsByStatus[lead.status] || 0) + 1;
    });

    return stats;
}

// Get dashboard data
async function getDashboard(event) {
    const queryParams = event.queryStringParameters || {};
    const repId = queryParams.repId;

    let advocatesParams = { TableName: TABLES.advocates };
    let leadsParams = { TableName: TABLES.leads };
    let payoutsParams = { TableName: TABLES.payouts };

    // Filter by rep if specified
    if (repId) {
        advocatesParams = {
            TableName: TABLES.advocates,
            IndexName: 'rep-index',
            KeyConditionExpression: 'repId = :repId',
            ExpressionAttributeValues: { ':repId': repId }
        };
        leadsParams = {
            TableName: TABLES.leads,
            IndexName: 'rep-index',
            KeyConditionExpression: 'repId = :repId',
            ExpressionAttributeValues: { ':repId': repId }
        };
    }

    const [advocates, leads, payouts] = await Promise.all([
        repId ? dynamodb.query(advocatesParams).promise() : dynamodb.scan(advocatesParams).promise(),
        repId ? dynamodb.query(leadsParams).promise() : dynamodb.scan(leadsParams).promise(),
        dynamodb.scan(payoutsParams).promise()
    ]);

    return {
        advocates: advocates.Items,
        leads: leads.Items,
        payouts: payouts.Items,
        stats: {
            totalAdvocates: advocates.Items.length,
            totalLeads: leads.Items.length,
            totalEarnings: advocates.Items.reduce((sum, a) => sum + (a.totalEarnings || 0), 0),
            pendingPayouts: payouts.Items.filter(p => p.status === 'pending').length,
            paidPayouts: payouts.Items.filter(p => p.status === 'paid').length
        }
    };
}

// Helper functions
function generateReferralCode() {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789';
    let code = '';
    for (let i = 0; i < 6; i++) {
        code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return code;
}

async function createPayoutRecord(advocateId, leadId, type, amount) {
    const payoutId = `PAY${Date.now()}_${type}`;
    const item = {
        payoutId,
        advocateId,
        leadId,
        amount,
        type,
        status: 'pending',
        createdAt: Date.now(),
        updatedAt: Date.now(),
        notes: `${type} payout`
    };

    await dynamodb.put({
        TableName: TABLES.payouts,
        Item: item
    }).promise();

    return item;
}

async function updateAdvocateStats(advocateId, field, value) {
    const params = {
        TableName: TABLES.advocates,
        Key: { advocateId },
        UpdateExpression: `ADD #field :value SET #updatedAt = :updatedAt`,
        ExpressionAttributeNames: {
            '#field': field,
            '#updatedAt': 'updatedAt'
        },
        ExpressionAttributeValues: {
            ':value': value,
            ':updatedAt': Date.now()
        }
    };

    await dynamodb.update(params).promise();
}
