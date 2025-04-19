import React, { useState, useEffect } from "react";
import axios from "axios";
import "../ChatBot.css";

const ChatBot = ({ formData }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [questionIndex, setQuestionIndex] = useState(0);
  const [followupCount, setFollowupCount] = useState(0);
  const [answers, setAnswers] = useState([]);

  useEffect(() => {
    setMessages([{ sender: "bot", text: "Hello! Tell me what you're facing?" }]);
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;

    const token = localStorage.getItem("jwt_token");
    const userMsg = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await axios.post(
        "http://localhost:5000/chat",
        {
          message: input,
          question_index: questionIndex,
          followup_count: followupCount,
          answers: answers,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const {
        reply,
        next_question,
        question_index,
        followup_count,
        show_result,
      } = res.data;

      if (next_question) {
        setMessages((prev) => [...prev, { sender: "bot", text: next_question }]);
        setQuestionIndex(question_index);
        setFollowupCount(followup_count);
        setAnswers((prev) => [...prev, input]);
      }

      if (show_result && reply) {
        const predictRes = await axios.post(
          "http://localhost:5000/predict",
          {
            form: formData,
            answers: [...answers, input], // All 10 answers
          },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        const { prediction, confidence, advice } = predictRes.data;

        const summary = [
          { sender: "bot", text: `Likely Condition: ${prediction}` },
          { sender: "bot", text: `Confidence Score: ${confidence}%` },
          { sender: "bot", text: `Recommendation: ${advice}` },
        ];

        setMessages((prev) => [...prev, ...summary]);

        // Reset for new chat
        setQuestionIndex(0);
        setFollowupCount(0);
        setAnswers([]);
      }
    } catch (err) {
      console.error("Chat error:", err);
      setMessages((prev) => [...prev, { sender: "bot", text: "Something went wrong." }]);
    }

    setInput("");
  };

  return (
    <div className="chat-container">
      <div className="chat-box">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.sender}`}>{msg.text}</div>
        ))}
      </div>
      <div className="input-box">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Type your response..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default ChatBot;
