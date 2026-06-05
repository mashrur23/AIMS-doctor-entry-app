import { Download, Save } from "lucide-react";
import { useState } from "react";

import { exportAllConsultationsExcel, saveConsultation } from "./api/client.js";
import Field from "./components/Field.jsx";
import RepeatingSection from "./components/RepeatingSection.jsx";
import SectionCard from "./components/SectionCard.jsx";
import { createBlankPayload, repeatingSections, sections } from "./formSchema.js";

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function valueAtPath(source, path) {
  return path.reduce((current, key) => current?.[key], source);
}

function setAtPath(source, path, value) {
  const next = clone(source);
  let cursor = next;
  path.slice(0, -1).forEach((key) => {
    cursor[key] = cursor[key] || {};
    cursor = cursor[key];
  });
  cursor[path[path.length - 1]] = value;
  return next;
}

function updateObjectField(source, path, field, value) {
  const current = valueAtPath(source, path) || {};
  return setAtPath(source, path, { ...current, [field]: value });
}

export default function App() {
  const [payload, setPayload] = useState(() => createBlankPayload());
  const [status, setStatus] = useState({ tone: "idle", message: "Draft" });
  const [isSaving, setIsSaving] = useState(false);
  const [savedFiles, setSavedFiles] = useState([]);
  const [exportFile, setExportFile] = useState(null);

  const canContinue = payload.file_name.trim().length > 0;

  const updateRootField = (field, value) => {
    setPayload((current) => ({ ...current, [field]: value }));
    setStatus({ tone: "idle", message: "Draft" });
  };

  const updateNestedField = (path, field, value) => {
    setPayload((current) => updateObjectField(current, path, field, value));
    setStatus({ tone: "idle", message: "Draft" });
  };

  const updateRepeatingRows = (path, rows) => {
    setPayload((current) => setAtPath(current, path, rows));
    setStatus({ tone: "idle", message: "Draft" });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!canContinue) {
      setStatus({ tone: "error", message: "File name required" });
      return;
    }

    setIsSaving(true);
    setStatus({ tone: "idle", message: "Saving" });

    try {
      const response = await saveConsultation(payload);
      const savedFileName = response.result.file_name;
      setSavedFiles((current) => [savedFileName, ...current].slice(0, 5));
      setPayload(createBlankPayload());
      setStatus({ tone: "success", message: `Saved ${savedFileName}; ready for next file` });
    } catch (error) {
      setStatus({ tone: "error", message: error.message });
    } finally {
      setIsSaving(false);
    }
  };

  const exportExcel = async () => {
    setStatus({ tone: "idle", message: "Exporting" });
    try {
      const file = await exportAllConsultationsExcel();
      setExportFile(file);
      setStatus({ tone: "success", message: `Saved ${file.rows} rows to Downloads` });
    } catch (error) {
      setStatus({
        tone: "error",
        message: error.message.includes("fetch") ? "Backend is not running" : error.message,
      });
    }
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">AIMS Clinical Intake</p>
          <h1>Doctor Entry</h1>
          {savedFiles.length > 0 && <p className="saved-line">Recent saved files: {savedFiles.join(", ")}</p>}
        </div>
        <div className="topbar__actions">
          <span className={`save-state save-state--${status.tone}`}>{status.message}</span>
          {exportFile && <span className="download-path">{exportFile.path}</span>}
          <button className="button button--secondary" type="button" onClick={exportExcel}>
            <Download size={18} />
            Export Excel
          </button>
          <button className="button" type="submit" form="consultation-form" disabled={isSaving}>
            <Save size={18} />
            {isSaving ? "Saving" : "Save"}
          </button>
        </div>
      </header>

      <div className="workspace workspace--single">
        <form className="content" id="consultation-form" onSubmit={handleSubmit}>
          <section className="setup-panel">
            <div>
              <h2>File Setup</h2>
              <p>Enter the file name first; the remaining sections attach to that record.</p>
            </div>
            <div className="setup-grid">
              <Field field="file_name" value={payload.file_name} onChange={(value) => updateRootField("file_name", value)} />
              <Field
                field="patient_identifier"
                value={payload.patient_identifier}
                onChange={(value) => updateRootField("patient_identifier", value)}
              />
              <Field
                field="consultation_date"
                type="date"
                value={payload.consultation_date}
                onChange={(value) => updateRootField("consultation_date", value)}
              />
            </div>
          </section>

          {canContinue && (
            <div className="section-stack">
              {sections.map((section) =>
                section.groups.map((group) => (
                  <SectionCard
                    group={group}
                    key={group.title}
                    values={valueAtPath(payload, group.path)}
                    onFieldChange={(field, value) => updateNestedField(group.path, field, value)}
                  />
                )),
              )}
              {repeatingSections.map((section) => (
                <RepeatingSection
                  key={section.title}
                  section={section}
                  rows={valueAtPath(payload, section.path)}
                  onChange={(rows) => updateRepeatingRows(section.path, rows)}
                />
              ))}
              <section className="section-card">
                <div className="section-card__header">
                  <h2>Advice</h2>
                </div>
                <Field
                  field="advice_notes"
                  value={payload.consultation_sections.advice.advice_notes}
                  multiline
                  onChange={(value) => updateNestedField(["consultation_sections", "advice"], "advice_notes", value)}
                />
              </section>
              <section className="section-card">
                <div className="section-card__header">
                  <h2>Transcript</h2>
                </div>
                <Field
                  field="transcript"
                  value={payload.transcript}
                  multiline
                  onChange={(value) => updateRootField("transcript", value)}
                />
              </section>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
