from apps.config.mongodb import MONGO_CONNECTION_STRING
import streamlit as st
from pymongo import MongoClient
from bson import ObjectId

# Load API key from Streamlit secrets
MONGO_CONNECTION_STRING = st.secrets["MongoDB"]["MONGO_CONNECTION_STRING"]

# MongoDB Connection
client = MongoClient(MONGO_CONNECTION_STRING)  # Update with your DB connection
db = client["latest_database"]  # Replace with your database name
collection = db["jobs"]  # Replace with your collection name

# Enums (Replace with actual values)
SalaryCurrencyEnum = ["USD", "EUR", "PKR"]
SalaryTypeEnum = ["Monthly", "Hourly"]
JobTypeEnum = ["Full-time", "Part-time", "Contract"]
ApplicantPreferenceEnum = ["Local", "Remote", "Nearby"]
GenderEnum = ["Male", "Female", "Any"]
JobShiftEnum = ["Morning", "Evening", "Night"]

def get_or_create(collection_name, field_name, value):
    collection = db[collection_name]
    existing = collection.find_one({field_name: value})
    if existing:
        return existing["_id"]
    return collection.insert_one({field_name: value}).inserted_id

st.set_page_config(
        page_title="Job Posting Form",
)

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.title("Job Posting Form")

with st.form("job_form"):
    company_name = st.text_input("Company Name")
    industry_name = st.text_input("Industry Name")
    designation_name = st.text_input("Designation Name")
    
    salary_from = st.number_input("Salary Range From", min_value=0)
    salary_to = st.number_input("Salary Range To", min_value=0)
    salary_currency = st.selectbox("Salary Currency", SalaryCurrencyEnum)
    salary_type = st.selectbox("Salary Type", SalaryTypeEnum)
    job_type = st.selectbox("Job Type", JobTypeEnum)
    description = st.text_area("Job Description")
    experience_from = st.number_input("Experience From (years)", min_value=0)
    experience_to = st.number_input("Experience To (years)", min_value=0)
    no_of_candidates = st.number_input("Number of Candidates", min_value=1)
    is_verified_candidate_needed = st.checkbox("Verified Candidate Needed")
    address_name = st.text_input("Address")
    is_active = st.checkbox("Is Active", value=False)
    applicant_preference = st.selectbox("Applicant Preference", ApplicantPreferenceEnum)
    gender = st.selectbox("Preferred Gender", GenderEnum)
    job_shift = st.selectbox("Job Shift", JobShiftEnum)
    required_skills = st.text_area("Required Skills (comma separated)")
    verified_skills = st.text_area("Verified Skills (comma separated)")
    search_radius = st.number_input("Search Radius (km)", min_value=0)
    
    submitted = st.form_submit_button("Submit Job")
    
    if submitted:
        job_data = {
            "companyId": get_or_create("companies", "name", company_name),
            "industryId": get_or_create("industries", "name", industry_name),
            "designationId": get_or_create("designations", "name", designation_name),
            "salaryRangeFrom": salary_from,
            "salaryRangeTo": salary_to,
            "salaryCurrency": salary_currency,
            "salaryType": salary_type,
            "jobType": job_type,
            "description": description,
            "experienceFrom": experience_from,
            "experienceTo": experience_to,
            "noOfCandidates": no_of_candidates,
            "isVerifiedCandidateNeeded": is_verified_candidate_needed,
            "addressId": get_or_create("addresses", "location", address_name),
            "isActive": is_active,
            "applicantPreference": applicant_preference,
            "gender": gender,
            "jobShift": job_shift,
            "requiredSkills": [get_or_create("skills", "name", skill.strip()) for skill in required_skills.split(",") if skill.strip()],
            "verifiedSkills": [get_or_create("skills", "name", skill.strip()) for skill in verified_skills.split(",") if skill.strip()],
        }
        
        if applicant_preference != "Remote":
            job_data["searchRadius"] = search_radius
        
        collection.insert_one(job_data)
        st.success("Job successfully posted!")
