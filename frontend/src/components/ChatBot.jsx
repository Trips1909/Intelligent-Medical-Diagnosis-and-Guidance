import React, { useState, useEffect } from "react";
import axios from "axios";
import "../ChatBot.css";

const ChatBot = ({ formData }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [questionIndex, setQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [crfKeywords, setCrfKeywords] = useState([]);
  const [showFollowups, setShowFollowups] = useState(false);
  const [gptResponses, setGptResponses] = useState([]);
  const [baseConfidence, setBaseConfidence] = useState(null);
  const [diagnosis, setDiagnosis] = useState("");
  const [advice, setAdvice] = useState("");
  const [resourceLinks, setResourceLinks] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem("jwt_token");

    const startChat = async () => {
      const res = await axios.post(
        "http://localhost:5000/chat",
        {
          message: "",
          question_index: 0,
          followup_count: 0,
          answers: [],
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      const { next_question, question_index, crf_keywords } = res.data;

      setMessages([
        { sender: "bot", text: "🧠 Welcome to your personal mental health assistant!" },
        { sender: "bot", text: "Let's begin with a few quick questions to understand you better." },
        { sender: "bot", text: next_question }
      ]);

      setQuestionIndex(question_index);
      if (crf_keywords) setCrfKeywords(crf_keywords);
    };

    startChat();
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;
    const token = localStorage.getItem("jwt_token");

    setMessages(prev => [...prev, { sender: "user", text: input }]);
    setInput("");

    if (showFollowups) {
      try {
        const res = await axios.post(
          "http://localhost:5000/gpt_followup",
          {
            gpt_response: input,
            gpt_responses: gptResponses,
            base_confidence: baseConfidence,
            diagnosis,
            symptoms: crfKeywords,
          },
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        if (res.data.final) {
          const finalMessages = [
            { sender: "bot", text: `✅ Final Diagnosis: ${diagnosis}` },
            { sender: "bot", text: `✅ Adjusted Confidence Score: ${res.data.updated_confidence}%` },
            { sender: "bot", text: `📌 Recommendation: ${advice}` }
          ];

          if (res.data.resources && res.data.resources.length > 0) {
            finalMessages.push({ sender: "bot", text: `📚 Helpful Resources:` });
            res.data.resources.forEach((link, idx) => {
              finalMessages.push({ sender: "bot", text: `🔗 [${idx + 1}] ${link}` });
            });
          }
          

          setMessages(prev => [...prev, ...finalMessages]);
          resetState();
        } else {
          setGptResponses(res.data.gpt_responses);
          setMessages(prev => [...prev, { sender: "bot", text: res.data.next_gpt_question }]);
        }
      } catch (err) {
        setMessages(prev => [...prev, { sender: "bot", text: "⚠️ GPT follow-up failed." }]);
      }
      return;
    }

    try {
      const res = await axios.post(
        "http://localhost:5000/chat",
        {
          message: input,
          question_index: questionIndex,
          answers: answers,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      const {
        next_question,
        question_index,
        show_result,
        crf_keywords,
      } = res.data;

      setAnswers(prev => [...prev, input]);
      if (crf_keywords) setCrfKeywords(crf_keywords);

      if (next_question) {
        setMessages(prev => [...prev, { sender: "bot", text: next_question }]);
        setQuestionIndex(question_index);
      }

      if (show_result) {
        const predictRes = await axios.post(
          "http://localhost:5000/predict",
          {
            form: formData,
            answers: [...answers, input],
          },
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        const { prediction, confidence, advice } = predictRes.data;
        setDiagnosis(prediction);
        setBaseConfidence(confidence);
        setAdvice(advice);

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
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        const gptInit = await axios.post(
          "http://localhost:5000/gpt_followup",
          {
            gpt_response: "",
            gpt_responses: [],
            base_confidence: confidence,
            diagnosis: prediction,
            symptoms: crfKeywords,
          },
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        setShowFollowups(true);
        setMessages(prev => [
          ...prev,
          { sender: "bot", text: `💡 Initial Diagnosis: ${prediction}` },
          { sender: "bot", text: `🧪 Starting GPT-based follow-ups to fine-tune confidence...` },
          { sender: "bot", text: gptInit.data.next_gpt_question },
        ]);
      }

    } catch (err) {
      console.error("Chat error:", err);
      setMessages(prev => [...prev, { sender: "bot", text: "Something went wrong. Please try again." }]);
    }
  };

  const resetState = () => {
    setQuestionIndex(0);
    setAnswers([]);
    setCrfKeywords([]);
    setShowFollowups(false);
    setGptResponses([]);
    setBaseConfidence(null);
    setDiagnosis("");
    setAdvice("");
    setResourceLinks([]);
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
