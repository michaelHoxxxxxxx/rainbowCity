import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { logout, getCurrentUser } from '../../services/auth_service';
import './UserAvatar.css';

const UserAvatar = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [user, setUser] = useState(null);
  const menuRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    // 获取当前用户信息
    const currentUser = getCurrentUser();
    setUser(currentUser);

    // 点击外部关闭菜单
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  const handleLogout = () => {
    logout();
    navigate('/');
    window.location.reload(); // 刷新页面以更新登录状态
  };

  // 如果没有用户信息，返回null
  if (!user) return null;

  // 获取用户头像或使用默认头像
  const userInitial = user.name ? user.name.charAt(0).toUpperCase() : 'U';
  const avatarUrl = user.avatar_url;

  return (
    <div className="user-avatar-container" ref={menuRef}>
      <div className="avatar-wrapper" onClick={toggleMenu}>
        {avatarUrl ? (
          <img src={avatarUrl} alt="User Avatar" className="user-avatar" />
        ) : (
          <div className="user-avatar-placeholder">
            {userInitial}
          </div>
        )}
      </div>
      
      {menuOpen && (
        <div className="user-menu">
          <ul className="menu-items">
            <li className="user-email-item">
              <div className="user-email">{user.email}</div>
            </li>
            <div className="menu-divider"></div>
            <li>
              <Link to="/dashboard" className="menu-item">
                <span className="menu-icon-box">○</span>
                开始套餐
              </Link>
            </li>
            <li>
              <Link to="/dashboard/ai-relationships" className="menu-item">
                <span className="menu-icon-box">⭕</span>
                自定义彩虹城 AI
              </Link>
            </li>
            <li>
              <Link to="/dashboard/profile" className="menu-item">
                <span className="menu-icon-box">⚙</span>
                设置
              </Link>
            </li>
            <li>
              <Link to="/dashboard/vip" className="menu-item">
                <span className="menu-icon-box">⌨</span>
                键盘快捷方式
              </Link>
            </li>
            <li>
              <button className="menu-item text-button">
                <span className="menu-icon-box">❓</span>
                帮助与常见问题解答
              </button>
            </li>
            <li>
              <button className="menu-item text-button">
                <span className="menu-icon-box">ℹ</span>
                发行说明
              </button>
            </li>
            <li>
              <button className="menu-item text-button">
                <span className="menu-icon-box">⚖</span>
                条款与政策
              </button>
            </li>
            <li>
              <button className="menu-item text-button">
                <span className="menu-icon-box">🔍</span>
                获取彩虹城 AI 搜索扩展程序
              </button>
            </li>
            
            <div className="menu-divider"></div>
            
            <li>
              <button onClick={handleLogout} className="menu-item text-button">
                <span className="menu-icon-box">→</span>
                注销
              </button>
            </li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default UserAvatar;
