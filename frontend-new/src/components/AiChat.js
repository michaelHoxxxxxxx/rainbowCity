import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './AiChat.dark.css';
import ChatSidebar from './ChatSidebar';

// 消息类型枚举
const MessageType = {
  TEXT: 'text',
  IMAGE: 'image',
  AUDIO: 'audio',
  TOOL_OUTPUT: 'tool_output',
  SYSTEM: 'system'
};

// 发送者角色枚举
const SenderRole = {
  USER: 'user',
  ASSISTANT: 'assistant',
  SYSTEM: 'system'
};

function AiChat() {
  const navigate = useNavigate();
  
  // 状态管理
  const [messages, setMessages] = useState([
    {
      id: '1',
      role: SenderRole.SYSTEM,
      content: '你是彩虹城系统的AI助手，专门解答关于彩虹城系统、频率编号和关系管理的问题。',
      type: MessageType.SYSTEM,
      timestamp: new Date().toISOString(),
      visible: false // 系统消息默认不显示
    },
    {
      id: '2',
      role: SenderRole.ASSISTANT,
      content: '你好！我是彩虹城AI，有什么我可以帮你的吗？',
      type: MessageType.TEXT,
      timestamp: new Date().toISOString(),
      visible: true,
      isTyping: true,
      displayedContent: '' // 初始为空字符串，将逐字显示
    }
  ]);
  
  // 输入状态
  const [textInput, setTextInput] = useState('');
  const [attachments, setAttachments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // 会话状态
  const [sessionId, setSessionId] = useState(generateUUID());
  const [turnId, setTurnId] = useState(generateUUID());
  
  // 聊天历史记录
  const [conversations, setConversations] = useState([
    {
      id: '1',
      title: '关于彩虹城AI的对话',
      preview: '你好！我是彩虹城AI助手...',
      lastUpdated: new Date().toISOString(),
      messages: [...messages]
    },
    {
      id: '2',
      title: '频率编号生成讨论',
      preview: '我想了解如何生成频率编号...',
      lastUpdated: new Date(Date.now() - 86400000).toISOString(),
      messages: []
    },
    {
      id: '3',
      title: 'AI关系管理问题',
      preview: '如何设置AI之间的关系？',
      lastUpdated: new Date(Date.now() - 172800000).toISOString(),
      messages: []
    }
  ]);
  
  // 工具状态
  const [availableTools, setAvailableTools] = useState([
    { id: 'frequency_generator', name: '频率生成器', description: '生成频率编号' },
    { id: 'ai_id_generator', name: 'AI-ID生成器', description: '生成AI标识符' },
    { id: 'relationship_manager', name: '关系管理器', description: '管理AI关系' }
  ]);
  const [activeTools, setActiveTools] = useState([]);
  
  // 用于自动滚动到最新消息
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const imageInputRef = useRef(null);
  const audioInputRef = useRef(null);
  const documentInputRef = useRef(null);
  
  // 上传按钮悬停状态
  const [isUploadHovered, setIsUploadHovered] = useState(false);
  
  // 生成UUID函数
  function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  // 处理文本输入变化
  const handleInputChange = (e) => {
    setTextInput(e.target.value);
  };

  // 处理文件附件上传
  const handleFileUpload = (e, fileType = 'any') => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;
    
    let filteredFiles = files;
    
    // 根据文件类型过滤
    if (fileType === 'image') {
      filteredFiles = files.filter(file => file.type.startsWith('image/'));
    } else if (fileType === 'audio') {
      filteredFiles = files.filter(file => file.type.startsWith('audio/'));
    } else if (fileType === 'document') {
      filteredFiles = files.filter(file => !file.type.startsWith('image/') && !file.type.startsWith('audio/'));
    }
    
    const newAttachments = filteredFiles.map(file => ({
      id: generateUUID(),
      file,
      type: file.type.startsWith('image/') ? MessageType.IMAGE : 
            file.type.startsWith('audio/') ? MessageType.AUDIO : MessageType.TEXT,
      name: file.name,
      size: file.size,
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : null
    }));
    
    setAttachments(prev => [...prev, ...newAttachments]);
  };
  
  // 处理不同类型的文件上传
  const handleImageUpload = (e) => handleFileUpload(e, 'image');
  const handleAudioUpload = (e) => handleFileUpload(e, 'audio');
  const handleDocumentUpload = (e) => handleFileUpload(e, 'document');
  
  // 删除附件
  const removeAttachment = (attachmentId) => {
    setAttachments(prev => prev.filter(attachment => attachment.id !== attachmentId));
  };

  // 创建新的消息对象
  const createMessage = (role, content, type = MessageType.TEXT, additionalData = {}) => ({
    id: generateUUID(),
    role,
    content,
    type,
    timestamp: new Date().toISOString(),
    visible: true,
    isTyping: role === SenderRole.ASSISTANT, // 助手消息默认启用打字机效果
    displayedContent: role === SenderRole.ASSISTANT ? '' : content, // 初始显示内容为空
    ...additionalData
  });

  // 创建新聊天
  const handleCreateNewChat = () => {
    // 创建新的会话ID
    const newSessionId = generateUUID();
    setSessionId(newSessionId);
    
    // 重置消息列表
    setMessages([
      {
        id: generateUUID(),
        role: SenderRole.SYSTEM,
        content: '你是彩虹城系统的AI助手，专门解答关于彩虹城系统、频率编号和关系管理的问题。',
        type: MessageType.SYSTEM,
        timestamp: new Date().toISOString(),
        visible: false
      },
      {
        id: generateUUID(),
        role: SenderRole.ASSISTANT,
        content: '你好！我是彩虹城AI助手。我可以帮助你了解彩虹城系统、频率编号和关系管理。有什么我可以帮你的吗？',
        type: MessageType.TEXT,
        timestamp: new Date().toISOString(),
        visible: true
      }
    ]);
    
    // 创建新的对话记录
    const newConversation = {
      id: newSessionId,
      title: '新对话 ' + new Date().toLocaleString(),
      preview: '你好！我是彩虹城AI助手...',
      lastUpdated: new Date().toISOString(),
      messages: []
    };
    
    setConversations(prev => [newConversation, ...prev]);
  };
  
  // 选择对话
  const handleSelectConversation = (conversationId) => {
    const selectedConversation = conversations.find(conv => conv.id === conversationId);
    if (selectedConversation) {
      setSessionId(conversationId);
      // 如果有保存的消息，则加载它们
      if (selectedConversation.messages && selectedConversation.messages.length > 0) {
        setMessages(selectedConversation.messages);
      }
    }
  };
  
  // 处理表单提交
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!textInput.trim() && attachments.length === 0) return;
    
    // 创建新的回合ID
    const newTurnId = generateUUID();
    setTurnId(newTurnId);
    
    // 准备用户消息
    const userMessages = [];
    
    // 处理文本消息
    if (textInput.trim()) {
      userMessages.push(createMessage(SenderRole.USER, textInput.trim()));
    }
    
    // 处理附件
    for (const attachment of attachments) {
      userMessages.push(createMessage(
        SenderRole.USER, 
        attachment.preview || attachment.name, 
        attachment.type, 
        { attachment }
      ));
    }
    
    // 添加用户消息到状态
    setMessages(prev => [...prev, ...userMessages]);
    setTextInput('');
    setAttachments([]);
    setIsLoading(true);
    setError(null);
    
    try {
      // 准备请求数据
      const visibleMessages = messages
        .filter(msg => msg.visible || msg.role === SenderRole.SYSTEM)
        .concat(userMessages)
        .map(msg => ({
          role: msg.role,
          content: msg.content,
          type: msg.type
        }));
      
      // 调用后端 API
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}` // 添加认证令牌
        },
        body: JSON.stringify({
          session_id: sessionId,
          turn_id: newTurnId,
          messages: visibleMessages
        }),
      });
      
      if (!response.ok) {
        throw new Error(`服务器错误: ${response.status}`);
      }
      
      const data = await response.json();
      
      // 处理响应
      if (data.response) {
        // 创建助手消息
        const assistantMessage = createMessage(
          SenderRole.ASSISTANT, 
          data.response.content || data.response,
          data.response.type || MessageType.TEXT,
          data.response.metadata || {}
        );
        
        // 如果有工具调用
        if (data.tool_calls && data.tool_calls.length > 0) {
          // 处理工具调用
          setActiveTools(data.tool_calls.map(tool => ({
            id: tool.id,
            name: tool.name,
            parameters: tool.parameters
          })));
          
          // 添加工具调用消息
          const toolMessage = createMessage(
            SenderRole.SYSTEM,
            `正在使用工具: ${data.tool_calls.map(t => t.name).join(', ')}`,
            MessageType.TOOL_OUTPUT,
            { tool_calls: data.tool_calls }
          );
          
          setMessages(prev => [...prev, assistantMessage, toolMessage]);
        } else {
          setMessages(prev => [...prev, assistantMessage]);
        }
      } else if (data.error) {
        throw new Error(data.error);
      } else {
        throw new Error('未知响应格式');
      }
    } catch (err) {
      console.error('Chat error:', err);
      setError(err.message || String(err));
      
      // 添加错误消息
      const errorMessage = createMessage(
        SenderRole.SYSTEM,
        `错误: ${err.message || '未知错误'}`,
        MessageType.TEXT,
        { error: true }
      );
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };
  
  // 处理工具调用
  const handleToolAction = (toolId, action) => {
    // 如果是导航到其他页面
    if (action === 'navigate') {
      const toolRoutes = {
        'frequency_generator': '/frequency-generator',
        'ai_id_generator': '/ai-id-generator',
        'relationship_manager': '/ai-relationships'
      };
      
      if (toolRoutes[toolId]) {
        navigate(toolRoutes[toolId]);
      }
    }
    
    // 清除活动工具
    setActiveTools([]);
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
  }, [messages]);
  
  // 实现打字机效果
  useEffect(() => {
    // 找到所有正在打字的消息
    const typingMessages = messages.filter(msg => msg.isTyping && msg.displayedContent !== msg.content);
    
    if (typingMessages.length === 0) return;
    
    // 对每个正在打字的消息设置定时器
    const timers = typingMessages.map(message => {
      return setTimeout(() => {
        setMessages(prevMessages => {
          return prevMessages.map(msg => {
            if (msg.id === message.id) {
              // 如果显示内容已经等于完整内容，则停止打字
              if (msg.displayedContent === msg.content) {
                return { ...msg, isTyping: false };
              }
              
              // 否则添加下一个字符
              const nextChar = msg.content.charAt(msg.displayedContent.length);
              return { 
                ...msg, 
                displayedContent: msg.displayedContent + nextChar 
              };
            }
            return msg;
          });
        });
      }, 30); // 每30毫秒添加一个字符
    });
    
    // 清除定时器
    return () => {
      timers.forEach(timer => clearTimeout(timer));
    };
  }, [messages]);

  // 渲染消息内容
  const renderMessageContent = (message) => {
    // 准备要显示的内容，如果在打字中则使用displayedContent
    const contentToShow = message.isTyping ? message.displayedContent : message.content;
    
    switch (message.type) {
      case MessageType.IMAGE:
        return (
          <div className="message-image">
            <img src={message.content} alt="图片附件" />
            {message.attachment && <div className="image-caption">{message.attachment.name}</div>}
          </div>
        );
      case MessageType.AUDIO:
        return (
          <div className="message-audio">
            <audio controls src={message.content}>
              您的浏览器不支持音频元素。
            </audio>
            {message.attachment && <div className="audio-caption">{message.attachment.name}</div>}
          </div>
        );
      case MessageType.TOOL_OUTPUT:
        return (
          <div className="message-tool">
            <div className="tool-content">{contentToShow}</div>
            {message.tool_calls && (
              <div className="tool-actions">
                {message.tool_calls.map(tool => (
                  <button 
                    key={tool.id}
                    className="tool-action-button"
                    onClick={() => handleToolAction(tool.id, 'navigate')}
                  >
                    打开 {tool.name}
                  </button>
                ))}
              </div>
            )}
          </div>
        );
      case MessageType.TEXT:
      default:
        return (
          <div className="message-content">
            {contentToShow}
            {message.isTyping && <span className="typing-cursor">|</span>}
          </div>
        );
    }
  };

  // 渲染附件预览
  const renderAttachmentPreviews = () => {
    if (attachments.length === 0) return null;
    
    return (
      <div className="attachments-preview">
        {attachments.map(attachment => (
          <div key={attachment.id} className="attachment-item">
            {attachment.type === MessageType.IMAGE && (
              <img src={attachment.preview} alt={attachment.name} className="attachment-preview" />
            )}
            {attachment.type === MessageType.AUDIO && (
              <div className="audio-attachment-preview">
                <i className="audio-icon"></i>
                <span>{attachment.name}</span>
              </div>
            )}
            <button 
              className="remove-attachment" 
              onClick={() => removeAttachment(attachment.id)}
            >
              &times;
            </button>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="ai-chat-container">
      <ChatSidebar 
        conversations={conversations}
        onSelectConversation={handleSelectConversation}
        onCreateNewChat={handleCreateNewChat}
      />
      <div className="messages-container">
        {messages
          .filter(message => message.visible)
          .map((message) => (
            <div 
              key={message.id} 
              className={`message ${message.role === SenderRole.ASSISTANT ? 'assistant' : 
                         message.role === SenderRole.USER ? 'user' : 'system'} 
                         ${message.error ? 'error' : ''}`}
            >
              <div className="message-header">
                <div className="message-role">
                  {message.role === SenderRole.USER ? '你' : 
                   message.role === SenderRole.ASSISTANT ? '彩虹城AI' : 
                   '系统'}
                </div>
                <div className="message-time">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
              </div>
              {renderMessageContent(message)}
            </div>
        ))}
        
        {isLoading && (
          <div className="message assistant">
            <div className="message-header">
              <div className="message-role">彩虹城AI</div>
            </div>
            <div className="thinking">
              <div className="thinking-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* 活动工具区域 */}
      {activeTools.length > 0 && (
        <div className="active-tools">
          <div className="tools-header">可用工具</div>
          <div className="tools-list">
            {activeTools.map(tool => (
              <div key={tool.id} className="tool-item">
                <div className="tool-name">{tool.name}</div>
                <button 
                  className="tool-open-button"
                  onClick={() => handleToolAction(tool.id, 'navigate')}
                >
                  打开
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="input-form">
        {renderAttachmentPreviews()}
        
        <div className="input-controls">
          <div 
            className="upload-container"
            onMouseEnter={() => setIsUploadHovered(true)}
            onMouseLeave={() => setIsUploadHovered(false)}
          >
            <button 
              type="button" 
              className="attachment-button"
              disabled={isLoading}
            >
              <i className="attachment-icon"></i>
            </button>
            
            {/* 悬停时显示的上传选项 */}
            <div className={`upload-options ${isUploadHovered ? 'visible' : ''}`}>
              <button 
                type="button" 
                className="upload-option-button image-upload"
                onClick={() => imageInputRef.current.click()}
                title="上传图片"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#a18cd1">
                  <path d="M21 17h-2v-4h-4v-2h4V7h2v4h4v2h-4v4z"/>
                  <path d="M16 21H5c-1.1 0-2-.9-2-2V8c0-1.1.9-2 2-2h11c1.1 0 2 .9 2 2v13h-2zm-11-2h9V8H5v11z"/>
                  <path d="M7 17l2.5-3 1.5 2 2-2.5 3 3.5H7z"/>
                  <circle cx="8.5" cy="10.5" r="1.5"/>
                </svg>
              </button>
              
              <button 
                type="button" 
                className="upload-option-button audio-upload"
                onClick={() => audioInputRef.current.click()}
                title="上传音频"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#a18cd1">
                  <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                  <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                  <path d="M15 5.5c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5.67 1.5 1.5 1.5 1.5-.67 1.5-1.5z"/>
                  <path d="M12 3c-.55 0-1 .45-1 1s.45 1 1 1 1-.45 1-1-.45-1-1-1z"/>
                  <path d="M19 11h2c0 4.97-4.03 9-9 9s-9-4.03-9-9h2c0 3.87 3.13 7 7 7s7-3.13 7-7z"/>
                </svg>
              </button>
              
              <button 
                type="button" 
                className="upload-option-button document-upload"
                onClick={() => documentInputRef.current.click()}
                title="上传文件"
              >
                <i className="document-icon"></i>
              </button>
            </div>
          </div>
          
          {/* 隐藏的文件输入 */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            style={{ display: 'none' }}
            multiple
            accept="image/*,audio/*,application/*,text/*"
          />
          
          <input
            type="file"
            ref={imageInputRef}
            onChange={handleImageUpload}
            style={{ display: 'none' }}
            multiple
            accept="image/*"
          />
          
          <input
            type="file"
            ref={audioInputRef}
            onChange={handleAudioUpload}
            style={{ display: 'none' }}
            multiple
            accept="audio/*"
          />
          
          <input
            type="file"
            ref={documentInputRef}
            onChange={handleDocumentUpload}
            style={{ display: 'none' }}
            multiple
            accept="application/*,text/*,.pdf,.doc,.docx,.txt,.xls,.xlsx,.ppt,.pptx"
          />
          
          <input
            value={textInput}
            onChange={handleInputChange}
            placeholder="输入您的问题..."
            className="chat-input"
            disabled={isLoading}
          />
          
          <button 
            type="submit" 
            disabled={isLoading || (!textInput.trim() && attachments.length === 0)} 
            className="send-button"
          >
            发送
          </button>
        </div>
      </form>
    </div>
  );
}

export default AiChat;
