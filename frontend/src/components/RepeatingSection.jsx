import { Plus, Trash2 } from "lucide-react";

import Field from "./Field.jsx";

export default function RepeatingSection({ section, rows, onChange }) {
  const addRow = () => {
    const blank = Object.fromEntries(section.fields.map((field) => [field, ""]));
    onChange([...(rows || []), blank]);
  };

  const updateRow = (index, field, value) => {
    const nextRows = [...rows];
    nextRows[index] = { ...nextRows[index], [field]: value };
    onChange(nextRows);
  };

  const removeRow = (index) => {
    const nextRows = rows.filter((_, rowIndex) => rowIndex !== index);
    onChange(nextRows.length ? nextRows : [Object.fromEntries(section.fields.map((field) => [field, ""]))]);
  };

  return (
    <section className="section-card">
      <div className="section-card__header">
        <h2>{section.title}</h2>
        <button className="icon-button" type="button" onClick={addRow} title={`Add ${section.title}`}>
          <Plus size={18} />
        </button>
      </div>
      <div className="repeat-list">
        {(rows || []).map((row, index) => (
          <div className="repeat-row" key={`${section.title}-${index}`}>
            <div className="repeat-row__fields">
              {section.fields.map((field) => (
                <Field
                  key={field}
                  field={field}
                  value={row[field]}
                  onChange={(value) => updateRow(index, field, value)}
                />
              ))}
            </div>
            <button className="icon-button icon-button--danger" type="button" onClick={() => removeRow(index)} title="Remove row">
              <Trash2 size={18} />
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}
