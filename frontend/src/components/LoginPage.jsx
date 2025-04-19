import React, { useState } from "react";
import axios from "axios";
import "./LoginPage.css";

const LoginPage = ({ onLogin, onSwitchToRegister }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post("http://localhost:5000/login", {
        email,
        password,
      });
      const token = res.data.access_token;
      localStorage.setItem("jwt_token", token);
      onLogin();
    } catch (err) {
      alert("Login failed. Please try again.");
    }
  };

  return (
    <div className="login-container">
      <h2>Login to Continue</h2>
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
        <button type="submit">Login</button>
      </form>
      <p style={{ marginTop: "10px" }}>
        Don't have an account?{" "}
        <span className="link" onClick={onSwitchToRegister}>
          Register here
        </span>
      </p>
    </div>
  );
};

export default LoginPage;
