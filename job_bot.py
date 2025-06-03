from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# RapidAPI credentials
API_KEY = "9a33f6c173mshf4a614942354e3ep123b33jsn4270933aae39"
API_HOST = "jsearch.p.rapidapi.com"

# Function to fetch jobs from RapidAPI
def fetch_jobs(location, experience, skills, posted_within):
    url = "https://jsearch.p.rapidapi.com/search"
    query = f"{skills} jobs in {location} with {experience} years experience"

    params = {
        "query": query,
        "page": "1",
        "num_pages": "1"
    }

    if posted_within:
        params["date_posted"] = posted_within

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return data.get("data", [])
    else:
        return None
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/results", methods=["POST"])
def results():
    location = request.form.get("location")
    experience = request.form.get("experience")
    skills = request.form.get("skills")
    posted_within = request.form.get("posted_within")

    jobs = fetch_jobs(location, experience, skills, posted_within)
    if jobs is None:
        error = "Failed to fetch jobs. Please try again later."
        return render_template("index.html", error=error)

    for job in jobs:
        desc = job.get('job_description', '')
        words = desc.split()
        job['short_description'] = ' '.join(words[:100]) + '...' if len(words) > 100 else desc
        posted_date = job.get('job_posted_at_datetime_utc')
        job['posted_date'] = posted_date[:10] if posted_date else 'N/A'

    return render_template("results.html", jobs=jobs, location=location, experience=experience, skills=skills)

@app.route("/api/jobs", methods=["POST"])
def api_jobs():
    data = request.get_json()

    location = data.get("location")
    experience = data.get("experience")
    skills = data.get("skills")
    posted_within = data.get("posted_within")

    if not location or not skills or experience is None:
        return jsonify({"error": "Missing required fields"}), 400

    jobs = fetch_jobs(location, experience, skills, posted_within)
    if jobs is None:
        return jsonify({"error": "Failed to fetch jobs"}), 500

    for job in jobs:
        desc = job.get('job_description', '')
        words = desc.split()
        job['short_description'] = ' '.join(words[:100]) + '...' if len(words) > 100 else desc
        posted_date = job.get('job_posted_at_datetime_utc')
        job['posted_date'] = posted_date[:10] if posted_date else 'N/A'

    return jsonify({"jobs": jobs}), 200

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))