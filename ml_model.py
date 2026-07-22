import joblib

with open("model.pkl", "rb") as f:
    model = joblib.load(f)


def predict(features) :
    prediction = model.predict([features])
    return int(prediction[0])