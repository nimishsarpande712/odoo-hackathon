import React, { useState, useEffect, useRef, useCallback } from 'react';
import '../styles/Chat.css';

function Chat({ requestId, recipientName, onClose }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef(null);

  const fetchMessages = useCallback(async () => {
    try {
      const response = await fetch(`http://localhost:5000/chat/${requestId}`, {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages || []);
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    } finally {
      setLoading(false);
    }
  }, [requestId]);

  useEffect(() => {
    fetchMessages();
    const interval = setInterval(fetchMessages, 3000);
    return () => clearInterval(interval);
  }, [fetchMessages]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    try {
      const response = await fetch('http://localhost:5000/chat/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          request_id: requestId,
          message: newMessage.trim()
        })
      });

      if (response.ok) {
        setNewMessage('');
        fetchMessages();
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="chat-overlay" onClick={onClose}>
        <div className="chat-popup" onClick={(e) => e.stopPropagation()}>
          <div className="chat-header">
            <h3>Chat with {recipientName}</h3>
            <button className="close-btn" onClick={onClose}>×</button>
          </div>
          <div className="chat-loading">Loading chat...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-overlay" onClick={onClose}>
      <div className="chat-popup" onClick={(e) => e.stopPropagation()}>
        <div className="chat-header">
          <h3>💬 Chat with {recipientName}</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="no-messages">
              <p>Start your conversation! 👋</p>
            </div>
          ) : (
            messages.map(message => (
              <div 
                key={message.id} 
                className={`message ${message.is_from_current_user ? 'sent' : 'received'}`}
              >
                <div className="message-content">
                  {message.message}
                </div>
                <div className="message-time">
                  {formatTime(message.sent_at)}
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
        
        <form onSubmit={sendMessage} className="chat-input-form">
          <div className="chat-input-container">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Type your message..."
              className="chat-input"
              maxLength={500}
            />
            <button type="submit" className="send-btn" disabled={!newMessage.trim()}>
              📤
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Chat;
