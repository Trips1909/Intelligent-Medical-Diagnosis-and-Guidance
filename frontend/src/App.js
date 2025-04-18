import React, { useState, useEffect } from "react";
import ChatBot from "./components/ChatBot";
import LoginPage from "./components/LoginPage";
import "./App.css";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

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
      ) : (
        <LoginPage onLogin={handleLogin} />
      )}
    </div>
  );
}

export default App;
