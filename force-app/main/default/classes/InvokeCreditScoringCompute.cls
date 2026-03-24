public class InvokeCreditScoringCompute {
	public static void invoke() {
        List<Account> accounts = [
            SELECT Id FROM Account
            WHERE WorkingCapital__c != null
              AND TotalAssets__c != null
              AND RetainedEarnings__c != null
              AND EBIT__c != null
              AND MarketValueEquity__c != null
              AND TotalLiabilities__c != null
              AND Sales__c != null
        ];
        Integer idx = (Integer) Math.floor(Math.random() * accounts.size());
        Account acct = accounts[idx];

        herokuapplink.CreditScoringCompute creditScoringCompute = new herokuapplink.CreditScoringCompute();
        herokuapplink.CreditScoringCompute.GenerateCreditScoring_Request request = new herokuapplink.CreditScoringCompute.GenerateCreditScoring_Request();
        request.body = new herokuapplink.CreditScoringCompute_CreditScoringData();
        request.body.data = new herokuapplink.CreditScoringCompute_CreditScoringRequest();
        request.body.data.accountId = acct.Id;
        System.debug('Invoking credit scoring for Account: ' + acct.Id);
        try {
            System.debug(JSON.serialize(creditScoringCompute.GenerateCreditScoring(request)));
        } catch (herokuapplink.CreditScoringCompute.GenerateCreditScoring_ResponseException e) {
            System.debug('GenerateCreditScoring failed with response code: ' + e.responseCode);
            if (e.responseCode == 404 && e.Code404 != null) {
                System.debug('404 - Account not found: ' + e.Code404.detail);
            } else if (e.responseCode == 422 && e.Code422 != null) {
                System.debug('422 - Insufficient financial data: ' + e.Code422.detail);
            } else if (e.responseCode == 500 && e.Code500 != null) {
                System.debug('500 - Internal server error: ' + e.Code500.detail);
            } else {
                System.debug('Default response: ' + e.defaultResponse);
            }
        }
    }
}