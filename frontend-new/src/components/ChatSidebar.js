import React, { useState, useEffect } from 'react';
import './ChatSidebar.css';

function ChatSidebar({ conversations, onSelectConversation, onCreateNewChat }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  
  // 当侧边栏展开状态变化时，通知父组件
  useEffect(() => {
    // 清理函数
    return () => {
      document.body.classList.remove('sidebar-expanded');
    };
  }, []);
  
  // 过滤对话
  const filteredConversations = conversations.filter(
    conv => conv.title.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  // 处理搜索输入变化
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };
  
  // 处理鼠标进入事件
  const handleMouseEnter = () => {
    setIsExpanded(true);
  };
  
  // 处理鼠标离开事件
  const handleMouseLeave = () => {
    setIsExpanded(false);
  };
  
  return (
    <div 
      className={`chat-sidebar ${isExpanded ? 'expanded' : ''}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div className="sidebar-trigger">
        <div className="trigger-icon"></div>
      </div>
      
      <div className="sidebar-content">
        <div className="sidebar-header">
          <div className="sidebar-actions">
            <button className="search-button">
              <i className="search-icon"></i>
              搜索聊天
            </button>
            <button className="new-chat-button" onClick={onCreateNewChat}>
              <i className="new-chat-icon"></i>
              创建新聊天
            </button>
          </div>
          <div className="search-container">
            <input
              type="text"
              placeholder="搜索聊天记录..."
              value={searchTerm}
              onChange={handleSearchChange}
              className="search-input"
            />
          </div>
        </div>
        
        <div className="conversations-list">
          {filteredConversations.length > 0 ? (
            filteredConversations.map(conv => (
              <div 
                key={conv.id} 
                className="conversation-item"
                onClick={() => onSelectConversation(conv.id)}
              >
                <div className="conversation-title">{conv.title}</div>
                <div className="conversation-preview">{conv.preview}</div>
                <div className="conversation-time">{new Date(conv.lastUpdated).toLocaleDateString()}</div>
              </div>
            ))
          ) : (
            <div className="no-conversations">
              {searchTerm ? '没有找到匹配的聊天记录' : '暂无聊天记录'}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ChatSidebar;
