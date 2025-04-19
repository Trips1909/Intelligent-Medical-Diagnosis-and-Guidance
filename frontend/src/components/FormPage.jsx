import React, { useState } from "react";
import "./FormPage.css"; // Optional for styling

const FormPage = ({ onSubmit }) => {
  const [form, setForm] = useState({
    Gender: "",
    Country: "",
    Occupation: "",
    self_employed: "",
    family_history: "",
    treatment: "",
    Growing_Stress: "",
    Changes_Habits: "",
    Mental_Health_History: "",
    Mood_Swings: "",
    Coping_Struggles: "",
    Work_Interest: "",
    Social_Weakness: "",
    mental_health_interview: "",
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(form);
  };

  return (
    <form onSubmit={handleSubmit} className="form-container">
      <h2>🧾 Demographic Information</h2>

      <label>Gender:</label>
      <select name="Gender" value={form.Gender} onChange={handleChange} required>
        <option value="">Select</option>
        <option>Male</option>
        <option>Female</option>
        <option>Other</option>
      </select>

      <label>Country:</label>
      <input type="text" name="Country" value={form.Country} onChange={handleChange} required />

      <label>Occupation:</label>
      <select name="Occupation" value={form.Occupation} onChange={handleChange} required>
        <option value="">Select</option>
        <option>Corporate</option>
        <option>Student</option>
        <option>Healthcare</option>
        <option>Freelancer</option>
        <option>Other</option>
      </select>

      <label>Self Employed:</label>
      <select name="self_employed" value={form.self_employed} onChange={handleChange} required>
        <option value="">Select</option>
        <option>Yes</option>
        <option>No</option>
      </select>

      <label>Family History of Mental Illness:</label>
      <select name="family_history" value={form.family_history} onChange={handleChange} required>
        <option value="">Select</option>
        <option>Yes</option>
        <option>No</option>
      </select>

      <label>Previous Treatment:</label>
      <select name="treatment" value={form.treatment} onChange={handleChange} required>
        <option value="">Select</option>
        <option>Yes</option>
        <option>No</option>
      </select>

      <label>Growing Stress:</label>
      <select name="Growing_Stress" value={form.Growing_Stress} onChange={handleChange} required>
        <option value="">Select</option>
        <option>Yes</option>
        <option>No</option>
      </select>

      <label>Changes in Habits:</label>
      <select name="Changes_Habits" value={form.Changes_Habits} onChange={handleChange} required>
        <option value="">Select</option>
        <option>Yes</option>
        <option>No</option>
      </select>

      <label>Mental Health History:</label>
      <select name="Mental_Health_History" value={form.Mental_Health_History} onChange={handleChange} required>
        <option value="">Select</option>
        <option>Yes</option>
        <option>No</option>
      </select>

      <label>Mood Swings:</label>
      <select name="Mood_Swings" value={form.Mood_Swings} onChange={handleChange} required>
        <option value="">Select</option>
        <option>Low</option>
        <option>Medium</option>
        <option>High</option>
      </select>

      <label>Coping Struggles:</label>
      <select name="Coping_Struggles" value={form.Coping_Struggles} onChange={handleChange} required>
        <option value="">Select</option>
        <option>Yes</option>
        <option>No</option>
      </select>

      <label>Work Interest:</label>
      <select name="Work_Interest" value={form.Work_Interest} onChange={handleChange} required>
        <option value="">Select</option>
        <option>Yes</option>
        <option>No</option>
      </select>

      <label>Social Weakness:</label>
      <select name="Social_Weakness" value={form.Social_Weakness} onChange={handleChange} required>
        <option value="">Select</option>
        <option>Yes</option>
        <option>No</option>
      </select>

      <label>Willingness to Discuss in Interview:</label>
      <select name="mental_health_interview" value={form.mental_health_interview} onChange={handleChange} required>
        <option value="">Select</option>
        <option>Yes</option>
        <option>No</option>
        <option>Maybe</option>
      </select>

      <br />
      <button type="submit">Continue to Chat</button>
    </form>
  );
};

export default FormPage;
