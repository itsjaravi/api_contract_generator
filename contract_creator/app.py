import streamlit as st
from contract_creator.ai_utils import generate_contract_with_ai
import json

# rest of the code remains the same...


st.set_page_config(page_title="API Contract Generator", layout="wide")
st.title("📃 API Contract Generator (with AI)")

# Metadata
creator = st.text_input("Creator Name")
version = st.text_input("Document Version")
context = st.text_area("Context/Description of the API")

# Endpoints
st.subheader("API Endpoints")
endpoint_list = []
num_endpoints = st.number_input("How many endpoints?", min_value=1, value=1)
for i in range(num_endpoints):
    with st.expander(f"Endpoint {i+1}"):
        name = st.text_input(f"Endpoint Name {i+1}", key=f"ep_name_{i}")
        url = st.text_input(f"Endpoint URL {i+1}", key=f"ep_url_{i}")
        endpoint_list.append({"name": name, "url": url})

# Dynamic JSON Field Builder
def field_input(prefix_path):
    name_key = f"{prefix_path}_name"
    type_key = f"{prefix_path}_type"
    length_key = f"{prefix_path}_length"
    comments_key = f"{prefix_path}_comments"

    datatype = st.text_input(f"Data Type", key=type_key)
    length = st.text_input(f"Length", key=length_key)
    comments = st.text_input(f"Comments", key=comments_key)
    return {
        "type": datatype,
        "length": length,
        "comments": comments
    }

def nested_fields(title, prefix_path):
    st.subheader(title)
    result = {}

    num_fields_key = f"{prefix_path}_num"
    num_fields = st.number_input(
        f"How many {title.lower()} fields?", min_value=1, value=1, key=num_fields_key
    )

    for i in range(num_fields):
        field_prefix = f"{prefix_path}_{i}"
        with st.expander(f"{title} Field {i+1}", expanded=True):
            field_name_key = f"{field_prefix}_fieldname"
            field_name = st.text_input("Field Name", key=field_name_key)

            is_nested_key = f"{field_prefix}_isnested"
            is_nested = st.checkbox("Is Nested?", key=is_nested_key)

            if is_nested:
                nested = nested_fields(f"{title} → {field_name}", field_prefix)
                result[field_name] = nested
            else:
                result[field_name] = field_input(field_prefix)
    return result

request_fields = nested_fields("Request Fields", "req")
response_fields = nested_fields("Response Fields", "res")

# Generate Contract
if st.button("Generate Contract"):
    contract = {
        "creator": creator,
        "version": version,
        "context": context,
        "endpoints": endpoint_list,
        "request": request_fields,
        "response": response_fields
    }

    st.subheader("🧾 Contract JSON")
    st.json(contract)

    prompt = f"""
I have the following API contract definition. Please review and generate a detailed contract document.

{json.dumps(contract, indent=2)}
    """

    with st.spinner("Calling AI model to generate full contract..."):
        contract_doc = generate_contract_with_ai(prompt)

    st.subheader("📘 AI-Generated Contract Document")
    st.markdown(contract_doc)
