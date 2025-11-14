# AI Integration Guide for PFMO Data Collection System

## Overview

The PFMO system now includes AI-powered analysis capabilities to provide intelligent insights from healthcare facility data.

## Current AI Features

### 1. **Text Analysis (NLP)**
- **Sentiment Analysis**: Analyzes issues and comments to determine sentiment (positive/negative/neutral)
- **Topic Extraction**: Identifies key topics from text (infrastructure, staffing, funding, etc.)
- **Priority Detection**: Automatically determines priority level based on content
- **Insights Generation**: Provides actionable insights from text analysis

### 2. **Patient Satisfaction Analysis**
- Analyzes satisfaction survey data
- Calculates average scores and distributions
- Provides recommendations based on satisfaction levels

### 3. **Predictive Analytics**
- **Facility Needs Prediction**: Predicts what facilities need based on current data
- **Risk Factor Identification**: Identifies facilities at risk
- **Priority Assessment**: Determines priority levels for interventions

### 4. **Data Quality & Anomaly Detection**
- Detects missing critical data
- Validates GPS coordinates
- Identifies logical inconsistencies
- Flags potential data entry errors

### 5. **At-Risk Facility Identification**
- Automatically identifies facilities requiring urgent attention
- Categorizes by priority level
- Lists risk factors and predicted needs

## API Endpoints

### Get Submission Insights
```
GET /api/v1/ai/submission/{submission_id}/insights
```
Returns comprehensive AI analysis for a specific submission.

### Get At-Risk Facilities
```
GET /api/v1/ai/facilities/at-risk
```
Lists all facilities identified as at-risk with priority levels.

### Get AI Recommendations
```
GET /api/v1/ai/recommendations?state={state}
```
Returns AI-generated recommendations categorized by type (infrastructure, staffing, funding, general).

### Analyze Text
```
POST /api/v1/ai/analyze-text
Body: { "text": "your text here" }
```
Analyzes any text for sentiment, topics, and insights.

## Advanced AI Integration Options

### Option 1: OpenAI Integration (Recommended)

1. **Install OpenAI SDK**:
```bash
pip install openai
```

2. **Set API Key**:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

3. **Update `ai_service.py`**:
Uncomment the OpenAI code in `_analyze_with_openai()` method.

**Benefits**:
- Advanced NLP capabilities
- Better sentiment analysis
- More accurate topic extraction
- Natural language summaries

### Option 2: Google Cloud AI

1. **Install Google Cloud AI**:
```bash
pip install google-cloud-aiplatform
```

2. **Use Cases**:
- Natural Language API for sentiment analysis
- Vision API for facility image analysis
- AutoML for custom predictions

### Option 3: Azure Cognitive Services

1. **Install Azure SDK**:
```bash
pip install azure-cognitiveservices-language-textanalytics
```

2. **Use Cases**:
- Text Analytics for sentiment and key phrases
- Computer Vision for image analysis
- Anomaly Detector for data quality

### Option 4: AWS AI Services

1. **Install AWS SDK**:
```bash
pip install boto3
```

2. **Use Cases**:
- Amazon Comprehend for NLP
- Amazon Rekognition for image analysis
- Amazon Forecast for predictions

## Image Analysis Integration

To enable facility image analysis:

1. **Choose a Vision API** (Google Cloud Vision, AWS Rekognition, Azure Computer Vision, or OpenAI Vision)

2. **Update `analyze_facility_image()` in `ai_service.py`**:
```python
def analyze_facility_image(self, image_path: str) -> Dict[str, Any]:
    # Example with Google Cloud Vision
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    
    image = vision.Image(content=content)
    response = client.label_detection(image=image)
    
    labels = [label.description for label in response.label_annotations]
    
    return {
        "detected_objects": labels,
        "facility_condition_estimate": "Good" if "building" in labels else "Unknown"
    }
```

## Machine Learning Models

### Custom ML Models

You can train custom models for:
- **Facility Condition Prediction**: Predict facility condition based on infrastructure data
- **Resource Need Forecasting**: Predict resource requirements
- **Anomaly Detection**: Custom anomaly detection models

**Example using scikit-learn**:
```python
from sklearn.ensemble import RandomForestClassifier
import joblib

# Train model
model = RandomForestClassifier()
# ... training code ...

# Save model
joblib.dump(model, 'facility_condition_model.pkl')

# Use in AI service
def predict_condition(self, data):
    model = joblib.load('facility_condition_model.pkl')
    prediction = model.predict([features])
    return prediction
```

## Cost Considerations

### Current Implementation (Free)
- Basic keyword-based analysis
- Rule-based predictions
- No external API costs

### With OpenAI (Paid)
- ~$0.01-0.03 per analysis
- More accurate insights
- Better natural language understanding

### With Cloud AI Services
- Pay-per-use pricing
- Typically $0.001-0.01 per request
- Scalable and reliable

## Best Practices

1. **Start Simple**: Use the basic implementation first
2. **Add AI Gradually**: Integrate advanced AI as needed
3. **Cache Results**: Store AI analysis results to avoid re-computation
4. **Error Handling**: Always have fallback to basic analysis
5. **Privacy**: Ensure patient data is handled according to regulations
6. **Cost Monitoring**: Track API usage and costs

## Future Enhancements

- **Real-time Alerts**: AI-powered alerts for critical issues
- **Predictive Maintenance**: Predict when facilities need maintenance
- **Resource Optimization**: AI recommendations for resource allocation
- **Chatbot Assistant**: AI assistant for data collectors
- **Automated Reporting**: AI-generated executive summaries
- **Image Classification**: Automatic facility condition assessment from photos

## Getting Started

1. The basic AI features are already working (keyword-based analysis)
2. Access AI Insights from the web app sidebar
3. Try the text analysis tool
4. View at-risk facilities
5. Check AI recommendations

To enable advanced AI:
1. Choose an AI service provider
2. Get API keys
3. Update `ai_service.py` with your credentials
4. Uncomment the advanced analysis code



