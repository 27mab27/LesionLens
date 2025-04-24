# lesion_agent.py

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# ======================================
# 🧠 Map bounding box to mouth region
# ======================================
def map_bbox_to_location(bbox, image_width=1000):
    x, y, w, h = bbox
    center_x = x + w / 2

    if center_x < image_width * 0.33:
        return "left mandible"
    elif center_x < image_width * 0.66:
        return "central mandibular region"
    else:
        return "right mandible"

# ======================================
# 📋 Format YOLO detection results
# ======================================
def format_detections(detections):
    lines = []
    for det in detections:
        label = det.get("label", "Periapical lesion")
        confidence = det.get("confidence", 0.0) * 100
        bbox = det.get("bbox", [0, 0, 0, 0])
        location = map_bbox_to_location(bbox)
        lines.append(f"- {label.capitalize()} lesion detected in the {location} ({confidence:.1f}% confidence).")
    return "\n".join(lines)

# ======================================
# 🤖 GPT-4o LangChain Agent
# ======================================
llm = ChatOpenAI(model="gpt-4o", temperature=0.3, max_tokens=2048)

prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a dental radiology AI assistant.
Based on object detection results from intra-bony lesion detection models (e.g., YOLO), generate a comprehensive clinical diagnosis report.

Include:
- Description of each lesion and its location
- Confidence interpretation
- Possible diagnosis
- Clinical implications
- Recommended next steps (e.g., CBCT, biopsy)
- Suggested treatment or monitoring plan

Respond in clear, formal medical language.
"""),
    ("human", "{detection_summary}")
])

parser = StrOutputParser()

# ======================================
# 🚀 Main function to use in views or CLI
# ======================================
from datetime import datetime

def generate_diagnostic_report(detections, patient_name=None, clinician="Dr. AI Lens"):
    today = datetime.today().strftime('%Y-%m-%d')
    sections = []

    for idx, det in enumerate(detections, start=1):
        conf = f"{det['confidence'] * 100:.1f}%"
        location = map_bbox_to_location(det['bbox'])

        section = f"""\
{idx}. **{location.title()} Lesion:**
   - **Location:** The lesion is situated in the {location}.
   - **Detection Confidence:** {conf}
   - **Description:** The confidence level suggests a probable abnormality in this region. Further clinical evaluation is advised."""
        sections.append(section)

    full_report = f"""\
**Clinical Diagnosis Report: Intra-Bony Lesions**

**Patient Information:**
- Patient Name: {patient_name or '[Unknown]'}
- Examination Type: Intraoral Radiographic Imaging
- Date of Examination: {today}
- Radiologist/Clinician: {clinician}

**Lesion Descriptions and Locations:**

{chr(10).join(sections)}

**Possible Diagnosis:**

- The lesions detected in the mandible could represent a variety of conditions, including but not limited to:
  - Odontogenic cysts (e.g., dentigerous cyst, radicular cyst)
  - Benign odontogenic tumors (e.g., ameloblastoma, odontoma)
  - Non-odontogenic cysts or tumors (e.g., central giant cell granuloma, fibrous dysplasia)
  - Malignant lesions (less likely but should be considered)

**Clinical Implications:**

- These lesions may indicate underlying pathology, potentially causing pain, swelling, or mobility.
- Early diagnosis is essential to prevent complications such as structural weakening or aggressive progression.

**Recommended Next Steps:**

1. **Advanced Imaging:** CBCT scan is advised for detailed assessment.
2. **Biopsy:** If findings appear suspicious, perform a biopsy to confirm the nature of the lesion.

**Suggested Treatment or Monitoring Plan:**

- **Monitoring:** If benign and asymptomatic, schedule regular imaging.
- **Surgical Intervention:** Recommended for symptomatic or growing lesions.
- **Referral:** Refer to an oral surgeon or pathologist for further care.

**Conclusion:**

The lesions identified in this radiographic image require clinical attention. Following the steps above will ensure proper care and long-term outcomes.

**Radiologist/Clinician Signature:**
- {clinician}
- [Insert Contact Information]
"""

    return full_report
