// Using AWS SDK v3 for Node.js 18+
const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, GetCommand, PutCommand, UpdateCommand, QueryCommand, ScanCommand } = require('@aws-sdk/lib-dynamodb');

const client = new DynamoDBClient({ region: 'us-east-2' });
const ddb = DynamoDBDocumentClient.from(client);

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

const PAYOUT_TIERS = {
    'signup': 25.00,
    'qualified': 50.00,
    'sold': 150.00
};

exports.handler = async (event) => {
    console.log('Event:', JSON.stringify(event));

    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 200, headers: CORS_HEADERS, body: '' };
    }

    const path = event.path;
    const method = event.httpMethod;

    try {
        let response;

        if (path === '/referral/advocates' && method === 'GET') {
            response = await getAdvocates(event);
        } else if (path === '/referral/leads' && method === 'GET') {
            response = await getLeads(event);
        } else if (path === '/referral/payouts' && method === 'GET') {
            response = await getPayouts(event);
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

async function getAdvocates(event) {
    const queryParams = event.queryStringParameters || {};
    const repId = queryParams.repId;

    if (repId) {
        const params = {
            TableName: TABLES.advocates,
            IndexName: 'rep-index',
            KeyConditionExpression: 'repId = :repId',
            ExpressionAttributeValues: { ':repId': repId }
        };
        const result = await ddb.send(new QueryCommand(params));
        return { advocates: result.Items || [] };
    } else {
        const result = await ddb.send(new ScanCommand({ TableName: TABLES.advocates }));
        return { advocates: result.Items || [] };
    }
}

async function getLeads(event) {
    const queryParams = event.queryStringParameters || {};
    const advocateId = queryParams.advocateId;
    const repId = queryParams.repId;
    const status = queryParams.status;

    if (advocateId) {
        const params = {
            TableName: TABLES.leads,
            IndexName: 'advocate-index',
            KeyConditionExpression: 'advocateId = :advocateId',
            ExpressionAttributeValues: { ':advocateId': advocateId }
        };
        const result = await ddb.send(new QueryCommand(params));
        return { leads: result.Items || [] };
    } else if (repId) {
        const params = {
            TableName: TABLES.leads,
            IndexName: 'rep-index',
            KeyConditionExpression: 'repId = :repId',
            ExpressionAttributeValues: { ':repId': repId }
        };
        const result = await ddb.send(new QueryCommand(params));
        return { leads: result.Items || [] };
    } else if (status) {
        const params = {
            TableName: TABLES.leads,
            IndexName: 'status-index',
            KeyConditionExpression: '#status = :status',
            ExpressionAttributeNames: { '#status': 'status' },
            ExpressionAttributeValues: { ':status': status }
        };
        const result = await ddb.send(new QueryCommand(params));
        return { leads: result.Items || [] };
    } else {
        const result = await ddb.send(new ScanCommand({ TableName: TABLES.leads }));
        return { leads: result.Items || [] };
    }
}

async function getPayouts(event) {
    const queryParams = event.queryStringParameters || {};
    const advocateId = queryParams.advocateId;
    const status = queryParams.status;

    if (advocateId) {
        const params = {
            TableName: TABLES.payouts,
            IndexName: 'advocate-index',
            KeyConditionExpression: 'advocateId = :advocateId',
            ExpressionAttributeValues: { ':advocateId': advocateId }
        };
        const result = await ddb.send(new QueryCommand(params));
        return { payouts: result.Items || [] };
    } else if (status) {
        const params = {
            TableName: TABLES.payouts,
            IndexName: 'status-index',
            KeyConditionExpression: '#status = :status',
            ExpressionAttributeNames: { '#status': 'status' },
            ExpressionAttributeValues: { ':status': status }
        };
        const result = await ddb.send(new QueryCommand(params));
        return { payouts: result.Items || [] };
    } else {
        const result = await ddb.send(new ScanCommand({ TableName: TABLES.payouts }));
        return { payouts: result.Items || [] };
    }
}

async function getSalesReps(event) {
    const result = await ddb.send(new ScanCommand({ TableName: TABLES.salesReps }));
    return { salesReps: result.Items || [] };
}

async function getStats(event) {
    const [advocates, leads, payouts] = await Promise.all([
        ddb.send(new ScanCommand({ TableName: TABLES.advocates })),
        ddb.send(new ScanCommand({ TableName: TABLES.leads })),
        ddb.send(new ScanCommand({ TableName: TABLES.payouts }))
    ]);

    const stats = {
        totalAdvocates: (advocates.Items || []).length,
        activeAdvocates: (advocates.Items || []).filter(a => a.active).length,
        totalLeads: (leads.Items || []).length,
        leadsByStatus: {},
        totalPayouts: (payouts.Items || []).reduce((sum, p) => sum + (p.amount || 0), 0),
        pendingPayouts: (payouts.Items || []).filter(p => p.status === 'pending').reduce((sum, p) => sum + (p.amount || 0), 0),
        paidPayouts: (payouts.Items || []).filter(p => p.status === 'paid').reduce((sum, p) => sum + (p.amount || 0), 0)
    };

    (leads.Items || []).forEach(lead => {
        stats.leadsByStatus[lead.status] = (stats.leadsByStatus[lead.status] || 0) + 1;
    });

    return stats;
}

async function getDashboard(event) {
    const queryParams = event.queryStringParameters || {};
    const repId = queryParams.repId;

    let advocatesData, leadsData;

    if (repId) {
        const [advocates, leads] = await Promise.all([
            ddb.send(new QueryCommand({
                TableName: TABLES.advocates,
                IndexName: 'rep-index',
                KeyConditionExpression: 'repId = :repId',
                ExpressionAttributeValues: { ':repId': repId }
            })),
            ddb.send(new QueryCommand({
                TableName: TABLES.leads,
                IndexName: 'rep-index',
                KeyConditionExpression: 'repId = :repId',
                ExpressionAttributeValues: { ':repId': repId }
            }))
        ]);
        advocatesData = advocates.Items || [];
        leadsData = leads.Items || [];
    } else {
        const [advocates, leads] = await Promise.all([
            ddb.send(new ScanCommand({ TableName: TABLES.advocates })),
            ddb.send(new ScanCommand({ TableName: TABLES.leads }))
        ]);
        advocatesData = advocates.Items || [];
        leadsData = leads.Items || [];
    }

    const payouts = await ddb.send(new ScanCommand({ TableName: TABLES.payouts }));
    const payoutsData = payouts.Items || [];

    return {
        advocates: advocatesData,
        leads: leadsData,
        payouts: payoutsData,
        stats: {
            totalAdvocates: advocatesData.length,
            totalLeads: leadsData.length,
            totalEarnings: advocatesData.reduce((sum, a) => sum + (a.totalEarnings || 0), 0),
            pendingPayouts: payoutsData.filter(p => p.status === 'pending').length,
            paidPayouts: payoutsData.filter(p => p.status === 'paid').length
        }
    };
}
