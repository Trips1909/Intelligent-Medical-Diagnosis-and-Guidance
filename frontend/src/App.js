import React, { useState, useEffect } from "react";
import ChatBot from "./components/ChatBot";
import LoginPage from "./components/LoginPage";
import RegisterPage from "./components/RegisterPage";
import "./App.css";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("jwt_token");
    setIsLoggedIn(!!token);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("jwt_token");
    setIsLoggedIn(false);
  };

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleRegisterSuccess = () => {
    setShowRegister(false);
  };

  return (
    <div className="app">
      <h1 className="header">🩺 Mental Health Diagnostic Assistant</h1>
      {isLoggedIn ? (
        <>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
          <ChatBot />
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
