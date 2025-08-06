# End-to-End Machine Learning Pipeline: Image Classification

## Video Demo

A short video demonstration of the application in action:

[Watch the Demo on YouTube](YOUR_YOUTUBE_DEMO_LINK_HERE)

## Live Demo

You can access the live deployed version of this application here:

[Live Application URL](YOUR_VERCEL_DEPLOYMENT_URL_HERE)

---

This project provides a complete end-to-end machine learning pipeline for image classification, featuring a Python Flask API backend for model serving and retraining, and a Next.js frontend for user interaction and data visualization.

## Table of Contents

*   [Features](#features)
*   [Technologies Used](#technologies-used)
*   [Project Structure](#project-structure)
*   [Setup Instructions](#setup-instructions)
    *   [Backend Setup (Python Flask)](#backend-setup-python-flask)
    *   [Frontend Setup (Next.js)](#frontend-setup-nextjs)
*   [Usage](#usage)
    *   [Image Prediction](#image-prediction)
    *   [Model Retraining](#model-retraining)
    *   [Data Visualizations & Interpretations](#data-visualizations--interpretations)
*   [Results from Flood Request Simulation](#results-from-flood-request-simulation)
*   [Deployment on Vercel](#deployment-on-vercel)

## Features

*   **Image Prediction:** Upload an image and get real-time predictions from the trained ML model.
*   **Model Retraining:** Upload new datasets (in ZIP format) to trigger on-demand model retraining.
*   **Data Insights:** Visualize class distribution, sample images, and image dimensions of your training data.
*   **Scalable Architecture:** Separated frontend and backend for better maintainability and scalability.
*   **Vercel Deployment Ready:** Configured for seamless deployment on Vercel as a monorepo.

## Technologies Used

*   **Backend:**
    *   Python 3.x
    *   Flask: Web framework for the API.
    *   TensorFlow / Keras: For building, training, and serving the ML model.
    *   Pillow (PIL): For image processing.
    *   Numpy: For numerical operations.
    *   Scikit-learn: For data splitting.
    *   Flask-CORS: For handling Cross-Origin Resource Sharing.
    *   Kagglehub: For dataset download.
*   **Frontend:**
    *   Next.js (React Framework): For building the user interface.
    *   TypeScript: For type-safe JavaScript.
    *   Tailwind CSS: For styling.
    *   shadcn/ui: UI components.
    *   Recharts: For data visualization (charts).
    *   Lucide React: Icons.
*   **Deployment:**
    *   Vercel: Hosting platform for both frontend and backend.
    *   Git LFS: For managing large model files.

## Project Structure

\`\`\`
.
├── app/                                # Next.js frontend (App Router)
│   └── page.tsx                        # Main dashboard page
├── components/                         # Reusable React components (e.g., shadcn/ui)
├── data/                               # Stores downloaded and organized image data (train/test)
│   ├── train/
│   │   ├── cats/
│   │   └── dogs/
│   └── test/
│       ├── cats/
│       └── dogs/
├── models/                             # Stores the trained ML model
│   └── image_classifier_model.h5
├── notebook/
│   └── image_classification_pipeline.ipynb # Jupyter Notebook for training
├── public/                             # Static assets for Next.js
├── scripts/
│   ├── setup_data.py                   # Script to download and organize dataset
│   └── check_data_contents.py          # Utility to check data directories
├── src/                                # Python backend source code
│   ├── api.py                          # Flask API endpoints
│   ├── model.py                        # ML model definition and training functions
│   ├── prediction.py                   # Model loading and prediction logic
│   └── preprocessing.py                # Image preprocessing utilities
├── .gitattributes                      # Git LFS configuration
├── next.config.mjs                     # Next.js configuration
├── postcss.config.js                   # PostCSS configuration for Tailwind CSS
├── package.json                        # Frontend dependencies
├── pnpm-lock.yaml                      # pnpm lock file
├── requirements.txt                    # Backend Python dependencies
├── tailwind.config.ts                  # Tailwind CSS configuration
├── tsconfig.json                       # TypeScript configuration
└── vercel.json                         # Vercel deployment configuration
\`\`\`

## Setup Instructions

Follow these steps to set up and run the project locally.

### Backend Setup (Python Flask)

1.  **Clone the repository:**
    \`\`\`bash
    git clone <your-repository-url>
    cd <your-repository-name>
    \`\`\`

2.  **Create a Python Virtual Environment (recommended):**
    \`\`\`bash
    python -m venv venv
    source venv/bin/activate # On Windows: venv\Scripts\activate
    \`\`\`

3.  **Install Python Dependencies:**
    \`\`\`bash
    pip install -r requirements.txt
    \`\`\`

4.  **Download and Organize Data:**
    Run the `setup_data.py` script to download the Cats vs. Dogs dataset from Kaggle and organize it into the `data/train` and `data/test` directories. This is crucial for both training and data insights.
    \`\`\`bash
    python scripts/setup_data.py
    \`\`\`
    *   **Note:** This script will create `data/train/cats`, `data/train/dogs`, `data/test/cats`, and `data/test/dogs` directories and populate them with images.

5.  **Train the Machine Learning Model:**
    Open and run the Jupyter Notebook to train the model and save it. This will create the `models/image_classifier_model.h5` file.
    \`\`\`bash
    jupyter notebook notebook/image_classification_pipeline.ipynb
    \`\`\`
    *   **Important:** Ensure all cells in the notebook are run successfully. The `MODEL_PATH` in `src/model.py` and `src/prediction.py` points to `../models/image_classifier_model.h5`.

6.  **Start the Flask API Server:**
    Navigate to the project root and run the Flask application.
    \`\`\`bash
    python src/api.py
    \`\`\`
    The API will typically run on `http://localhost:5000`.

### Frontend Setup (Next.js)

1.  **Install Node.js Dependencies:**
    Navigate to the project root and install the frontend dependencies.
    \`\`\`bash
    pnpm install # or npm install
    \`\`\`

2.  **Start the Next.js Development Server:**
    \`\`\`bash
    pnpm dev # or npm run dev
    \`\`\`
    The frontend will typically run on `http://localhost:3000`.

## Usage

Once both the Flask API and Next.js frontend are running, open your browser to `http://localhost:3000`.

### Image Prediction

1.  In the "Model Prediction" section, click "Upload Image".
2.  Select an image file (e.g., a cat or dog image).
3.  Click the "Predict" button.
4.  The prediction result (predicted class and confidence) will be displayed.

### Model Retraining

1.  Prepare a new dataset as a ZIP file. The ZIP file should contain subdirectories for each class (e.g., `new_data.zip` containing `new_data/class_a/image1.jpg`, `new_data/class_b/image2.png`).
2.  In the "Model Retraining" section, click "Upload New Data (ZIP)".
3.  Select your prepared ZIP file.
4.  Click "Trigger Retrain".
5.  The API will extract the data, retrain the model, and update the insights.

### Data Visualizations & Interpretations

This section automatically fetches and displays insights from your `data/train` directory:

*   **Class Distribution:** A bar chart showing the number of images per class.
*   **Sample Images per Class:** Displays a few sample images from each class.
*   **Image Dimensions/Resolution:** Provides min, max, and average dimensions of images.

Ensure `setup_data.py` has been run to populate the `data` directory for these visualizations to work.

## Results from Flood Request Simulation

This section presents the results of a load test performed using Locust.io on the API endpoints.

\`\`\`png file="public/images/locust-results.png" url="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-q7RlHvQa5RC3XAyK6HO1Jtylr2QwRN.png"
\`\`\`

**Interpretation of Results:**

The simulation was run with 20 users, achieving an aggregated 2 Requests Per Second (RPS) with a concerning 33% failure rate.

*   **`/data-insights` (GET):** This endpoint shows very high latency, with an average response time of approximately 171.58 seconds (171580.51 ms) and a median of 108 seconds. This indicates that fetching data insights is a very slow operation, likely due to the extensive image processing involved in calculating dimensions and class distributions. However, it had 0 failures.
*   **`/predict` (POST):** This endpoint has significantly lower latency, with an average response time of 585.14 ms and a median of 400 ms. While faster, it experienced a high number of failures (120 out of 283 requests), contributing heavily to the overall 33% failure rate. This suggests issues with the prediction process under load, possibly related to resource contention or specific error handling.

**Key Takeaways:**

*   The `/data-insights` endpoint needs significant optimization to reduce its extremely high response times.
*   The `/predict` endpoint, despite better latency, has a critical failure rate that needs immediate investigation and resolution to ensure reliability.

## Deployment on Vercel

This project is configured for deployment on Vercel as a monorepo, handling both the Next.js frontend and the Flask API backend.

1.  **`vercel.json`:** The `vercel.json` file in the project root configures Vercel to build the Next.js app and deploy the Flask API as a serverless function. It also sets up routing to direct `/api/*` requests to the Flask backend.
2.  **Git LFS:** Ensure your `.h5` model file is tracked by Git LFS.
    *   Add `*.h5 filter=lfs diff=lfs merge=lfs -text` to your `.gitattributes` file.
    *   If the model file was already committed without LFS, you'll need to migrate it:
        \`\`\`bash
        git lfs track "*.h5"
        git add .gitattributes
        git rm --cached models/image_classifier_model.h5 # Replace with your actual model path
        git add models/image_classifier_model.h5
        git commit -m "Migrate .h5 model to Git LFS"
        git push origin main # Or your branch name
        \`\`\`
    *   This ensures large files are handled correctly during deployment, avoiding "Size of uploaded file exceeds 300MB" errors.
