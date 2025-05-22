import React, { useState, useEffect } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { getUserProfile, logout } from '../services/auth_service';
import './MainLayout.css';

const MainLayout = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // 加载用户数据
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const userData = await getUserProfile();
        setUser(userData);
      } catch (error) {
        console.error('Error fetching user profile:', error);
        // 如果获取用户信息失败，可能是token无效，重定向到登录页
        if (error && error.message && (error.message === '未登录，请先登录' || error.message.includes('token'))) {
          handleLogout();
        } else {
          // 如果是其他错误，也重定向到登录页
          handleLogout();
        }
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

  // 处理登出
  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // 切换菜单状态
  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  // 关闭菜单
  const closeMenu = () => {
    setMenuOpen(false);
  };

  // 检查当前路由是否活跃
  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(`${path}/`);
  };

  return (
    <div className="main-layout">
      <header className="main-header">
        <div className="header-left">
          <button className="menu-toggle" onClick={toggleMenu}>
            <span className="menu-icon"></span>
          </button>
          <Link to="/" className="logo">
            彩虹城
          </Link>
        </div>
        
        <div className="header-right">
          {user && (
            <div className="user-menu">
              <div className="user-avatar" onClick={() => navigate('/profile')}>
                {user.avatar_url ? (
                  <img src={user.avatar_url} alt="用户头像" />
                ) : (
                  <div className="avatar-placeholder">
                    {user.display_name?.charAt(0) || user.username?.charAt(0) || user.email?.charAt(0) || '?'}
                  </div>
                )}
              </div>
              {user.is_vip && (
                <div className="vip-badge">
                  {user.vip_level}
                </div>
              )}
            </div>
          )}
        </div>
      </header>
      
      <div className={`sidebar ${menuOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <button className="close-menu" onClick={closeMenu}>×</button>
          {user && (
            <div className="sidebar-user-info">
              <div className="sidebar-avatar">
                {user.avatar_url ? (
                  <img src={user.avatar_url} alt="用户头像" />
                ) : (
                  <div className="avatar-placeholder">
                    {user.display_name?.charAt(0) || user.username?.charAt(0) || user.email?.charAt(0) || '?'}
                  </div>
                )}
              </div>
              <div className="user-details">
                <div className="user-name">{user.display_name || user.username || '用户'}</div>
                <div className="user-email">{user.email}</div>
                {user.is_vip && (
                  <div className="sidebar-vip-badge">
                    {user.vip_level} VIP
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
        
        <nav className="sidebar-nav">
          <Link 
            to="/" 
            className={`nav-item ${isActive('/') && !isActive('/ai-id-generator') && !isActive('/frequency-generator') ? 'active' : ''}`}
            onClick={closeMenu}
          >
            <i className="nav-icon home-icon"></i>
            首页
          </Link>
          
          <Link 
            to="/ai-id-generator" 
            className={`nav-item ${isActive('/ai-id-generator') ? 'active' : ''}`}
            onClick={closeMenu}
          >
            <i className="nav-icon ai-id-icon"></i>
            AI-ID生成器
          </Link>
          
          <Link 
            to="/frequency-generator" 
            className={`nav-item ${isActive('/frequency-generator') ? 'active' : ''}`}
            onClick={closeMenu}
          >
            <i className="nav-icon frequency-icon"></i>
            频率编号生成器
          </Link>
          
          <Link 
            to="/ai-relationships" 
            className={`nav-item ${isActive('/ai-relationships') ? 'active' : ''}`}
            onClick={closeMenu}
          >
            <i className="nav-icon relationships-icon"></i>
            AI关系管理
          </Link>
          
          <div className="nav-divider"></div>
          
          <Link 
            to="/profile" 
            className={`nav-item ${isActive('/profile') ? 'active' : ''}`}
            onClick={closeMenu}
          >
            <i className="nav-icon profile-icon"></i>
            个人资料
          </Link>
          
          <Link 
            to="/vip" 
            className={`nav-item ${isActive('/vip') ? 'active' : ''}`}
            onClick={closeMenu}
          >
            <i className="nav-icon vip-icon"></i>
            VIP会员
          </Link>
          
          <button className="nav-item logout-button" onClick={handleLogout}>
            <i className="nav-icon logout-icon"></i>
            退出登录
          </button>
        </nav>
      </div>
      
      <div className="content-overlay" onClick={closeMenu} style={{ display: menuOpen ? 'block' : 'none' }}></div>
      
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

export default MainLayout;
