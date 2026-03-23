// Insert 5 Account records with credit scoring financial fields.
// Execute via: SFDX: Execute Anonymous Apex with Editor Contents

List<Account> accounts = new List<Account>();

// 1. Acme Corporation — Strong financials (expect AAA, Safe)
accounts.add(new Account(
    Name = 'Acme Corporation',
    WorkingCapital__c = 750000,
    TotalAssets__c = 1500000,
    RetainedEarnings__c = 400000,
    EBIT__c = 300000,
    MarketValueEquity__c = 2000000,
    TotalLiabilities__c = 500000,
    Sales__c = 1800000
));

// 2. Globex Industries — Solid financials (expect A, Safe)
accounts.add(new Account(
    Name = 'Globex Industries',
    WorkingCapital__c = 350000,
    TotalAssets__c = 1000000,
    RetainedEarnings__c = 180000,
    EBIT__c = 120000,
    MarketValueEquity__c = 600000,
    TotalLiabilities__c = 400000,
    Sales__c = 850000
));

// 3. Initech Partners — Moderate financials (expect BBB, Grey Zone)
accounts.add(new Account(
    Name = 'Initech Partners',
    WorkingCapital__c = 150000,
    TotalAssets__c = 1000000,
    RetainedEarnings__c = 100000,
    EBIT__c = 80000,
    MarketValueEquity__c = 350000,
    TotalLiabilities__c = 500000,
    Sales__c = 600000
));

// 4. Umbrella Ltd — Weak financials (expect B, Distress)
accounts.add(new Account(
    Name = 'Umbrella Ltd',
    WorkingCapital__c = 20000,
    TotalAssets__c = 800000,
    RetainedEarnings__c = 30000,
    EBIT__c = 25000,
    MarketValueEquity__c = 150000,
    TotalLiabilities__c = 700000,
    Sales__c = 350000
));

// 5. Stark Ventures — Distressed financials (expect D, Distress)
accounts.add(new Account(
    Name = 'Stark Ventures',
    WorkingCapital__c = -100000,
    TotalAssets__c = 900000,
    RetainedEarnings__c = -150000,
    EBIT__c = -50000,
    MarketValueEquity__c = 80000,
    TotalLiabilities__c = 850000,
    Sales__c = 200000
));

insert accounts;

for (Account a : accounts) {
    System.debug('Inserted Account: ' + a.Name + ' (Id: ' + a.Id + ')');
}
System.debug('Successfully inserted ' + accounts.size() + ' credit rating test Accounts.');
