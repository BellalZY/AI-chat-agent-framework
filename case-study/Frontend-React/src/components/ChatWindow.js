import React, { useState, useEffect, useRef, useMemo } from "react";
import { getAIMessage } from "../api/api";
import { marked } from "marked";
import "./ChatWindow.css";

// Memoized Message component
const Message = React.memo(({ role, content, isLoading }) => {
  return (
    <div className={`message-wrapper ${role}`}>
      <div className="message-bubble">
        {isLoading ? (
          <div className="loading-bar">Typing...</div>
        ) : (
          <div
            dangerouslySetInnerHTML={{
              __html: marked(content).replace(/<p>|<\/p>/g, ""),
            }}
          />
        )}
      </div>
    </div>
  );
});

function ChatWindow() {
  const defaultMessage = [
    {
      role: "assistant",
      content: `Hello! How can I help you today?
      <p style="margin: 4px 0 4px 0;">Guess you want to ask:</p>
      <div>
        <a href="question:How can I install part number PS11752927?">💡How can I install part number PS11752927?</a>
        <a href="question:Is part PS758446 compatible with my PFS22SISBSS model?">❓Is part PS758446 compatible with my PFS22SISBSS model?</a>
        <a href="question:The ice maker on my Whirlpool fridge is not working. How can I fix it?">🧊The ice maker on my Whirlpool fridge is not working. How can I fix it?</a>
        <a href="question:Recommend good but cheap dishwasher parts for me!">💰Recommend good but cheap dishwasher parts for me!</a>
      </div>`,
    },
  ];

  const handleClick = (e) => {
    if (
      e.target.tagName === "A" &&
      e.target.getAttribute("href")?.startsWith("question:")
    ) {
      e.preventDefault();
      const question = decodeURIComponent(
        e.target.getAttribute("href").replace("question:", "")
      );
      handleSend(question);
    }
  };

  const [messages, setMessages] = useState(defaultMessage);
  const [input, setInput] = useState("");
  const [showHistory, setShowHistory] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    document.addEventListener("click", handleClick);
    return () => document.removeEventListener("click", handleClick);
  }, []);

  useEffect(() => {
    setShowHistory(false);
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSend = async (input) => {
    if (input.trim() !== "") {
      const userMessage = { role: "user", content: input };
      setMessages((prev) => [...prev, userMessage]);
      setInput("");

      const loadingMessage = { role: "assistant", content: "", isLoading: true };
      setMessages((prev) => [...prev, loadingMessage]);

      const aiMessage = await getAIMessage(input);

      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = aiMessage;
        return updated;
      });
    }
  };

  const recentMessages = useMemo(() => messages.slice(-4), [messages]);
  const historyMessages = useMemo(() => messages.slice(0, -4), [messages]);

  return (
    <div className="chat-container">
      <div className="chat-messages">

        {historyMessages.length > 0 && (
          <button
            className="toggle-history-button"
            onClick={() => setShowHistory((prev) => !prev)}
          >
            {showHistory ? "Hide History Messages" : "Show History Messages"}
          </button>
        )}

        {showHistory &&
          historyMessages.map((message, index) => (
            <Message
              key={`history-${index}`}
              role={message.role}
              content={message.content}
              isLoading={message.isLoading}
            />
          ))}

        {recentMessages.map((message, index) => (
          <Message
            key={`recent-${index}`}
            role={message.role}
            content={message.content}
            isLoading={message.isLoading}
          />
        ))}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              handleSend(input);
              e.preventDefault();
            }
          }}
          rows="2"
        />
        <button className="chat-send-button" onClick={() => handleSend(input)}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;
