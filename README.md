\# 🛡️ Adaptive Hybrid Intrusion Detection System



\### AI-Powered Real-Time Network Security Monitoring



An \*\*Adaptive Hybrid Intrusion Detection System (IDS)\*\* that combines \*\*Autoencoder-based anomaly detection\*\* with a \*\*Deep Neural Network (DNN) classifier\*\* to monitor network traffic, identify known attacks, detect previously unseen anomalous traffic, assess risk, and provide real-time security monitoring through a Streamlit dashboard.



\---



\## 📌 Overview



Traditional signature-based Intrusion Detection Systems primarily depend on previously known attack signatures. This can make it difficult to identify new or previously unseen attack patterns.



This project uses a \*\*hybrid AI-based detection architecture\*\*:



```text

Network Traffic

&#x20;     │

&#x20;     ▼

78 Network Traffic Features

&#x20;     │

&#x20;     ▼

Feature Scaling

&#x20;     │

&#x20;     ├──────────────────────┐

&#x20;     ▼                      ▼

Autoencoder              DNN Classifier

&#x20;     │                      │

&#x20;     ▼                      ▼

Reconstruction Error     Attack Class

&#x20;     │                      │

&#x20;     ▼                      │

Anomaly Detection            │

&#x20;     │                      │

&#x20;     └──────────┬───────────┘

&#x20;                ▼

&#x20;       Hybrid Detection Logic

&#x20;                │

&#x20;                ▼

&#x20;      Risk Assessment

&#x20;                │

&#x20;                ▼

&#x20;       SQLite Attack History

&#x20;                │

&#x20;                ▼

&#x20;      Real-Time SOC Dashboard

```



The system therefore combines \*\*unsupervised anomaly detection\*\* with \*\*supervised attack classification\*\*.



\---



\## 🚀 Key Features



\* Real-time network-flow monitoring

\* 78 CICIDS-style traffic features

\* Autoencoder-based anomaly detection

\* DNN-based attack classification

\* Known attack identification

\* Unknown anomaly detection

\* Reconstruction-error-based risk assessment

\* Hybrid anomaly + classification decision

\* Persistent SQLite attack history

\* FastAPI prediction API

\* Streamlit Security Operations Center dashboard

\* Real-time detection statistics

\* Attack intelligence visualization

\* Risk profile visualization

\* Reconstruction-error monitoring

\* Global source/destination IP visualization

\* Automatic dashboard refresh



\---



\## 🧠 Hybrid AI Detection



The detection engine consists of two complementary components.



\### 1. Autoencoder — Anomaly Detection



The Autoencoder learns the normal structure of network traffic.



During prediction, the incoming 78-feature traffic vector is passed through the trained Autoencoder.



The model reconstructs the input:



```text

Input Traffic

&#x20;    │

&#x20;    ▼

Encoder

&#x20;    │

&#x20;    ▼

Latent Representation

&#x20;    │

&#x20;    ▼

Decoder

&#x20;    │

&#x20;    ▼

Reconstructed Traffic

```



The system then calculates the difference between the original and reconstructed feature vectors.



\### Reconstruction Error



The reconstruction error is calculated from the difference between the input and reconstructed vectors.



Conceptually:



```text

Reconstruction Error

&#x20;       =

Mean Squared Error

between original features

and reconstructed features

```



A larger reconstruction error indicates that the observed traffic differs significantly from patterns learned by the Autoencoder.



The current trained system uses an Autoencoder threshold stored in:



```text

models/autoencoder\_threshold\_combined.pkl

```



Current threshold:



```text

0.04958238299974599

```



Traffic exceeding the learned threshold can be treated as anomalous.



\---



\## 🎯 DNN Attack Classification



The second component is a Deep Neural Network classifier.



The classifier is trained to identify the attack classes represented in the training data.



The current label encoder contains:



```text

Benign

DoS attacks-GoldenEye

DoS attacks-Slowloris

FTP-BruteForce

SSH-Bruteforce

```



The classifier produces an attack prediction together with a confidence value.



\---



\## 🔀 Hybrid Decision



The system combines the Autoencoder anomaly result with the DNN classification result.



This allows the system to distinguish between:



\### Known Attack



Traffic that is classified into one of the known attack categories.



\### Unknown Anomaly



Traffic that is considered anomalous by the Autoencoder but does not correspond to the known attack categories with sufficient confidence.



The dashboard therefore reports both:



```text

Known Attacks

Unknown Attacks

```



\*\*Important:\*\* An `Unknown Attack` classification represents anomalous traffic outside the currently known classification categories. It should not automatically be interpreted as a confirmed zero-day attack without further investigation.



\---



\## ⚠️ Risk Assessment



Risk is assessed using the detected traffic and reconstruction error.



The dashboard categorizes events into levels such as:



```text

HIGH

MEDIUM

LOW

UNKNOWN

```



Higher reconstruction errors indicate greater deviation from learned traffic patterns and can therefore contribute to a higher risk classification.



\---



\## 📊 Model Evaluation



The trained classification system was evaluated on:



```text

Test Samples: 417,060

```



\### Overall Performance



| Metric             |      Score |

| ------------------ | ---------: |

| Accuracy           | \*\*99.99%\*\* |

| Weighted Precision | \*\*99.99%\*\* |

| Weighted Recall    | \*\*99.99%\*\* |

| Weighted F1        | \*\*99.99%\*\* |

| Macro F1           | \*\*99.93%\*\* |



\### Per-Class Performance



| Class                 | Precision | Recall |     F1 |

| --------------------- | --------: | -----: | -----: |

| Benign                |    1.0000 | 0.9999 | 1.0000 |

| DoS attacks-GoldenEye |    0.9999 | 0.9995 | 0.9997 |

| DoS attacks-Slowloris |    0.9941 | 1.0000 | 0.9971 |

| FTP-BruteForce        |    0.9999 | 1.0000 | 0.9999 |

| SSH-Bruteforce        |    0.9999 | 0.9998 | 0.9999 |



The confusion matrix showed very few misclassifications across the evaluated classes.



\---



\## 🌐 Real-Time Detection



The system can process live network-flow information and send the extracted 78-feature vector to the prediction API.



The current API endpoint is:



```text

POST /predict

```



Example request structure:



```json

{

&#x20; "src\_ip": "192.168.31.13",

&#x20; "dst\_ip": "192.168.31.88",

&#x20; "protocol": 6,

&#x20; "features": \[78 feature values]

}

```



Example response:



```json

{

&#x20; "attack": "Unknown Attack",

&#x20; "detection\_type": "Unknown Anomaly",

&#x20; "anomaly": true,

&#x20; "reconstruction\_error": 24.977191,

&#x20; "risk": "High",

&#x20; "confidence": 1.0

}

```



\---



\## 🖥️ Security Operations Center Dashboard



The Streamlit dashboard provides a real-time overview of the detection engine.



\### Network Overview



Displays:



\* Network flows

\* Anomalies

\* Known attacks

\* Unknown attacks

\* Anomaly rate

\* High-risk activity



\### Global Threat Map



Displays source and destination IP activity geographically to provide a visual representation of network connections.



\### Threat Profile



Shows the distribution of:



```text

Benign

Known

Unknown

```



\### Reconstruction Error



Displays Autoencoder reconstruction-error activity over time.



This helps identify periods where network traffic significantly deviates from learned patterns.



\### Attack Intelligence



Displays detected attack categories and their frequencies.



\### Risk Profile



Displays the distribution of:



```text

High

Medium

Low

Unknown

```



\### Live Connection Feed



Provides recent network-flow activity and detected security events.



\---



\## 🗄️ Persistent Attack History



Detected events are stored in a SQLite database.



Database:



```text

ids.db

```



Main table:



```text

AttackHistory

```



The database stores information such as:



\* Timestamp

\* Source IP

\* Destination IP

\* Protocol

\* Attack classification

\* Anomaly status

\* Reconstruction error

\* Risk level

\* Confidence



This allows the dashboard to maintain historical detection information instead of relying only on temporary memory.



\---



\## 🧩 Technology Stack



\### Machine Learning



\* Python

\* TensorFlow / Keras

\* Scikit-learn

\* NumPy

\* Pandas

\* Joblib



\### Backend



\* FastAPI

\* Uvicorn



\### Network Monitoring



\* Scapy

\* Network-flow feature extraction



\### Visualization



\* Streamlit

\* Plotly



\### Database



\* SQLite



\---



\## 📁 Project Structure



```text

ids-project/

│

├── app.py

├── dashboard.py

├── dashboard\_unique.py

├── attack\_logger.py

├── database.py

├── live\_capture.py

├── live\_predict.py

├── flow\_builder\_v2.py

├── packet\_features.py

├── packet\_to\_ids.py

├── real\_packet\_capture.py

├── firewall.py

│

├── evaluation.py

├── retrain\_ids\_models.py

├── threshold\_test.py

├── check\_features.py

├── check\_live\_scaling.py

├── create\_label\_encoder.py

│

├── src/

│   ├── train\_autoencoder\_combined.py

│   ├── train\_autoencoder.py

│   ├── train\_dnn.py

│   ├── train\_dnn\_combined.py

│   ├── prepare\_combined.py

│   ├── preprocess\_combined.py

│   └── ...

│

├── data/

│

├── models/

│

├── requirements.txt

├── .gitignore

└── README.md

```



Large datasets, trained model files, generated logs, and the local database are intentionally excluded from version control.



\---



\## ⚙️ Installation



Clone the repository:



```bash

git clone https://github.com/kavyaslamani/ids-project.git

cd ids-project

```



Create a virtual environment:



\### Windows



```powershell

python -m venv venv

.\\venv\\Scripts\\Activate.ps1

```



Install dependencies:



```powershell

pip install -r requirements.txt

```



\---



\## 🤖 Model Files



The trained model files are not included directly in the Git repository.



The system expects the following files:



```text

models/

├── autoencoder\_combined.h5

├── dnn\_combined.h5

├── scaler\_combined.pkl

├── label\_encoder\_combined.pkl

└── autoencoder\_threshold\_combined.pkl

```



These files must be available locally before starting the prediction API.



\---



\## ▶️ Running the System



\### Start the FastAPI Detection API



From the project directory:



```powershell

uvicorn app:app --host 127.0.0.1 --port 8000

```



The API documentation can then be accessed at:



```text

http://127.0.0.1:8000/docs

```



\### Start the Streamlit Dashboard



In another terminal:



```powershell

streamlit run dashboard\_unique.py

```



The dashboard will normally be available at:



```text

http://localhost:8501

```



\### Live Monitoring



The live-capture and prediction components can then send network-flow features to the FastAPI `/predict` endpoint.



\---



\## 🔄 Detection Pipeline



The complete operational pipeline is:



```text

Network Packets

&#x20;     ↓

Flow Construction

&#x20;     ↓

78 Feature Extraction

&#x20;     ↓

Feature Scaling

&#x20;     ↓

Autoencoder

&#x20;     ↓

Reconstruction Error

&#x20;     ↓

Anomaly Decision

&#x20;     ↓

DNN Classification

&#x20;     ↓

Known / Unknown Decision

&#x20;     ↓

Risk Assessment

&#x20;     ↓

SQLite Database

&#x20;     ↓

Streamlit SOC Dashboard

```



\---



\## 🔐 Security Considerations



This project is intended for \*\*research, academic, and controlled network-monitoring environments\*\*.



Live packet capture may require administrator/root privileges depending on the operating system and network interface.



The system should be tested only on networks and systems for which the user has appropriate authorization.



\---



\## ⚠️ Limitations



\* Detection performance depends on the quality and distribution of the training data.

\* Unknown-anomaly detection does not guarantee identification of a genuine zero-day attack.

\* IP geolocation is an approximate visualization and should not be treated as exact physical location information.

\* Model performance on benchmark/test data may differ from performance on unseen real-world traffic.

\* The currently trained DNN recognizes the attack classes represented by its label encoder.

\* Live monitoring depends on successful network-flow feature extraction.



\---



\## 🚀 Future Enhancements



Potential future improvements include:



\* Additional modern network-attack datasets

\* Continuous/adaptive model retraining

\* More attack classes

\* Advanced threat-intelligence integration

\* Alert notifications

\* Role-based SOC access

\* Long-term database analytics

\* Model explainability

\* Distributed monitoring across multiple hosts

\* Containerized deployment

\* Cloud-based monitoring

\* Enhanced geographic threat visualization



\---



\## 👩‍💻 Project



\*\*Adaptive Hybrid Intrusion Detection System\*\*



An AI-driven cybersecurity research project combining anomaly detection and supervised classification for real-time network security monitoring.



\*\*Repository:\*\*

https://github.com/kavyaslamani/ids-project



