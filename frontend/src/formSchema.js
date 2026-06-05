export const sections = [
  {
    id: "history",
    label: "History",
    groups: [
      {
        title: "Family History",
        path: ["patient_sections", "family_history"],
        fields: ["father", "mother", "siblings", "others"],
      },
      {
        title: "Allergic History",
        path: ["patient_sections", "allergic_history"],
        fields: ["food", "medicine", "pollen", "dust", "mites", "others"],
      },
      {
        title: "Personal History",
        path: ["patient_sections", "personal_history"],
        fields: ["smoking", "alcohol", "activity_level", "food_preferences", "others"],
      },
      {
        title: "Gynae Obs History",
        path: ["patient_sections", "gynae_obs_history"],
        fields: [
          "lmp",
          "edd",
          "para",
          "gravida",
          "alc",
          "delivery_history",
          "contraceptives_history",
          "pv_examination",
        ],
        dateFields: ["lmp", "edd"],
      },
    ],
  },
  {
    id: "screening",
    label: "Screening",
    groups: [
      {
        title: "Health Screening",
        path: ["consultation_sections", "health_screening"],
        fields: ["blood_pressure", "pulse_rate", "temperature", "respiratory_rate", "weight", "height", "bmi"],
      },
      {
        title: "Clinical Exam",
        path: ["consultation_sections", "clinical_exam"],
        fields: ["anaemia", "jaundice", "cyanosis", "edema", "systemic_examination_notes"],
        longFields: ["systemic_examination_notes"],
      },
    ],
  },
];

export const repeatingSections = [
  {
    title: "Chief Complaints",
    path: ["consultation_sections", "chief_complaints"],
    fields: ["complaint", "duration"],
  },
  {
    title: "Investigations",
    path: ["consultation_sections", "investigations"],
    fields: ["investigation_name"],
  },
  {
    title: "Diagnoses",
    path: ["consultation_sections", "diagnoses"],
    fields: ["diagnosis_name", "diagnosis_note"],
  },
  {
    title: "Medications",
    path: ["consultation_sections", "medications"],
    fields: ["medicine_name", "dosage", "frequency", "duration", "instruction"],
  },
];

export function createBlankPayload() {
  return {
    file_name: "",
    patient_identifier: "",
    consultation_date: new Date().toISOString().slice(0, 10),
    transcript: "",
    patient_sections: {
      family_history: {},
      allergic_history: {},
      personal_history: {},
      gynae_obs_history: {},
    },
    consultation_sections: {
      chief_complaints: [{ complaint: "", duration: "" }],
      health_screening: {},
      clinical_exam: {},
      investigations: [{ investigation_name: "" }],
      diagnoses: [{ diagnosis_name: "", diagnosis_note: "" }],
      medications: [{ medicine_name: "", dosage: "", frequency: "", duration: "", instruction: "" }],
      advice: { advice_notes: "" },
    },
  };
}

export function labelFor(field) {
  return field
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}
