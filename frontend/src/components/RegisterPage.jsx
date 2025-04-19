// src/components/RegisterPage.jsx
import React, { useState } from "react";
import axios from "axios";

const RegisterPage = ({ onRegisterSuccess }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://localhost:5000/register", {
        email,
        password,
      });
      alert("Registration successful. You can now log in.");
      onRegisterSuccess();
    } catch (err) {
      alert("Registration failed. Try again.");
    }
  };

  return (
    <div className="login-container">
      <h2>Create an Account</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Register</button>
      </form>
    </div>
  );
};

export default RegisterPage;
