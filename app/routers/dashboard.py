from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.database import get_db
from app.models.submission import FormSubmission
from app.models.user import User
from app.routers.auth import get_current_active_admin

router = APIRouter()


@router.get("/overview")
def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_admin)
):
    """Get dashboard overview statistics"""

    # Total submissions
    total_submissions = db.query(func.count(FormSubmission.id)).scalar() or 0

    # Synced vs pending
    synced = db.query(func.count(FormSubmission.id)).filter(
        FormSubmission.is_synced == True
    ).scalar() or 0
    pending = db.query(func.count(FormSubmission.id)).filter(
        FormSubmission.sync_status == "pending"
    ).scalar() or 0

    # Submissions by state
    submissions_by_state = db.query(
        FormSubmission.state,
        func.count(FormSubmission.id).label('count')
    ).group_by(FormSubmission.state).all()

    # Submissions by LGA
    submissions_by_lga = db.query(
        FormSubmission.lga,
        func.count(FormSubmission.id).label('count')
    ).group_by(FormSubmission.lga).order_by(desc('count')).limit(10).all()

    # Recent activity
    recent_submissions = db.query(FormSubmission).order_by(
        desc(FormSubmission.created_at)
    ).limit(10).all()

    # Submissions over time (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    submissions_over_time = db.query(
        func.date(FormSubmission.created_at).label('date'),
        func.count(FormSubmission.id).label('count')
    ).filter(
        FormSubmission.created_at >= thirty_days_ago
    ).group_by(func.date(FormSubmission.created_at)).all()

    return {
        "total_submissions": total_submissions,
        "synced_submissions": synced,
        "pending_submissions": pending,
        "synced_percentage": round((synced / total_submissions * 100) if total_submissions > 0 else 0, 2),
        "submissions_by_state": [
            {"state": state, "count": count}
            for state, count in submissions_by_state
        ],
        "top_lgas": [
            {"lga": lga, "count": count}
            for lga, count in submissions_by_lga
        ],
        "recent_submissions": [
            {
                "id": s.id,
                "facility_name": s.facility_name,
                "state": s.state,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "sync_status": s.sync_status
            }
            for s in recent_submissions
        ],
        "submissions_over_time": [
            {"date": str(date), "count": count}
            for date, count in submissions_over_time
        ]
    }


@router.get("/geographic-data")
def get_geographic_data(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_admin)
):
    """Get geographic distribution data for mapping"""

    submissions = db.query(
        FormSubmission.latitude,
        FormSubmission.longitude,
        FormSubmission.facility_name,
        FormSubmission.state,
        FormSubmission.lga,
        FormSubmission.facility_condition
    ).filter(
        FormSubmission.latitude.isnot(None),
        FormSubmission.longitude.isnot(None)
    ).all()

    return {
        "facilities": [
            {
                "latitude": lat,
                "longitude": lng,
                "name": facility_name,
                "state": state,
                "lga": lga,
                "condition": condition
            }
            for lat, lng, facility_name, state, lga, condition in submissions
        ]
    }


@router.get("/collectors")
def get_collectors_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_admin)
):
    """Get data collector statistics"""

    collectors = db.query(
        User.id,
        User.username,
        User.full_name,
        func.count(FormSubmission.id).label('submission_count')
    ).join(
        FormSubmission, User.id == FormSubmission.collector_id
    ).group_by(User.id).all()

    return [
        {
            "id": collector_id,
            "username": username,
            "full_name": full_name,
            "submission_count": count
        }
        for collector_id, username, full_name, count in collectors
    ]


@router.get("/detailed-analytics")
def get_detailed_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_admin)
):
    """Get detailed analytics of form submission content"""

    submissions = db.query(FormSubmission).all()

    # Facility Condition Analysis
    condition_counts = {}
    ownership_counts = {}
    assessment_type_counts = {}
    has_health_workers_counts = {}

    # Funding Analysis
    bhcpf_facilities = 0
    impact_facilities = 0
    total_funding_amount = 0
    funding_by_state = {}

    # Infrastructure Analysis
    infrastructure_stats = {
        "has_power": 0,
        "has_water": 0,
        "has_internet": 0,
        "has_pharmacy": 0,
        "revitalization_count": 0
    }

    # Human Resources Analysis
    total_staff = 0
    staff_by_type = {}
    facilities_with_staff = 0

    # Services Utilization
    total_patients = 0
    services_offered = {}
    avg_patients_per_facility = 0

    # Patient Satisfaction
    satisfaction_scores = []
    satisfaction_by_category = {}

    # Geographic Zone Analysis
    zone_counts = {}

    for sub in submissions:
        # Facility Condition
        if sub.facility_condition:
            condition_counts[sub.facility_condition] = condition_counts.get(
                sub.facility_condition, 0) + 1

        # Ownership Type
        if sub.ownership_type:
            ownership_counts[sub.ownership_type] = ownership_counts.get(
                sub.ownership_type, 0) + 1

        # Assessment Type
        if sub.assessment_type:
            assessment_type_counts[sub.assessment_type] = assessment_type_counts.get(
                sub.assessment_type, 0) + 1

        # Health Workers
        if sub.has_health_workers:
            has_health_workers_counts[sub.has_health_workers] = has_health_workers_counts.get(
                sub.has_health_workers, 0) + 1

        # Geopolitical Zone
        if sub.geopolitical_zone:
            zone_counts[sub.geopolitical_zone] = zone_counts.get(
                sub.geopolitical_zone, 0) + 1

        # Funding Data Analysis
        if sub.funding_data and isinstance(sub.funding_data, dict):
            if sub.funding_data.get('bhcpf_received') == 'Yes' or sub.funding_data.get('has_bhcpf'):
                bhcpf_facilities += 1
            if sub.funding_data.get('amount'):
                try:
                    amount = float(
                        str(sub.funding_data.get('amount', 0)).replace(',', ''))
                    total_funding_amount += amount
                    if sub.state:
                        funding_by_state[sub.state] = funding_by_state.get(
                            sub.state, 0) + amount
                except:
                    pass

        if sub.impact_funding_data and isinstance(sub.impact_funding_data, dict):
            if sub.impact_funding_data.get('received') == 'Yes' or sub.impact_funding_data.get('has_impact_funding'):
                impact_facilities += 1

        # Infrastructure Data Analysis
        if sub.infrastructure_data and isinstance(sub.infrastructure_data, dict):
            if sub.infrastructure_data.get('has_power') == 'Yes' or sub.infrastructure_data.get('power_available'):
                infrastructure_stats["has_power"] += 1
            if sub.infrastructure_data.get('has_water') == 'Yes' or sub.infrastructure_data.get('water_available'):
                infrastructure_stats["has_water"] += 1
            if sub.infrastructure_data.get('has_internet') == 'Yes' or sub.infrastructure_data.get('internet_available'):
                infrastructure_stats["has_internet"] += 1
            if sub.infrastructure_data.get('has_pharmacy') == 'Yes' or sub.infrastructure_data.get('pharmacy_available'):
                infrastructure_stats["has_pharmacy"] += 1
            if sub.infrastructure_data.get('revitalization') == 'Yes' or sub.infrastructure_data.get('revitalized'):
                infrastructure_stats["revitalization_count"] += 1

        # Human Resources Analysis
        if sub.human_resources_data and isinstance(sub.human_resources_data, dict):
            facility_staff_count = 0
            for key, value in sub.human_resources_data.items():
                if 'staff' in key.lower() or 'personnel' in key.lower() or 'worker' in key.lower():
                    try:
                        count = int(str(value).split()[0]) if isinstance(
                            value, str) else int(value)
                        facility_staff_count += count
                        staff_type = key.replace('_', ' ').title()
                        staff_by_type[staff_type] = staff_by_type.get(
                            staff_type, 0) + count
                    except:
                        pass
            if facility_staff_count > 0:
                total_staff += facility_staff_count
                facilities_with_staff += 1

        # Services Utilization Analysis
        if sub.services_data and isinstance(sub.services_data, dict):
            # Count patients
            for key, value in sub.services_data.items():
                if 'patient' in key.lower() or 'attendance' in key.lower() or 'utilization' in key.lower():
                    try:
                        count = int(str(value).split()[0]) if isinstance(
                            value, str) else int(value)
                        total_patients += count
                    except:
                        pass

            # Count services offered
            for key, value in sub.services_data.items():
                if isinstance(value, str) and value.lower() in ['yes', 'true', 'available']:
                    service_name = key.replace('_', ' ').title()
                    services_offered[service_name] = services_offered.get(
                        service_name, 0) + 1

        # Patient Satisfaction Analysis
        if sub.satisfaction_survey_data and isinstance(sub.satisfaction_survey_data, dict):
            for key, value in sub.satisfaction_survey_data.items():
                if 'satisfaction' in key.lower() or 'rating' in key.lower() or 'score' in key.lower():
                    try:
                        score = float(value) if isinstance(
                            value, (int, float)) else float(str(value).split()[0])
                        satisfaction_scores.append(score)
                        category = key.replace('_', ' ').title()
                        if category not in satisfaction_by_category:
                            satisfaction_by_category[category] = []
                        satisfaction_by_category[category].append(score)
                    except:
                        pass

    total_submissions = len(submissions)

    return {
        "facility_analysis": {
            "condition_distribution": [
                {"condition": k, "count": v, "percentage": round(
                    (v / total_submissions * 100) if total_submissions > 0 else 0, 2)}
                for k, v in condition_counts.items()
            ],
            "ownership_distribution": [
                {"type": k, "count": v, "percentage": round(
                    (v / total_submissions * 100) if total_submissions > 0 else 0, 2)}
                for k, v in ownership_counts.items()
            ],
            "assessment_type_distribution": [
                {"type": k, "count": v}
                for k, v in assessment_type_counts.items()
            ],
            "health_workers_distribution": [
                {"status": k, "count": v, "percentage": round(
                    (v / total_submissions * 100) if total_submissions > 0 else 0, 2)}
                for k, v in has_health_workers_counts.items()
            ],
            "geopolitical_zone_distribution": [
                {"zone": k, "count": v}
                for k, v in zone_counts.items()
            ]
        },
        "funding_analysis": {
            "bhcpf_facilities": bhcpf_facilities,
            "bhcpf_percentage": round((bhcpf_facilities / total_submissions * 100) if total_submissions > 0 else 0, 2),
            "impact_facilities": impact_facilities,
            "impact_percentage": round((impact_facilities / total_submissions * 100) if total_submissions > 0 else 0, 2),
            "total_funding_amount": round(total_funding_amount, 2),
            "average_funding_per_facility": round((total_funding_amount / total_submissions) if total_submissions > 0 else 0, 2),
            "funding_by_state": [
                {"state": k, "amount": round(v, 2)}
                for k, v in sorted(funding_by_state.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
        },
        "infrastructure_analysis": {
            "facilities_with_power": infrastructure_stats["has_power"],
            "power_percentage": round((infrastructure_stats["has_power"] / total_submissions * 100) if total_submissions > 0 else 0, 2),
            "facilities_with_water": infrastructure_stats["has_water"],
            "water_percentage": round((infrastructure_stats["has_water"] / total_submissions * 100) if total_submissions > 0 else 0, 2),
            "facilities_with_internet": infrastructure_stats["has_internet"],
            "internet_percentage": round((infrastructure_stats["has_internet"] / total_submissions * 100) if total_submissions > 0 else 0, 2),
            "facilities_with_pharmacy": infrastructure_stats["has_pharmacy"],
            "pharmacy_percentage": round((infrastructure_stats["has_pharmacy"] / total_submissions * 100) if total_submissions > 0 else 0, 2),
            "revitalized_facilities": infrastructure_stats["revitalization_count"],
            "revitalization_percentage": round((infrastructure_stats["revitalization_count"] / total_submissions * 100) if total_submissions > 0 else 0, 2)
        },
        "human_resources_analysis": {
            "total_staff": total_staff,
            "facilities_with_staff": facilities_with_staff,
            "average_staff_per_facility": round((total_staff / facilities_with_staff) if facilities_with_staff > 0 else 0, 2),
            "staff_by_type": [
                {"type": k, "count": v}
                for k, v in sorted(staff_by_type.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
        },
        "services_utilization": {
            "total_patients": total_patients,
            "average_patients_per_facility": round((total_patients / total_submissions) if total_submissions > 0 else 0, 2),
            "top_services_offered": [
                {"service": k, "facilities": v, "percentage": round(
                    (v / total_submissions * 100) if total_submissions > 0 else 0, 2)}
                for k, v in sorted(services_offered.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
        },
        "patient_satisfaction": {
            "average_score": round((sum(satisfaction_scores) / len(satisfaction_scores)) if satisfaction_scores else 0, 2),
            "total_responses": len(satisfaction_scores),
            "scores_by_category": {
                k: {
                    "average": round((sum(v) / len(v)) if v else 0, 2),
                    "count": len(v)
                }
                for k, v in satisfaction_by_category.items()
            }
        },
        "summary": {
            "total_facilities": total_submissions,
            "facilities_with_complete_data": sum(1 for s in submissions if s.facility_condition and s.ownership_type),
            "data_completeness_percentage": round((sum(1 for s in submissions if s.facility_condition and s.ownership_type) / total_submissions * 100) if total_submissions > 0 else 0, 2)
        }
    }
