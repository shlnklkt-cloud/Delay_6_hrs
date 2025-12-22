from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

class PolicyHolder(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str = "Jolene Chua"
    membership_type: str = "Premium Member"
    email: str = "jolene.chua@email.com"
    phone: str = "+65 9123 4567"

class FlightSegment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    flight_number: str
    airline: str
    departure_airport: str
    departure_code: str
    arrival_airport: str
    arrival_code: str
    scheduled_departure: str
    scheduled_arrival: str
    actual_departure: Optional[str] = None
    actual_arrival: Optional[str] = None
    status: str = "On Time"
    delay_hours: int = 0
    delay_reason: Optional[str] = None

class PolicyDetails(BaseModel):
    model_config = ConfigDict(extra="ignore")
    policy_number: str = "TRV-2026-0014879"
    policy_type: str = "Comprehensive Travel Insurance"
    coverage_start: str
    coverage_end: str
    flight_delay_coverage: str = "$100 per 6 hours"
    max_delay_coverage: str = "$500"
    trip_cancellation: str = "$5,000"
    medical_coverage: str = "$100,000"
    baggage_loss: str = "$2,500"
    status: str = "Active"

class ValidationStep(BaseModel):
    model_config = ConfigDict(extra="ignore")
    step_number: int
    name: str
    status: str = "pending"  # pending, in_progress, completed, failed
    details: Optional[str] = None
    api_called: Optional[str] = None
    timestamp: Optional[str] = None

class ClaimDetails(BaseModel):
    model_config = ConfigDict(extra="ignore")
    claim_id: str
    claim_type: str = "Flight Delay Claim Payment"
    delay_duration: int  # in hours
    compensation_amount: float
    filing_date: str
    status: str = "Processing"

class AgentLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    timestamp: str
    agent: str
    message: str
    log_type: str = "info"  # info, success, warning, error, api_call

class ClaimWorkflow(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    policy_holder: PolicyHolder
    policy_details: PolicyDetails
    flight_segments: List[FlightSegment]
    validation_steps: List[ValidationStep]
    claim_details: Optional[ClaimDetails] = None
    agent_logs: List[AgentLog] = []
    current_step: int = 0
    status: str = "initialized"  # initialized, processing, approved, paid, rejected
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ClaimWorkflowCreate(BaseModel):
    pass  # No input needed, we use predefined scenario

# ==================== HELPER FUNCTIONS ====================

def get_dynamic_journey_datetime():
    """Get journey date/time as current Singapore time + 6 hours"""
    from zoneinfo import ZoneInfo
    singapore_tz = ZoneInfo("Asia/Singapore")
    now = datetime.now(singapore_tz)
    journey_time = now + timedelta(hours=6)
    return journey_time

def create_scenario():
    """Create the predefined travel claim scenario"""
    journey_time = get_dynamic_journey_datetime()

    # Calculate flight times
    sin_hak_departure = journey_time
    sin_hak_arrival = sin_hak_departure + timedelta(hours=4, minutes=30)

    # Delayed by 6 hours
    sin_hak_actual_departure = sin_hak_departure + timedelta(hours=6)
    sin_hak_actual_arrival = sin_hak_arrival + timedelta(hours=6)

    # Connecting flight
    hak_nrt_departure = sin_hak_arrival + timedelta(hours=2)  # 2 hour layover originally
    hak_nrt_arrival = hak_nrt_departure + timedelta(hours=4)

    # Due to delay, connecting flight also pushed
    hak_nrt_actual_departure = hak_nrt_departure + timedelta(hours=6)
    hak_nrt_actual_arrival = hak_nrt_arrival + timedelta(hours=6)

    coverage_start = (journey_time - timedelta(days=1)).strftime("%d %B %Y")
    coverage_end = (journey_time + timedelta(days=14)).strftime("%d %B %Y")

    flight_segments = [
        FlightSegment(
            flight_number="SQ656",
            airline="Singapore Airlines",
            departure_airport="Singapore Changi Airport",
            departure_code="SIN",
            arrival_airport="Haikou Meilan International Airport",
            arrival_code="HAK",
            scheduled_departure=sin_hak_departure.strftime("%d %b %Y, %H:%M"),
            scheduled_arrival=sin_hak_arrival.strftime("%d %b %Y, %H:%M"),
            actual_departure=sin_hak_actual_departure.strftime("%d %b %Y, %H:%M"),
            actual_arrival=sin_hak_actual_arrival.strftime("%d %b %Y, %H:%M"),
            status="Delayed",
            delay_hours=6,
            delay_reason="Adverse Weather Conditions - Tropical Storm"
        ),
        FlightSegment(
            flight_number="CA168",
            airline="Air China",
            departure_airport="Haikou Meilan International Airport",
            departure_code="HAK",
            arrival_airport="Narita International Airport",
            arrival_code="NRT",
            scheduled_departure=hak_nrt_departure.strftime("%d %b %Y, %H:%M"),
            scheduled_arrival=hak_nrt_arrival.strftime("%d %b %Y, %H:%M"),
            actual_departure=hak_nrt_actual_departure.strftime("%d %b %Y, %H:%M"),
            actual_arrival=hak_nrt_actual_arrival.strftime("%d %b %Y, %H:%M"),
            status="Rescheduled",
            delay_hours=0,
            delay_reason=None
        )
    ]

    validation_steps = [
        ValidationStep(step_number=1, name="Policy Verification", status="pending"),
        ValidationStep(step_number=2, name="Flight Delay Confirmation", status="pending"),
        ValidationStep(step_number=3, name="Delay Duration Validation", status="pending"),
        ValidationStep(step_number=4, name="Eligibility Assessment", status="pending"),
        ValidationStep(step_number=5, name="Claim Payment Calculation", status="pending"),
        ValidationStep(step_number=6, name="Security Screening", status="pending"),
    ]

    policy_holder = PolicyHolder()
    policy_details = PolicyDetails(
        coverage_start=coverage_start,
        coverage_end=coverage_end
    )

    return ClaimWorkflow(
        policy_holder=policy_holder,
        policy_details=policy_details,
        flight_segments=flight_segments,
        validation_steps=validation_steps
    )

# ==================== MOCK EXTERNAL API ENDPOINTS ====================

@api_router.get("/external/flight-status/{flight_number}")
async def get_flight_status(flight_number: str):
    """Mock FlightAware API - Simulates real flight status check"""
    await simulate_api_delay()

    if flight_number == "SQ656":
        return {
            "api": "FlightAware Real-Time API",
            "request_id": f"FA-{uuid.uuid4().hex[:8].upper()}",
            "flight": {
                "ident": "SQ656",
                "airline": "Singapore Airlines",
                "status": "Delayed",
                "delay_minutes": 360,
                "delay_reason": "Weather - Tropical Storm Warning",
                "origin": {"code": "SIN", "name": "Singapore Changi Airport"},
                "destination": {"code": "HAK", "name": "Haikou Meilan Intl"},
                "gate_origin": "C24",
                "gate_destination": "A12"
            }
        }
    elif flight_number == "CA168":
        return {
            "api": "FlightAware Real-Time API",
            "request_id": f"FA-{uuid.uuid4().hex[:8].upper()}",
            "flight": {
                "ident": "CA168",
                "airline": "Air China",
                "status": "Scheduled",
                "delay_minutes": 0,
                "origin": {"code": "HAK", "name": "Haikou Meilan Intl"},
                "destination": {"code": "NRT", "name": "Narita International"}
            }
        }
    return {"error": "Flight not found"}

@api_router.get("/external/weather/{location_code}")
async def get_weather(location_code: str):
    """Mock WeatherAPI - Simulates weather verification"""
    await simulate_api_delay()

    weather_data = {
        "SIN": {
            "api": "OpenWeatherMap Pro API",
            "request_id": f"OWM-{uuid.uuid4().hex[:8].upper()}",
            "location": "Singapore",
            "condition": "Partly Cloudy",
            "temperature": "31°C",
            "wind_speed": "12 km/h",
            "visibility": "Good",
            "alerts": []
        },
        "HAK": {
            "api": "OpenWeatherMap Pro API",
            "request_id": f"OWM-{uuid.uuid4().hex[:8].upper()}",
            "location": "Haikou, China",
            "condition": "Tropical Storm",
            "temperature": "26°C",
            "wind_speed": "85 km/h",
            "visibility": "Poor",
            "alerts": ["Tropical Storm Warning", "Flight Operations Suspended"]
        }
    }
    return weather_data.get(location_code, {"error": "Location not found"})

@api_router.get("/external/policy-verify/{policy_number}")
async def verify_policy(policy_number: str):
    """Mock Policy Verification API"""
    await simulate_api_delay()

    if policy_number == "TRV-2026-0014879":
        return {
            "api": "Income Insurance Policy API",
            "request_id": f"INC-{uuid.uuid4().hex[:8].upper()}",
            "policy": {
                "number": policy_number,
                "holder": "Jolene Chua",
                "type": "Comprehensive Travel Insurance",
                "status": "Active",
                "premium_status": "Paid",
                "coverage": {
                    "flight_delay": "$100 per 6 hours (max $500)",
                    "trip_cancellation": "$5,000",
                    "medical": "$100,000",
                    "baggage": "$2,500"
                },
                "verification": "PASSED"
            }
        }
    return {"error": "Policy not found", "verification": "FAILED"}

@api_router.get("/external/eligibility-check")
async def check_eligibility(policy_number: str, claim_type: str, delay_hours: int):
    """Mock Eligibility Check API"""
    await simulate_api_delay()

    return {
        "api": "Income Claims Eligibility Engine",
        "request_id": f"ELG-{uuid.uuid4().hex[:8].upper()}",
        "eligibility": {
            "policy_number": policy_number,
            "claim_type": claim_type,
            "delay_hours": delay_hours,
            "minimum_delay_required": 6,
            "meets_criteria": delay_hours >= 6,
            "eligible": True,
            "reason": "Delay duration meets minimum threshold of 6 hours"
        }
    }

@api_router.get("/external/security-screening")
async def security_screening(policy_number: str, claim_amount: float):
    """Mock Fraud Detection API"""
    await simulate_api_delay()

    return {
        "api": "Income Fraud Detection System",
        "request_id": f"FDS-{uuid.uuid4().hex[:8].upper()}",
        "screening": {
            "policy_number": policy_number,
            "claim_amount": claim_amount,
            "risk_score": 12,
            "risk_level": "Low",
            "flags": [],
            "recommendation": "APPROVE",
            "auto_approval": True
        }
    }

@api_router.post("/external/payment-process")
async def process_payment(policy_number: str, amount: float, holder_name: str):
    """Mock Payment Processing API"""
    await simulate_api_delay()

    return {
        "api": "Income Payment Gateway",
        "request_id": f"PAY-{uuid.uuid4().hex[:8].upper()}",
        "payment": {
            "transaction_id": f"TXN-{uuid.uuid4().hex[:12].upper()}",
            "policy_number": policy_number,
            "beneficiary": holder_name,
            "amount": amount,
            "currency": "SGD",
            "method": "Bank Transfer",
            "bank": "DBS Bank",
            "account_ending": "****7890",
            "status": "COMPLETED",
            "estimated_arrival": "1-2 business days"
        }
    }

async def simulate_api_delay():
    """Simulate network latency for realistic API calls"""
    import asyncio
    await asyncio.sleep(random.uniform(0.3, 0.8))

# ==================== MAIN API ENDPOINTS ====================

@api_router.get("/")
async def root():
    return {"message": "Income Insurance - Smart Travel Claims API"}

@api_router.get("/scenario")
async def get_scenario():
    """Get the current claim scenario with dynamic date/time"""
    scenario = create_scenario()
    return scenario.model_dump()

@api_router.post("/claim/start", response_model=dict)
async def start_claim():
    """Start a new claim workflow"""
    workflow = create_scenario()
    workflow.status = "processing"

    # Store in MongoDB
    doc = workflow.model_dump()
    await db.claims.insert_one(doc)

    return {"id": workflow.id, "status": "started"}

@api_router.get("/claim/{claim_id}")
async def get_claim(claim_id: str):
    """Get claim workflow status"""
    claim = await db.claims.find_one({"id": claim_id}, {"_id": 0})
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim

@api_router.post("/claim/{claim_id}/process-step")
async def process_step(claim_id: str, step_number: int):
    """Process a specific validation step"""
    claim = await db.claims.find_one({"id": claim_id}, {"_id": 0})
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    logs = []
    step_result = None

    if step_number == 1:  # Policy Verification
        api_response = await verify_policy(claim["policy_details"]["policy_number"])
        step_result = {
            "status": "completed",
            "details": f"Policy {claim['policy_details']['policy_number']} verified - Status: Active",
            "api_called": "/api/external/policy-verify",
            "api_response": api_response,
            "timestamp": timestamp
        }
        logs = [
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message="Policy Verification - Processing...", log_type="info"),
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message=f"Calling external API: /api/policy-verify/{claim['policy_details']['policy_number']}", log_type="api_call"),
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message="Policy Verification Complete: Validated successfully", log_type="success"),
        ]

    elif step_number == 2:  # Flight Delay Confirmation
        flight = claim["flight_segments"][0]
        api_response = await get_flight_status(flight["flight_number"])
        step_result = {
            "status": "completed",
            "details": f"Flight {flight['flight_number']} confirmed delayed by {flight['delay_hours']} hours",
            "api_called": "/api/external/flight-status",
            "api_response": api_response,
            "timestamp": timestamp
        }
        logs = [
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message="Flight Delay Confirmation - Processing...", log_type="info"),
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message=f"Calling FlightAware API: /api/external/flight-status/{flight['flight_number']}", log_type="api_call"),
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message=f"Flight Status Retrieved: {flight['status']} - {flight['delay_hours']}h delay confirmed", log_type="success"),
        ]

    elif step_number == 3:  # Delay Duration Validation
        flight = claim["flight_segments"][0]
        weather_response = await get_weather(flight["departure_code"])
        step_result = {
            "status": "completed",
            "details": f"Delay of {flight['delay_hours']} hours validated - Reason: {flight['delay_reason']}",
            "api_called": "/api/external/weather",
            "api_response": weather_response,
            "timestamp": timestamp
        }
        logs = [
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message="Delay Duration Validation - Processing...", log_type="info"),
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message=f"Calling Weather API: /api/external/weather/{flight['departure_code']}", log_type="api_call"),
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message=f"Weather Verification: {flight['delay_reason']} confirmed", log_type="success"),
        ]

    elif step_number == 4:  # Eligibility Assessment
        flight = claim["flight_segments"][0]
        eligibility = await check_eligibility(
            claim["policy_details"]["policy_number"],
            "Flight Delay",
            flight["delay_hours"]
        )
        step_result = {
            "status": "completed",
            "details": f"Claim eligible - Delay of {flight['delay_hours']}h meets 6h minimum requirement",
            "api_called": "/api/external/eligibility-check",
            "api_response": eligibility,
            "timestamp": timestamp
        }
        logs = [
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message="Eligibility Assessment - Processing...", log_type="info"),
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message="Calling Eligibility Engine: /api/external/eligibility-check", log_type="api_call"),
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message="Eligibility Confirmed: Meets all policy criteria", log_type="success"),
        ]

    elif step_number == 5:  # Claim Payment Calculation
        flight = claim["flight_segments"][0]
        # $100 per 6 hours
        compensation = (flight["delay_hours"] // 6) * 100
        step_result = {
            "status": "completed",
            "details": f"Claim Payment calculated: ${compensation} ({flight['delay_hours']}h ÷ 6h × $100)",
            "api_called": None,
            "compensation": compensation,
            "timestamp": timestamp
        }
        logs = [
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message="Claim Payment Calculation - Processing...", log_type="info"),
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message=f"Calculating: {flight['delay_hours']} hours delay", log_type="info"),
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message=f"Formula: ({flight['delay_hours']}h ÷ 6h) × $100 = ${compensation}", log_type="info"),
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message=f"Claim Payment Amount: ${compensation}", log_type="success"),
        ]

        # Update claim with claim payment details
        await db.claims.update_one(
            {"id": claim_id},
            {"$set": {
                "claim_details": {
                    "claim_id": f"CLM-TRV-2026-008431",
                    "claim_type": "Flight Delay Claim Payment",
                    "delay_duration": flight["delay_hours"],
                    "compensation_amount": compensation,
                    "filing_date": datetime.now(timezone.utc).strftime("%d %B %Y"),
                    "status": "Processing"
                }
            }}
        )

    elif step_number == 6:  # Security Screening
        flight = claim["flight_segments"][0]
        compensation = (flight["delay_hours"] // 6) * 100
        security = await security_screening(claim["policy_details"]["policy_number"], compensation)
        step_result = {
            "status": "completed",
            "details": "Security screening passed - Low risk, auto-approval recommended",
            "api_called": "/api/external/security-screening",
            "api_response": security,
            "timestamp": timestamp
        }
        logs = [
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message="Security Screening - Processing...", log_type="info"),
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message="Calling Fraud Detection: /api/external/security-screening", log_type="api_call"),
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message="Security Check: PASSED - Risk Score: 12 (Low)", log_type="success"),
            AgentLog(timestamp=timestamp, agent="Claim Processing Agent", message="All 6 validations completed successfully!", log_type="success"),
        ]

    # Update the step in database
    if step_result:
        await db.claims.update_one(
            {"id": claim_id, "validation_steps.step_number": step_number},
            {"$set": {
                f"validation_steps.$.status": step_result["status"],
                f"validation_steps.$.details": step_result["details"],
                f"validation_steps.$.api_called": step_result.get("api_called"),
                f"validation_steps.$.timestamp": step_result["timestamp"]
            }}
        )

        # Add logs
        log_dicts = [log.model_dump() for log in logs]
        await db.claims.update_one(
            {"id": claim_id},
            {"$push": {"agent_logs": {"$each": log_dicts}}}
        )

    return {"step": step_number, "result": step_result, "logs": [log.model_dump() for log in logs]}

@api_router.post("/claim/{claim_id}/approve")
async def approve_claim(claim_id: str):
    """Approve the claim after all validations"""
    claim = await db.claims.find_one({"id": claim_id}, {"_id": 0})
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")

    await db.claims.update_one(
        {"id": claim_id},
        {
            "$set": {"status": "approved", "claim_details.status": "Approved"},
            "$push": {"agent_logs": {
                "timestamp": timestamp,
                "agent": "Orchestrator Agent",
                "message": "Claim APPROVED - Transferring to Payment Agent",
                "log_type": "success"
            }}
        }
    )

    return {"status": "approved", "timestamp": timestamp}

@api_router.post("/claim/{claim_id}/pay")
async def pay_claim(claim_id: str):
    """Process payment for the approved claim"""
    claim = await db.claims.find_one({"id": claim_id}, {"_id": 0})
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    if claim.get("status") != "approved":
        raise HTTPException(status_code=400, detail="Claim must be approved before payment")

    timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")

    # Get compensation amount
    compensation = claim.get("claim_details", {}).get("compensation_amount", 100)

    # Process payment
    payment_response = await process_payment(
        claim["policy_details"]["policy_number"],
        compensation,
        claim["policy_holder"]["name"]
    )

    logs = [
        {"timestamp": timestamp, "agent": "Payment Agent", "message": "Initiating claim payment transfer...", "log_type": "info"},
        {"timestamp": timestamp, "agent": "Payment Agent", "message": "Calling Payment Gateway: /api/external/payment-process", "log_type": "api_call"},
        {"timestamp": timestamp, "agent": "Payment Agent", "message": f"Payment Processed: ${compensation}", "log_type": "success"},
        {"timestamp": timestamp, "agent": "Payment Agent", "message": f"Transaction ID: {payment_response['payment']['transaction_id']}", "log_type": "success"},
        {"timestamp": timestamp, "agent": "Payment Agent", "message": f"Funds transferred to {claim['policy_holder']['name']}", "log_type": "success"},
    ]

    await db.claims.update_one(
        {"id": claim_id},
        {
            "$set": {"status": "paid", "claim_details.status": "Paid", "payment_response": payment_response},
            "$push": {"agent_logs": {"$each": logs}}
        }
    )

    return {"status": "paid", "payment": payment_response, "logs": logs}

@api_router.delete("/claims")
async def clear_claims():
    """Clear all claims (for testing)"""
    await db.claims.delete_many({})
    return {"message": "All claims cleared"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
