import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

# Load data
csv_path = 'data/all_transactions_ready.csv'
df = pd.read_csv(csv_path)

# Use only necessary columns and drop missing
X = df['description'].astype(str)
y = df['category'].astype(str)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Vectorize descriptions
vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2), max_features=2000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train classifier
clf = LogisticRegression(max_iter=1000, multi_class='auto')
clf.fit(X_train_vec, y_train)

# Evaluate
accuracy = clf.score(X_test_vec, y_test)
print(f"Test accuracy: {accuracy:.3f}")

# Save the model and vectorizer
joblib.dump(clf, 'app/models/transaction_classifier.joblib')
joblib.dump(vectorizer, 'app/models/vectorizer.joblib')
print("Model and vectorizer saved.") 