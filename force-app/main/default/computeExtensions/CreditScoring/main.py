"""
This module is the main entry point for the Credit Scoring application.

It initializes a main FastAPI application for public endpoints and mounts a
sub-application for all endpoints that require Salesforce context via
Heroku AppLink.
"""
import os

import heroku_applink as sdk
import numpy as np
import yaml
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sklearn.linear_model import LogisticRegression
from typing import Dict, Optional


# --- Credit Scoring Router ---

router = APIRouter(
    tags=["credit-scoring"],
)


class CreditScoringRequest(BaseModel):
    accountId: str = Field(
        json_schema_extra={"example": "001XX000003GYQXYA4"}
    )


class CreditScoringData(BaseModel):
    data: CreditScoringRequest


class CreditScoringResponse(BaseModel):
    accountId: str
    accountName: str
    score: float
    creditScoring: str
    riskCategory: str
    method: str


def compute_altman_z_score(
    working_capital: float,
    total_assets: float,
    retained_earnings: float,
    ebit: float,
    market_value_equity: float,
    total_liabilities: float,
    sales: float,
) -> float:
    """
    Compute the Altman Z-Score using the original Z-Score formula.

    Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5

    Where:
      X1 = Working Capital / Total Assets
      X2 = Retained Earnings / Total Assets
      X3 = EBIT / Total Assets
      X4 = Market Value of Equity / Total Liabilities
      X5 = Sales / Total Assets

    :param working_capital: Current Assets minus Current Liabilities.
    :param total_assets: Total assets of the company.
    :param retained_earnings: Retained earnings of the company.
    :param ebit: Earnings before interest and taxes.
    :param market_value_equity: Market value of equity.
    :param total_liabilities: Total liabilities of the company.
    :param sales: Net sales / revenue.
    :return: The computed Altman Z-Score.
    :rtype: float
    """
    if total_assets == 0 or total_liabilities == 0:
        raise ValueError("Total assets and total liabilities must be non-zero.")

    ratios = np.array([
        working_capital / total_assets,
        retained_earnings / total_assets,
        ebit / total_assets,
        market_value_equity / total_liabilities,
        sales / total_assets,
    ])

    coefficients = np.array([1.2, 1.4, 3.3, 0.6, 1.0])

    z_score = float(np.dot(coefficients, ratios))
    return round(z_score, 4)


def compute_credit_score_lr(
    working_capital: float,
    total_assets: float,
    retained_earnings: float,
    ebit: float,
    market_value_equity: float,
    total_liabilities: float,
    sales: float,
) -> float:
    """
    Compute a credit score using a scikit-learn LogisticRegression model.

    A pre-configured logistic regression model estimates the probability that
    the company is creditworthy based on the same five financial ratios used
    in the Altman Z-Score.  The probability is then scaled to a 1.0–4.0
    range so it can be mapped through the same rating table as the Z-Score.

    The coefficients approximate a trained credit-risk model.  In production
    you would load a model persisted with joblib or pickle.

    :param working_capital: Current Assets minus Current Liabilities.
    :param total_assets: Total assets of the company.
    :param retained_earnings: Retained earnings of the company.
    :param ebit: Earnings before interest and taxes.
    :param market_value_equity: Market value of equity.
    :param total_liabilities: Total liabilities of the company.
    :param sales: Net sales / revenue.
    :return: A score on a 1.0–4.0 scale comparable to the Altman Z-Score.
    :rtype: float
    """
    if total_assets == 0 or total_liabilities == 0:
        raise ValueError("Total assets and total liabilities must be non-zero.")

    ratios = np.array([[
        working_capital / total_assets,
        retained_earnings / total_assets,
        ebit / total_assets,
        market_value_equity / total_liabilities,
        sales / total_assets,
    ]])

    model = LogisticRegression()
    model.classes_ = np.array([0, 1])
    model.coef_ = np.array([[0.8, 0.9, 2.2, 0.4, 0.7]])
    model.intercept_ = np.array([-1.5])

    probability = float(model.predict_proba(ratios)[0][1])

    # Scale probability (0-1) to a 1.0–4.0 range for rating mapping
    score = round(1.0 + probability * 3.0, 4)
    return score


def map_z_score_to_rating(z_score: float) -> tuple:
    """
    Map an Altman Z-Score to a credit scoring and risk category.

    Z > 3.0   -> AAA  (Safe)
    2.7 - 3.0 -> AA   (Safe)
    2.4 - 2.7 -> A    (Safe)
    2.0 - 2.4 -> BBB  (Grey Zone)
    1.8 - 2.0 -> BB   (Grey Zone)
    1.5 - 1.8 -> B    (Distress)
    1.0 - 1.5 -> CCC  (Distress)
    Z < 1.0   -> D    (Distress)

    :param z_score: The Altman Z-Score.
    :return: A tuple of (credit_rating, risk_category).
    :rtype: tuple
    """
    if z_score > 3.0:
        return ("AAA", "Safe")
    elif z_score > 2.7:
        return ("AA", "Safe")
    elif z_score > 2.4:
        return ("A", "Safe")
    elif z_score > 2.0:
        return ("BBB", "Grey Zone")
    elif z_score > 1.8:
        return ("BB", "Grey Zone")
    elif z_score > 1.5:
        return ("B", "Distress")
    elif z_score > 1.0:
        return ("CCC", "Distress")
    else:
        return ("D", "Distress")


@router.post("/", response_model=CreditScoringResponse, status_code=200)
async def generate_credit_rating(request: CreditScoringData) -> CreditScoringResponse:
    """
    Generate a credit scoring for a Salesforce Account.

    This endpoint queries the invoking Salesforce org for the Account's financial
    data, computes an Altman Z-Score using NumPy, maps it to a standard credit
    scoring, publishes a GenerateCreditScoring__e Platform Event, and returns the
    result.

    :param request: The request body containing the Account ID.
    :type request: CreditScoringData
    :raises HTTPException: If the Account is not found or financial data is missing.
    :return: The computed credit scoring for the Account.
    :rtype: CreditScoringResponse
    """
    context = sdk.get_client_context()
    org = context.org
    data_api = org.data_api
    logger = context.logger

    account_id = request.data.accountId
    logger.info(f"POST /credit-scoring for Account: {account_id}")

    # Query the Salesforce org for the Account's financial data
    try:
        query = (
            "SELECT Id, Name, "
            "WorkingCapital__c, TotalAssets__c, RetainedEarnings__c, "
            "EBIT__c, MarketValueEquity__c, TotalLiabilities__c, Sales__c "
            f"FROM Account WHERE Id = '{account_id}'"
        )
        result = await data_api.query(query)
    except Exception as e:
        error_message = f"Failed to query Account financial data: {e}"
        logger.error(error_message)
        raise HTTPException(status_code=500, detail=error_message) from e

    if not result.records:
        raise HTTPException(
            status_code=404,
            detail=f"Account with Id '{account_id}' not found.",
        )

    record = result.records[0]
    account_name = record.fields["Name"]

    # Extract financial fields, defaulting to 0 if not populated
    working_capital = float(record.fields.get("WorkingCapital__c") or 0)
    total_assets = float(record.fields.get("TotalAssets__c") or 0)
    retained_earnings = float(record.fields.get("RetainedEarnings__c") or 0)
    ebit = float(record.fields.get("EBIT__c") or 0)
    market_value_equity = float(record.fields.get("MarketValueEquity__c") or 0)
    total_liabilities = float(record.fields.get("TotalLiabilities__c") or 0)
    sales = float(record.fields.get("Sales__c") or 0)

    # Select scoring method from environment variable (default: altman_z_score)
    method = os.environ.get("SCORING_METHOD", "altman_z_score")
    financial_args = dict(
        working_capital=working_capital,
        total_assets=total_assets,
        retained_earnings=retained_earnings,
        ebit=ebit,
        market_value_equity=market_value_equity,
        total_liabilities=total_liabilities,
        sales=sales,
    )

    try:
        if method == "logistic_regression":
            score = compute_credit_score_lr(**financial_args)
        else:
            method = "altman_z_score"
            score = compute_altman_z_score(**financial_args)
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Cannot compute credit scoring: {e}",
        ) from e

    credit_rating, risk_category = map_z_score_to_rating(score)

    logger.info(
        f"Account '{account_name}' ({account_id}): "
        f"Method={method}, Score={score}, Rating={credit_rating}, Risk={risk_category}"
    )

    # Publish a GenerateCreditScoring__e Platform Event in the invoking org
    try:
        await data_api.create({
            "type": "GenerateCreditScoring__e",
            "fields": {
                "AccountId__c": account_id,
                "Rating__c": credit_rating,
                "Score__c": score,
                "RiskCategory__c": risk_category,
            },
        })
        logger.info("Published GenerateCreditScoring__e Platform Event.")
    except Exception as e:
        error_message = f"Failed to publish GenerateCreditScoring__e Platform Event: {e}"
        logger.error(error_message)
        raise HTTPException(status_code=500, detail=error_message) from e

    return CreditScoringResponse(
        accountId=account_id,
        accountName=account_name,
        score=score,
        creditScoring=credit_rating,
        riskCategory=risk_category,
        method=method,
    )


# --- Protected Salesforce App ---
# All routers and middleware that require Salesforce context are attached here.
sf_app = FastAPI()
sf_app.add_middleware(sdk.IntegrationAsgiMiddleware, config=sdk.Config())

sf_app.include_router(router, prefix="/credit-scoring")

# --- Main Public App ---
app = FastAPI(
    title="Credit Scoring API",
    description="A Heroku AppLink application that computes credit ratings for "
                "Salesforce Accounts using the Altman Z-Score model.",
    version="1.0.0",
)

# Mount the protected Salesforce app at the /api prefix
app.mount("/api", sf_app)

# Load the OpenAPI spec and attach it to the main app
with open("api-spec.yaml", "r") as f:
    openapi_schema = yaml.safe_load(f)
app.openapi_schema = openapi_schema


@app.get("/", summary="Welcome endpoint")
def read_root() -> Dict[str, str]:
    """
    A welcoming root endpoint that is publicly accessible.

    :return: A welcome message.
    :rtype: Dict[str, str]
    """
    return {
        "message": "Welcome to the Credit Scoring API!",
        "docs_url": "/docs",
        "salesforce_api_prefix": "/api",
    }


@app.get("/health", summary="Health check endpoint")
def get_health() -> Dict[str, str]:
    """
    A simple health check endpoint.

    :return: A dictionary with a status of "ok".
    :rtype: Dict[str, str]
    """
    return {"status": "ok"}
