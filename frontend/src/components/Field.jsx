import { labelFor } from "../formSchema.js";

export default function Field({ field, value, onChange, multiline = false, type = "text" }) {
  return (
    <label className={multiline ? "field field--wide" : "field"}>
      <span>{labelFor(field)}</span>
      {multiline ? (
        <textarea value={value || ""} onChange={(event) => onChange(event.target.value)} rows={4} />
      ) : (
        <input type={type} value={value || ""} onChange={(event) => onChange(event.target.value)} />
      )}
    </label>
  );
}
