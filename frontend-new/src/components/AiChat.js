import React, { useRef, useEffect, useState } from 'react';
import './AiChat.dark.css';

function AiChat() {
  // 状态管理
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '你好！我是彩虹城一体七翼系统的AI助手。我可以帮助你了解一体七翼系统、频率编号和关系管理。有什么我可以帮你的吗？'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [debug, setDebug] = useState({});
  
  // 用于自动滚动到最新消息
  const messagesEndRef = useRef(null);

  // 处理输入变化
  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  // 处理表单提交
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    // 添加用户消息
    const userMessage = { role: 'user', content: input.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);
    
    try {
      // 使用简单的fetch请求
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ messages: [...messages, userMessage] }),
      });
      
      // 记录响应状态
      setDebug(prev => ({ 
        ...prev, 
        responseStatus: response.status, 
        responseOk: response.ok,
        responseHeaders: Object.fromEntries([...response.headers.entries()]),
      }));
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setDebug(prev => ({ ...prev, responseData: data }));
      
      // 检查响应格式并提取内容
      if (data.choices && data.choices.length > 0 && data.choices[0].message) {
        // 添加助手消息
        const assistantMessage = {
          role: 'assistant',
          content: data.choices[0].message.content
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else if (data.error) {
        throw new Error(data.error);
      } else {
        throw new Error('未知响应格式');
      }
      
    } catch (err) {
      console.error('Chat error:', err);
      setError(err.message || String(err));
      setDebug(prev => ({ ...prev, error: err.message || String(err) }));
    } finally {
      setIsLoading(false);
    }
  };

  // 自动滚动到最新消息
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);
  
  // 记录消息变化
  useEffect(() => {
    console.log('Messages updated:', messages);
    setDebug(prev => ({ ...prev, messageCount: messages.length }));
  }, [messages]);

  return (
    <div className="ai-chat-container">
      <div className="messages-container">
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`message ${message.role === 'assistant' ? 'assistant' : 'user'}`}
          >
            <div className="message-role">
              {message.role === 'user' ? '你' : '一体七翼助手'}
            </div>
            <div className="message-content">{message.content}</div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message assistant">
            <div className="message-role">一体七翼助手</div>
            <div className="thinking">
              <div className="thinking-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        {/* 显示错误信息（如果有） */}
        {error && (
          <div className="message error">
            <div className="message-role">错误</div>
            <div className="message-content">{error.toString()}</div>
          </div>
        )}
        
        {/* 调试信息区域已移除 */}
        
        <div ref={messagesEndRef} />
      </div>
      
      <form onSubmit={handleSubmit} className="input-form">
        <input
          value={input}
          onChange={handleInputChange}
          placeholder="输入您的问题..."
          className="chat-input"
          disabled={isLoading}
        />
        <button 
          type="submit" 
          disabled={isLoading || !input.trim()} 
          className="send-button"
        >
          发送
        </button>
      </form>
    </div>
  );
}

export default AiChat;
