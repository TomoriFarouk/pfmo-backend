"""
AI Insights API endpoints
Provides AI-powered analysis and recommendations
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from app.database import get_db
from app.models.submission import FormSubmission
from app.routers.auth import get_current_active_admin, get_current_user
from app.services.ai_service import ai_service

router = APIRouter()


class TextAnalysisRequest(BaseModel):
    text: str


@router.get("/submission/{submission_id}/insights")
def get_submission_insights(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get AI-powered insights for a specific submission"""
    submission = db.query(FormSubmission).filter(
        FormSubmission.id == submission_id).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Convert submission to dict
    submission_dict = submission.to_dict()

    # Get AI insights
    insights = {
        "submission_id": submission_id,
        "facility_name": submission.facility_name,
        "ai_analysis": {
            "issues_analysis": ai_service.analyze_issues_and_comments(
                submission.issues or "",
                submission.comments or ""
            ),
            "satisfaction_analysis": ai_service.analyze_patient_satisfaction(
                submission.satisfaction_survey_data or {}
            ),
            "predictions": ai_service.predict_facility_needs(submission_dict),
            "anomalies": ai_service.detect_data_anomalies(submission_dict),
            "summary": ai_service.generate_insights_summary(submission_dict)
        }
    }

    return insights


@router.get("/facilities/at-risk")
def get_at_risk_facilities(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_admin)
):
    """Identify facilities at risk based on AI analysis"""
    submissions = db.query(FormSubmission).all()

    at_risk_facilities = []

    for submission in submissions:
        submission_dict = submission.to_dict()
        predictions = ai_service.predict_facility_needs(submission_dict)
        anomalies = ai_service.detect_data_anomalies(submission_dict)

        if predictions["priority_level"] == "high" or len(anomalies) > 0:
            at_risk_facilities.append({
                "id": submission.id,
                "facility_name": submission.facility_name,
                "state": submission.state,
                "lga": submission.lga,
                "condition": submission.facility_condition,
                "priority": predictions["priority_level"],
                "risk_factors": predictions["risk_factors"],
                "predicted_needs": predictions["predicted_needs"],
                "anomalies_count": len(anomalies)
            })

    # Sort by priority
    at_risk_facilities.sort(key=lambda x: 0 if x["priority"] == "high" else 1)

    return {
        "total_at_risk": len(at_risk_facilities),
        "facilities": at_risk_facilities
    }


@router.get("/recommendations")
def get_ai_recommendations(
    state: str = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_admin)
):
    """Get AI-generated recommendations based on all submissions"""
    query = db.query(FormSubmission)
    if state:
        query = query.filter(FormSubmission.state == state)

    submissions = query.all()

    recommendations = {
        "infrastructure": [],
        "staffing": [],
        "funding": [],
        "general": []
    }

    for submission in submissions:
        submission_dict = submission.to_dict()
        predictions = ai_service.predict_facility_needs(submission_dict)

        for rec in predictions.get("recommendations", []):
            if "infrastructure" in rec.lower() or "power" in rec.lower() or "water" in rec.lower():
                recommendations["infrastructure"].append({
                    "facility": submission.facility_name,
                    "state": submission.state,
                    "recommendation": rec
                })
            elif "staff" in rec.lower() or "worker" in rec.lower():
                recommendations["staffing"].append({
                    "facility": submission.facility_name,
                    "state": submission.state,
                    "recommendation": rec
                })
            elif "funding" in rec.lower() or "financial" in rec.lower():
                recommendations["funding"].append({
                    "facility": submission.facility_name,
                    "state": submission.state,
                    "recommendation": rec
                })
            else:
                recommendations["general"].append({
                    "facility": submission.facility_name,
                    "state": submission.state,
                    "recommendation": rec
                })

    return recommendations


@router.post("/analyze-text")
def analyze_text(
    request: TextAnalysisRequest,
    current_user=Depends(get_current_user)
):
    """Analyze any text for sentiment, topics, and insights"""
    analysis = ai_service.analyze_issues_and_comments(request.text, "")
    return analysis
