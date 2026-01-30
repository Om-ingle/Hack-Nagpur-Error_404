import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pickle

# Generate synthetic training data
def generate_training_data(n_samples=1000):
    np.random.seed(42)
    data = []
    
    for _ in range(n_samples):
        age = np.random.randint(18, 80)
        
        # Symptom features (binary)
        chest_pain = np.random.choice([0, 1], p=[0.8, 0.2])
        breathing_difficulty = np.random.choice([0, 1], p=[0.85, 0.15])
        fever = np.random.choice([0, 1], p=[0.7, 0.3])
        headache = np.random.choice([0, 1], p=[0.6, 0.4])
        emergency_keywords = np.random.choice([0, 1], p=[0.95, 0.05])
        
        # Calculate risk score based on features
        risk_score = 0.0
        risk_score += age / 100 * 0.3  # Age factor
        risk_score += chest_pain * 0.4
        risk_score += breathing_difficulty * 0.3
        risk_score += emergency_keywords * 0.8
        risk_score += fever * 0.1
        
        # Add some noise
        risk_score += np.random.normal(0, 0.1)
        risk_score = max(0.0, min(1.0, risk_score))  # Clamp to [0,1]
        
        data.append({
            'age_normalized': age / 100,
            'chest_pain': chest_pain,
            'breathing_difficulty': breathing_difficulty,
            'fever': fever,
            'headache': headache,
            'emergency_keywords': emergency_keywords,
            'risk_score': risk_score
        })
    
    return pd.DataFrame(data)

# Train model
def train_model():
    df = generate_training_data()
    
    features = ['age_normalized', 'chest_pain', 'breathing_difficulty', 
                'fever', 'headache', 'emergency_keywords']
    X = df[features]
    y = df['risk_score']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Save model
    with open('risk_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    print(f"✅ Model trained! Accuracy: {model.score(X_test, y_test):.2f}")
    return model

if __name__ == "__main__":
    train_model()