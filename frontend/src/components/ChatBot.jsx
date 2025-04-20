import React, { useState, useEffect } from "react";
import axios from "axios";
import "../ChatBot.css";

const ChatBot = ({ formData }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [questionIndex, setQuestionIndex] = useState(0);
  const [followupCount, setFollowupCount] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [crfKeywords, setCrfKeywords] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem("jwt_token");

    const startChat = async () => {
      const introMsgs = [
        { sender: "bot", text: "🧠 Welcome to your personal mental health assistant!" },
        { sender: "bot", text: "Let's begin with a few quick questions to understand you better." },
      ];

      // Immediately fetch first question (without needing input)
      const res = await axios.post(
        "http://localhost:5000/chat",
        {
          message: "", // no message from user yet
          question_index: 0,
          followup_count: 0,
          answers: [],
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const { next_question, question_index, followup_count, crf_keywords } = res.data;
      if (crf_keywords) setCrfKeywords(crf_keywords);

      setMessages([...introMsgs, { sender: "bot", text: next_question }]);
      setQuestionIndex(question_index);
      setFollowupCount(followup_count);
    };

    startChat();
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;
    const token = localStorage.getItem("jwt_token");

    setMessages((prev) => [...prev, { sender: "user", text: input }]);

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
        crf_keywords,
      } = res.data;

      if (crf_keywords) setCrfKeywords(crf_keywords);

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
            answers: [...answers, input],
          },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        const { prediction, confidence, advice } = predictRes.data;

        await axios.post(
          "http://localhost:5000/log_feedback",
          {
            form: formData,
            answers: [...answers, input],
            diagnosis: prediction,
            confidence: confidence,
            symptoms: crfKeywords,
          },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        const summary = [
          { sender: "bot", text: `Likely Condition: ${prediction}` },
          { sender: "bot", text: `Confidence Score: ${confidence}%` },
          { sender: "bot", text: `Recommendation: ${advice}` },
        ];

        setMessages((prev) => [...prev, ...summary]);

        // Reset for next session
        setQuestionIndex(0);
        setFollowupCount(0);
        setAnswers([]);
        setCrfKeywords([]);
      }
    } catch (err) {
      console.error("Chat error:", err);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Something went wrong. Please try again." },
      ]);
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
