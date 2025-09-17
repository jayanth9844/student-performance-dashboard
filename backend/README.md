# Student Performance Dashboard - Backend

A FastAPI-based machine learning API for predicting student assignment scores with Redis caching and batch processing capabilities.

## 🚀 Features

- **Single & Batch Predictions**: Predict assignment scores for individual students or batches up to 100 students
- **Redis Caching**: Intelligent caching with 1-hour expiration for optimal performance
- **Memory Optimized**: Designed for Render free tier (512MB RAM) with efficient batch processing
- **Performance Monitoring**: Built-in cache statistics and processing metrics
- **Production Ready**: Complete with authentication, validation, and error handling

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes_predict.py    # Prediction endpoints
│   │   ├── routes_auth.py       # Authentication
│   │   └── routes_admin.py      # Cache management
│   ├── cache/
│   │   └── redis_cache.py       # Redis operations
│   ├── core/
│   │   ├── config.py           # Configuration
│   │   └── dependencies.py     # FastAPI dependencies
│   ├── services/
│   │   └── model_service.py    # ML model operations
│   └── main.py                 # FastAPI application
├── training/
│   ├── train_model.py          # Model training script
│   └── train_utils.py          # Training utilities
├── examples/
│   └── batch_prediction_example.py  # Usage examples
├── requirements.txt            # Python dependencies
├── render.yaml                # Render deployment config
└── Dockerfile                 # Docker configuration
```

## 🔧 Installation & Setup

### Local Development

1. **Install Dependencies**
```bash
conda activate fastapi-env
pip install -r requirements.txt
```

2. **Train the Model**
```bash
cd training
python train_model.py
```

3. **Run the API**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Development

```bash
docker-compose up --build
```

Access the API at: http://localhost:8000

## 🌐 Deployment on Render

1. **Push to GitHub**: Ensure your code is in a GitHub repository
2. **Create Render Account**: Sign up at [render.com](https://render.com)
3. **Deploy**: Use the `render.yaml` configuration file for automatic deployment
4. **Environment Variables**: Set your API_KEY in Render dashboard

## 📊 API Endpoints

### Single Prediction
```http
POST /predict
Content-Type: application/json
Authorization: Bearer <jwt_token>
X-API-Key: <api_key>

{
  "comprehension": 75.5,
  "attention": 82.0,
  "focus": 78.3,
  "retention": 80.1,
  "engagement_time": 120
}
```

### Batch Prediction
```http
POST /predict/batch
Content-Type: application/json
Authorization: Bearer <jwt_token>
X-API-Key: <api_key>

{
  "students": [
    {
      "comprehension": 75.5,
      "attention": 82.0,
      "focus": 78.3,
      "retention": 80.1,
      "engagement_time": 120
    }
  ]
}
```

### Cache Statistics
```http
GET /admin/cache/stats
Authorization: Bearer <jwt_token>
```

## 🎯 Usage Examples

Run the example script to test batch predictions:

```bash
python examples/batch_prediction_example.py
```

## 🔧 Configuration

### Environment Variables

- `API_KEY`: Your API authentication key
- `JWT_SECRET_KEY`: JWT signing secret (auto-generated on Render)
- `REDIS_URL`: Redis connection URL (auto-configured on Render)

### Model Features

The ML model expects these input features:
- `comprehension`: Student comprehension score (0-100)
- `attention`: Attention level score (0-100)
- `focus`: Focus capability score (0-100)
- `retention`: Information retention score (0-100)
- `engagement_time`: Time spent engaged (0-300 minutes)

## 📈 Performance Optimization

### Batch Processing
- Maximum 100 students per batch (free tier optimized)
- Internal processing in chunks of 50 for memory efficiency
- Redis pipeline operations for cache efficiency

### Caching Strategy
- MD5 hash keys for consistent caching
- 1-hour expiration to manage Redis memory
- LRU eviction policy for optimal memory usage
- Batch cache operations to reduce network calls

## 🛠 Development

### Training New Models

1. Update training data in `data/student_personas_named.csv`
2. Run training script: `python training/train_model.py`
3. Models are saved to `app/models/`

### Adding New Features

1. Update the `StudentFeatures` model in `routes_predict.py`
2. Modify the feature columns in `model_service.py`
3. Retrain the model with new features

## 🚀 Production Considerations

### Render Free Tier Limits
- 512MB RAM limit
- Redis memory management with LRU policy
- Batch size limitations for memory efficiency
- 1-hour cache expiration to prevent memory overflow

### Monitoring
- Built-in cache hit rate monitoring
- Processing time metrics
- Redis statistics endpoint
- Error handling and logging

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
