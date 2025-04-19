import os
import pandas as pd
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import confusion_matrix
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

# Load dataset
df = pd.read_csv("data/Enhanced_Mental_Health_Dataset.csv")

# Split features and target
X = df.drop(columns=["Diagnosis"])
y = df["Diagnosis"]

# Identify columns
categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()
numerical_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()

# Define transformers
numerical_transformer = SimpleImputer(strategy="mean")
categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

# Column transformer
preprocessor = ColumnTransformer(
    transformers=[
        ("num", numerical_transformer, numerical_cols),
        ("cat", categorical_transformer, categorical_cols)
    ])

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Preprocess input
X_train_proc = preprocessor.fit_transform(X_train)
X_test_proc = preprocessor.transform(X_test)

# Define models with 100 epochs
xgb = XGBClassifier(n_estimators=100, eval_metric='mlogloss', use_label_encoder=False)
lgbm = LGBMClassifier(n_estimators=100)
catboost = CatBoostClassifier(n_estimators=100, verbose=0)

# Train models
xgb.fit(X_train_proc, y_train)
lgbm.fit(X_train_proc, y_train)
catboost.fit(X_train_proc, y_train)

# Predict probabilities from each model
proba_xgb = xgb.predict_proba(X_test_proc)
proba_lgbm = lgbm.predict_proba(X_test_proc)
proba_catboost = catboost.predict_proba(X_test_proc)

# Weighted ensemble prediction: 50% XGB, 25% LGBM, 25% CatBoost
ensemble_proba = (
    0.5 * proba_xgb +
    0.25 * proba_lgbm +
    0.25 * proba_catboost
)

# Final prediction by taking argmax of weighted average
y_pred_ensemble = np.argmax(ensemble_proba, axis=1)

# Compute confusion matrix
cm = confusion_matrix(y_test, y_pred_ensemble)
class_names = label_encoder.classes_
n_classes = len(class_names)
total = np.sum(cm)

# Per-Class Accuracy
print("\n📊 Per-Class Accuracy (Ensemble - Weighted):")
for i in range(n_classes):
    TP = cm[i, i]
    FN = np.sum(cm[i, :]) - TP
    FP = np.sum(cm[:, i]) - TP
    TN = total - (TP + FP + FN)
    acc_i = (TP + TN) / total
    print(f"{class_names[i]}: {acc_i:.4f}")

# Save models and encoders
os.makedirs("train", exist_ok=True)
with open("train/xgb_model.pkl", "wb") as f:
    pickle.dump(xgb, f)
with open("train/lgbm_model.pkl", "wb") as f:
    pickle.dump(lgbm, f)
with open("train/catboost_model.pkl", "wb") as f:
    pickle.dump(catboost, f)
with open("train/preprocessor.pkl", "wb") as f:
    pickle.dump(preprocessor, f)
with open("train/label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)
