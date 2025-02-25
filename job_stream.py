import streamlit as st
from pymongo import MongoClient
from bson import ObjectId

# Load API key from Streamlit secrets
MONGO_CONNECTION_STRING = st.secrets["MongoDB"]["MONGO_CONNECTION_STRING"]

# MongoDB Connection
client = MongoClient(MONGO_CONNECTION_STRING)
db = client["database"]
collection = db["jobs"]

# Enums
SalaryCurrencyEnum = ["USD", "EUR", "PKR"]
SalaryTypeEnum = ["Monthly", "Hourly"]
JobTypeEnum = ["Full-time", "Part-time", "Contract"]
ApplicantPreferenceEnum = ["Local", "Remote", "Nearby"]
GenderEnum = ["Male", "Female", "Any"]
JobShiftEnum = ["Morning", "Evening", "Night"]

def get_or_create(collection_name, field_name, value):
    """Fetches existing ID or creates a new entry if it does not exist."""
    collection = db[collection_name]
    existing = collection.find_one({field_name: value})
    return existing["_id"] if existing else collection.insert_one({field_name: value}).inserted_id

def is_designation_unique(designation_name):
    """Checks if the designation is already used in the jobs collection."""
    return collection.find_one({"designationId": get_or_create("designations", "name", designation_name)}) is None

st.set_page_config(page_title="Job Posting Form")

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
        errors = []

        # Check required text fields
        if not company_name.strip():
            errors.append("Company Name is required.")
        if not industry_name.strip():
            errors.append("Industry Name is required.")
        if not designation_name.strip():
            errors.append("Designation Name is required.")
        if not description.strip():
            errors.append("Job Description is required.")
        if not address_name.strip():
            errors.append("Address is required.")

        # Check if designation is unique
        if not is_designation_unique(designation_name):
            errors.append(f"The designation '{designation_name}' is already in use. Please choose a different one.")

        # Check salary range
        if salary_from > salary_to:
            errors.append("Salary Range 'From' cannot be greater than 'To'.")

        # Check experience range
        if experience_from > experience_to:
            errors.append("Experience 'From' cannot be greater than 'To'.")

        # Check required skills
        required_skills_list = [skill.strip() for skill in required_skills.split(",") if skill.strip()]
        if not required_skills_list:
            errors.append("At least one Required Skill is needed.")

        # Check verified skills
        verified_skills_list = [skill.strip() for skill in verified_skills.split(",") if skill.strip()]
        if not verified_skills_list:
            errors.append("At least one Verified Skill is needed.")

        # Validate search radius for non-remote jobs
        if applicant_preference != "Remote" and search_radius == 0:
            errors.append("Search Radius must be greater than zero for non-remote jobs.")

        if errors:
            for error in errors:
                st.error(error)
        else:
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
                "requiredSkills": [get_or_create("skills", "name", skill) for skill in required_skills_list],
                "verifiedSkills": [get_or_create("skills", "name", skill) for skill in verified_skills_list],
            }

            if applicant_preference != "Remote":
                job_data["searchRadius"] = search_radius

            collection.insert_one(job_data)
            st.success("Job successfully posted!")
