"""
AI Service for PFMO Data Collection System
Provides AI-powered analysis and insights for healthcare facility data
"""

import os
from typing import Dict, List, Any, Optional
import json

# Optional: Uncomment when you add AI libraries
# import openai
# from transformers import pipeline
# import requests


class AIService:
    """AI-powered analysis service for PFMO data"""

    def __init__(self):
        # Initialize AI services (add your API keys here)
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.enabled = bool(self.openai_api_key)

    def analyze_issues_and_comments(self, issues: str, comments: str) -> Dict[str, Any]:
        """
        Analyze issues and comments using NLP to extract:
        - Sentiment (positive/negative/neutral)
        - Key topics/categories
        - Priority level
        - Actionable insights
        """
        if not issues and not comments:
            return {
                "sentiment": "neutral",
                "topics": [],
                "priority": "low",
                "insights": [],
                "summary": "No issues or comments provided"
            }

        combined_text = f"{issues or ''} {comments or ''}".strip()

        # If OpenAI is available, use it for analysis
        if self.enabled:
            try:
                return self._analyze_with_openai(combined_text)
            except Exception as e:
                print(f"OpenAI analysis failed: {e}")

        # Fallback: Basic keyword-based analysis
        return self._basic_text_analysis(combined_text)

    def _analyze_with_openai(self, text: str) -> Dict[str, Any]:
        """Analyze text using OpenAI GPT"""
        # Uncomment when OpenAI is configured
        # import openai
        # openai.api_key = self.openai_api_key
        #
        # response = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     messages=[
        #         {"role": "system", "content": "You are an expert healthcare data analyst. Analyze facility issues and provide insights."},
        #         {"role": "user", "content": f"Analyze this healthcare facility issue/comment and provide: 1) Sentiment (positive/negative/neutral), 2) Key topics, 3) Priority (high/medium/low), 4) Actionable insights. Text: {text}"}
        #     ]
        # )
        #
        # return json.loads(response.choices[0].message.content)

        return self._basic_text_analysis(text)

    def _basic_text_analysis(self, text: str) -> Dict[str, Any]:
        """Basic keyword-based text analysis (fallback)"""
        text_lower = text.lower()

        # Sentiment keywords
        negative_keywords = ['problem', 'issue', 'broken', 'missing',
                             'urgent', 'critical', 'poor', 'bad', 'lack', 'no']
        positive_keywords = ['good', 'excellent',
                             'working', 'available', 'complete', 'satisfied']

        negative_count = sum(
            1 for word in negative_keywords if word in text_lower)
        positive_count = sum(
            1 for word in positive_keywords if word in text_lower)

        if negative_count > positive_count:
            sentiment = "negative"
            priority = "high" if negative_count > 3 else "medium"
        elif positive_count > negative_count:
            sentiment = "positive"
            priority = "low"
        else:
            sentiment = "neutral"
            priority = "medium"

        # Extract topics
        topics = []
        topic_keywords = {
            "infrastructure": ["power", "water", "building", "facility", "structure"],
            "staffing": ["staff", "worker", "personnel", "doctor", "nurse"],
            "funding": ["money", "budget", "funding", "financial", "cost"],
            "equipment": ["equipment", "machine", "device", "tool"],
            "supplies": ["supply", "commodity", "medicine", "drug", "stock"],
            "services": ["service", "patient", "treatment", "care"]
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)

        return {
            "sentiment": sentiment,
            "topics": topics if topics else ["general"],
            "priority": priority,
            "insights": [f"Detected {sentiment} sentiment with {len(topics)} key topics"],
            "summary": text[:200] + "..." if len(text) > 200 else text
        }

    def analyze_patient_satisfaction(self, satisfaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze patient satisfaction survey data
        Returns insights, trends, and recommendations
        """
        if not satisfaction_data:
            return {
                "average_score": 0,
                "insights": [],
                "recommendations": []
            }

        scores = []
        for key, value in satisfaction_data.items():
            if isinstance(value, (int, float)):
                scores.append(value)
            elif isinstance(value, str):
                try:
                    scores.append(float(value))
                except:
                    pass

        avg_score = sum(scores) / len(scores) if scores else 0

        insights = []
        recommendations = []

        if avg_score < 3.0:
            insights.append("Patient satisfaction is below average")
            recommendations.append(
                "Investigate service quality and patient experience")
        elif avg_score >= 4.0:
            insights.append("Patient satisfaction is above average")
            recommendations.append("Maintain current service standards")

        return {
            "average_score": round(avg_score, 2),
            "total_responses": len(scores),
            "insights": insights,
            "recommendations": recommendations,
            "score_distribution": {
                "excellent": sum(1 for s in scores if s >= 4.5),
                "good": sum(1 for s in scores if 3.5 <= s < 4.5),
                "fair": sum(1 for s in scores if 2.5 <= s < 3.5),
                "poor": sum(1 for s in scores if s < 2.5)
            }
        }

    def predict_facility_needs(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict facility needs based on current data
        Uses facility condition, funding, staffing, and infrastructure
        """
        predictions = {
            "priority_level": "medium",
            "predicted_needs": [],
            "risk_factors": [],
            "recommendations": []
        }

        # Analyze facility condition
        condition = submission_data.get("facility_condition", "").lower()
        if condition in ["poor", "critical"]:
            predictions["priority_level"] = "high"
            predictions["risk_factors"].append("Poor facility condition")
            predictions["predicted_needs"].append("Infrastructure improvement")
            predictions["recommendations"].append(
                "Prioritize facility rehabilitation")

        # Analyze staffing
        hr_data = submission_data.get("human_resources_data", {})
        if isinstance(hr_data, dict):
            total_staff = sum(
                int(str(v).split()[0]) if isinstance(v, (str, int)) else 0
                for k, v in hr_data.items()
                if "staff" in k.lower() or "personnel" in k.lower()
            )
            if total_staff < 5:
                predictions["risk_factors"].append("Insufficient staffing")
                predictions["predicted_needs"].append(
                    "Additional healthcare workers")
                predictions["recommendations"].append(
                    "Recruit and train more staff")

        # Analyze funding
        funding_data = submission_data.get("funding_data", {})
        if isinstance(funding_data, dict):
            has_funding = funding_data.get(
                "bhcpf_status") == "Received" or funding_data.get("has_bhcpf")
            if not has_funding:
                predictions["risk_factors"].append("Lack of funding")
                predictions["predicted_needs"].append("Financial support")
                predictions["recommendations"].append(
                    "Apply for BHCPF or IMPACT funding")

        # Analyze infrastructure
        infra_data = submission_data.get("infrastructure_data", {})
        if isinstance(infra_data, dict):
            has_power = infra_data.get(
                "has_power") == "Yes" or infra_data.get("power_available")
            has_water = infra_data.get(
                "has_water") == "Yes" or infra_data.get("water_available")

            if not has_power:
                predictions["predicted_needs"].append("Power supply")
                predictions["recommendations"].append(
                    "Install or repair power infrastructure")
            if not has_water:
                predictions["predicted_needs"].append("Water supply")
                predictions["recommendations"].append(
                    "Ensure reliable water access")

        return predictions

    def detect_data_anomalies(self, submission_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect anomalies and potential data quality issues
        """
        anomalies = []

        # Check for missing critical data
        critical_fields = ["facility_name",
                           "state", "lga", "facility_condition"]
        for field in critical_fields:
            if not submission_data.get(field):
                anomalies.append({
                    "type": "missing_data",
                    "field": field,
                    "severity": "high",
                    "message": f"Missing critical field: {field}"
                })

        # Check GPS coordinates validity
        lat = submission_data.get("latitude")
        lon = submission_data.get("longitude")
        if lat and lon:
            # Check if coordinates are in Nigeria (rough bounds)
            if not (4.0 <= lat <= 14.0) or not (2.0 <= lon <= 15.0):
                anomalies.append({
                    "type": "invalid_location",
                    "field": "coordinates",
                    "severity": "medium",
                    "message": f"Coordinates ({lat}, {lon}) appear to be outside Nigeria"
                })

        # Check for logical inconsistencies
        has_workers = submission_data.get("has_health_workers")
        hr_data = submission_data.get("human_resources_data", {})
        if has_workers == "No" and isinstance(hr_data, dict):
            # Check if HR data exists despite saying no workers
            has_hr_data = any(v for v in hr_data.values() if v)
            if has_hr_data:
                anomalies.append({
                    "type": "inconsistency",
                    "field": "health_workers",
                    "severity": "medium",
                    "message": "Form indicates no health workers but HR data exists"
                })

        return anomalies

    def generate_insights_summary(self, submission_data: Dict[str, Any]) -> str:
        """
        Generate a natural language summary of facility insights
        """
        facility_name = submission_data.get(
            "facility_name", "Unknown Facility")
        state = submission_data.get("state", "Unknown State")
        condition = submission_data.get("facility_condition", "Unknown")

        # Analyze various aspects
        predictions = self.predict_facility_needs(submission_data)
        anomalies = self.detect_data_anomalies(submission_data)

        summary_parts = [
            f"Facility: {facility_name} in {state}",
            f"Condition: {condition}",
        ]

        if predictions["risk_factors"]:
            summary_parts.append(
                f"Risk Factors: {', '.join(predictions['risk_factors'])}")

        if predictions["predicted_needs"]:
            summary_parts.append(
                f"Predicted Needs: {', '.join(predictions['predicted_needs'])}")

        if anomalies:
            summary_parts.append(
                f"Data Quality Issues: {len(anomalies)} anomalies detected")

        return ". ".join(summary_parts) + "."

    def analyze_facility_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze facility image using computer vision
        Detects infrastructure, condition, and potential issues
        """
        # Placeholder for image analysis
        # When implemented, use services like:
        # - Google Cloud Vision API
        # - AWS Rekognition
        # - Azure Computer Vision
        # - OpenAI Vision API

        return {
            "analysis_available": False,
            "message": "Image analysis requires computer vision API integration",
            "suggested_services": [
                "Google Cloud Vision API",
                "AWS Rekognition",
                "Azure Computer Vision",
                "OpenAI Vision API"
            ]
        }


# Singleton instance
ai_service = AIService()


