# -*- coding: utf-8 -*-
"""aistockpredictionmdoel.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1R3rD6pY-TyN_A8cXA21mJUi1u9gIjKuy
"""

# Install yfinance
!pip install yfinance

import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
from datetime import datetime, timedelta

# Download stock data
stock_data = yf.download('NVDA', start='2014-07-01', end='2024-07-01')

# Scale the data
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(stock_data['Close'].values.reshape(-1, 1))

# Create dataset
def create_dataset(data, time_step):
    X, y = [], []
    for i in range(len(data) - time_step - 1):
        X.append(data[i:(i + time_step), 0])
        y.append(data[i + time_step, 0])
    return np.array(X), np.array(y)

time_step = 100
X, y = create_dataset(scaled_data, time_step)

# Split data into train and test sets
train_size = 0.8
X_train, X_test = X[:int(X.shape[0]*train_size)], X[int(X.shape[0]*train_size):]
y_train, y_test = y[:int(y.shape[0]*train_size)], y[int(y.shape[0]*train_size):]

# Reshape data to fit the LSTM input requirements
X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

# Build the LSTM model
model = Sequential()
model.add(LSTM(units=64, return_sequences=True, input_shape=(time_step, 1)))
model.add(LSTM(units=64))
model.add(Dense(units=64))
model.add(Dense(units=1))

# Compile and fit the model
model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(X_train, y_train, epochs=10, batch_size=64)

# Evaluate the model
test_loss = model.evaluate(X_test, y_test)
print('Test Loss:', test_loss)

# Predict the test data
predictions = model.predict(X_test)
predictions = scaler.inverse_transform(predictions)

# Plot the original and predicted data
original_data = stock_data['Close'].values
predicted_data = np.empty_like(original_data)
predicted_data[:] = np.nan
predicted_data[-len(predictions):] = predictions.reshape(-1)

plt.plot(original_data, label='Original Data')
plt.plot(predicted_data, label='Predicted Data')
plt.legend()
plt.show()

# Predict the next week's stock prices
X_input = scaled_data[-time_step:].reshape(1, time_step, 1)
predictions = []

for _ in range(7):
    next_prediction = model.predict(X_input)
    predictions.append(next_prediction[0, 0])
    X_input = np.append(X_input[:, 1:, :], next_prediction.reshape(1, 1, 1), axis=1)

predicted_prices = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))

# Generate dates for the next week
dates = [datetime.now().date() + timedelta(days=i) for i in range(7)]

# Plotting the predictions
plt.figure(figsize=(14, 7))
plt.plot(dates, predicted_prices, marker='o', linestyle='-', color='orange', label='Predicted Data')
plt.xlabel('Date')
plt.ylabel('Stock Price')
plt.title('Predicted Stock Prices for the Next Week')
plt.legend()
plt.grid(True)
plt.show()

# Print the predicted opening and closing prices for each day
print("Predicted Opening and Closing Prices for the Next Week:")
for i, date in enumerate(dates):
    print(f"{date}: Open: {predicted_prices[i][0]:.2f}, Close: {predicted_prices[i][0]:.2f}")

