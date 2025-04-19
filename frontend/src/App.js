import React, { useState, useEffect } from "react";
import ChatBot from "./components/ChatBot";
import FormPage from "./components/FormPage";
import LoginPage from "./components/LoginPage";
import RegisterPage from "./components/RegisterPage";
import "./App.css";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [formData, setFormData] = useState(null); // ✅ Store form input

  useEffect(() => {
    const token = localStorage.getItem("jwt_token");
    setIsLoggedIn(!!token);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("jwt_token");
    setIsLoggedIn(false);
    setFormData(null);
  };

  const handleLogin = () => setIsLoggedIn(true);

  const handleRegisterSuccess = () => setShowRegister(false);

  return (
    <div className="app">
      <h1 className="header">🩺 Mental Health Diagnostic Assistant</h1>
      {isLoggedIn ? (
        <>
          <button onClick={handleLogout} className="logout-btn">Logout</button>
          {formData ? (
            <ChatBot formData={formData} />
          ) : (
            <FormPage onSubmit={setFormData} />
          )}
        </>
      ) : showRegister ? (
        <RegisterPage onRegisterSuccess={handleRegisterSuccess} />
      ) : (
        <>
          <LoginPage onLogin={handleLogin} />
          <button onClick={() => setShowRegister(true)}>Register</button>
        </>
      )}
    </div>
  );
}

export default App;
