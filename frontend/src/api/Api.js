/* stylelint-disable */
import axios from "axios";

const BASE_URL = "http://localhost:5000";

// Get JWT token from localStorage
const getAuthHeaders = () => ({
  headers: {
    Authorization: `Bearer ${localStorage.getItem("jwt_token")}`,
  },
});

// 🔐 Login
export const loginUser = async (email, password) => {
  const response = await axios.post(`${BASE_URL}/login`, { email, password });
  return response.data;
};

// 📝 Register
export const registerUser = async (email, password) => {
  const response = await axios.post(`${BASE_URL}/register`, {
    email,
    password,
  });
  return response.data;
};

// 🧾 Submit Demographic Form
export const submitForm = async (formData) => {
  // We are not sending answers here, just the form. Chatbot will handle Q1–Q10 later.
  return formData; // You can add backend saving if needed
};

// 💬 Chat Interaction (Optional: only for old flow)
export const chatWithBot = async (payload) => {
  const response = await axios.post(`${BASE_URL}/chat`, payload, getAuthHeaders());
  return response.data;
};

// 🔍 Predict after full data collection
export const getPrediction = async (form, answers) => {
  const response = await axios.post(
    `${BASE_URL}/predict`,
    { form, answers },
    getAuthHeaders()
  );
  return response.data;
};

// 💾 Save Feedback
export const logFeedback = async (form, answers, diagnosis, confidence) => {
  const response = await axios.post(
    `${BASE_URL}/log_feedback`,
    { form, answers, diagnosis, confidence },
    getAuthHeaders()
  );
  return response.data;
};
