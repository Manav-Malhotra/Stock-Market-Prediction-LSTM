#BTC Next Day Prediction
#By MANAV MALHOTRA 
#Integrated on trading view custom indicator 
ß
#importing necessary files 
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pandas_datareader as web
import datetime as dt

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM

#Load Crypto Data
company = 'BTC-USD'
start = dt.datetime(2020, 1, 1)
end = dt.datetime(2021,1,1) #Time Series Data

data = web.DataReader(company, 'yahoo', start, end)
print(data)

#Prepare Data
scaler=MinMaxScaler(feature_range=(0,1))
scaled_data=scaler.fit_transform(data['Close'].values.reshape(-1,1))

prediction_days = 60

x_train=[]
y_train=[]

for x in range(prediction_days, len(scaled_data)):
    x_train.append(scaled_data[x-prediction_days:x, 0]) #Model Can Learn to predict the 61st value 
    y_train.append(scaled_data[x, 0])

x_train, y_train = np.array(x_train), np.array(y_train)
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1)) #Reshape by so that it can work with NN 

#Model Creation
model = Sequential()

model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1))) #LSTM is recurrent so it is gonna feedback the information
model.add(Dropout(0.2))

model.add(LSTM(units=50, return_sequences=True))
model.add(Dropout(0.2))

model.add(LSTM(units=50))
model.add(Dropout(0.2))

model.add(Dense(units=1)) #prediction of the next closing value

model.compile(optimizer='adam', loss='mean_squared_error') #LOSS FUNCTION
model.fit(x_train, y_train, epochs=25, batch_size=32) 


#Load Test Data
test_start=dt.datetime(2022, 1, 1)
test_end=dt.datetime.now()

test_data = web.DataReader(company, 'yahoo', test_start, test_end)
actual_prices=test_data['Close'].values

total_dataset=pd.concat((data['Close'], test_data['Close']), axis=0) #Combines Both training as well as test data

model_inputs=total_dataset[len(total_dataset)-len(test_data)-prediction_days:].values #INPUT FOR THE MODEL
model_inputs = model_inputs.reshape(-1, 1)
model_inputs = scaler.transform(model_inputs) #Re Transform to actual


# Make Predictions on Test Data
x_test=[]

for x in range(prediction_days, len(model_inputs)):
    x_test.append(model_inputs[x-prediction_days:x, 0])

x_test=np.array(x_test)
x_test=np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1)) #Reshaping for Neural Network 

#We dont need need y_test since we already have bitcoin price

predicted_prices=model.predict(x_test)
predicted_prices=scaler.inverse_transform(predicted_prices)

# Plot the test predictions
plt.plot(actual_prices, color = "black", label=f"Actual {company} Price")
plt.plot(predicted_prices, color="green", label=f"Predicted {company} Price")
plt.title(f"{company} Crypto Price")
plt.xlabel("Time")
plt.ylabel(f"{company} Crypto Price")
plt.legend()
plt.show()

#Predict Next Day
real_data = [model_inputs[len(model_inputs)+1-prediction_days:len(model_inputs+1), 0]]
real_data = np.array(real_data)
real_data=np.reshape(real_data, (real_data.shape[0], real_data.shape[1],1))

prediction=model.predict(real_data)
prediction = scaler.inverse_transform(prediction)
print(f"Prediction: {prediction}")
