import Field from "./Field.jsx";

export default function SectionCard({ group, values, onFieldChange }) {
  return (
    <section className="section-card">
      <div className="section-card__header">
        <h2>{group.title}</h2>
      </div>
      <div className="field-grid">
        {group.fields.map((field) => (
          <Field
            key={field}
            field={field}
            value={values?.[field] || ""}
            type={group.dateFields?.includes(field) ? "date" : "text"}
            multiline={group.longFields?.includes(field)}
            onChange={(value) => onFieldChange(field, value)}
          />
        ))}
      </div>
    </section>
  );
}
