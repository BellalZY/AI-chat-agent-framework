import React from "react";
import "./App.css";
import ChatWindow from "./components/ChatWindow";

function App() {
  return (
    <div className="App">
      <header className="heading">
      <div className="logo-container">
          <div className="logo-icon">P</div>
          <div className="logo-info">
            <div className="logo-brand">PartSelect</div>
            <div className="logo-since">Here to help since 1999</div>
          </div>
          <div className="logo-anniversary">
            <span className="logo-25">25</span>
            <span className="logo-years">YEARS</span>
          </div>
        </div>
      </header>
      <main className="chat-wrapper">
        <ChatWindow />
      </main>
      <div className="chat-footer">
        Need help finding parts?&nbsp;
        <a href="https://www.partselect.com/" target="_blank" rel="noopener noreferrer">
          Visit PartSelect.com →
        </a>
      </div>
    </div>
  );
}

export default App;

