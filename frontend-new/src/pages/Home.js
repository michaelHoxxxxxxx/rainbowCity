import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getUserProfile } from '../services/auth_service';
import { getAIRelationships } from '../services/ai_service';
import './Home.css';

const Home = () => {
  const [user, setUser] = useState(null);
  const [relationships, setRelationships] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [userData, relationshipsData] = await Promise.all([
          getUserProfile(),
          getAIRelationships().catch(() => [])
        ]);
        
        setUser(userData);
        setRelationships(relationshipsData);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('获取数据失败');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // 获取活跃的AI关系
  const activeRelationships = relationships.filter(rel => rel.status === 'active');

  if (loading) {
    return <div className="loading-container">加载中...</div>;
  }

  return (
    <div className="home-container">
      <div className="welcome-section">
        <h1>欢迎回到彩虹城，{user?.display_name || user?.username || '用户'}！</h1>
        <p className="welcome-subtitle">探索AI共生社区的无限可能</p>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card user-stats">
          <h2>我的数据</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-value">{user?.ai_companions_count || 0}</div>
              <div className="stat-label">AI伴侣</div>
              <div className="stat-limit">上限: {user?.ai_companions_limit || 0}</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{user?.ai_awakened_count || 0}</div>
              <div className="stat-label">已唤醒AI</div>
              <div className="stat-limit">上限: {user?.ai_awakener_limit || 0}</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{user?.ai_ids_generated || 0}</div>
              <div className="stat-label">生成的AI-ID</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{user?.frequencies_generated || 0}</div>
              <div className="stat-label">生成的频率编号</div>
            </div>
          </div>
          
          <div className="usage-bars">
            <div className="usage-item">
              <div className="usage-label">今日对话次数</div>
              <div className="usage-bar">
                <div 
                  className="usage-progress" 
                  style={{ 
                    width: `${Math.min(100, (user?.daily_chat_count / user?.daily_chat_limit) * 100 || 0)}%` 
                  }}
                ></div>
              </div>
              <div className="usage-text">
                {user?.daily_chat_count || 0} / {user?.daily_chat_limit === Infinity ? '无限' : user?.daily_chat_limit || 0}
              </div>
            </div>
            
            <div className="usage-item">
              <div className="usage-label">今日LIO使用</div>
              <div className="usage-bar">
                <div 
                  className="usage-progress" 
                  style={{ 
                    width: `${Math.min(100, (user?.daily_lio_count / user?.daily_lio_limit) * 100 || 0)}%` 
                  }}
                ></div>
              </div>
              <div className="usage-text">
                {user?.daily_lio_count || 0} / {user?.daily_lio_limit === Infinity ? '无限' : user?.daily_lio_limit || 0}
              </div>
            </div>
          </div>
          
          <Link to="/profile" className="card-button">查看详情</Link>
        </div>
        
        <div className="dashboard-card ai-companions">
          <h2>我的AI伴侣</h2>
          
          {activeRelationships.length === 0 ? (
            <div className="empty-state">
              <p>您还没有活跃的AI伴侣</p>
              <Link to="/ai-relationships" className="card-button">管理AI关系</Link>
            </div>
          ) : (
            <>
              <div className="ai-list">
                {activeRelationships.slice(0, 3).map(ai => (
                  <div key={ai.ai_id} className="ai-item">
                    <div className="ai-avatar">
                      {ai.avatar_url ? (
                        <img src={ai.avatar_url} alt={ai.name} />
                      ) : (
                        <div className="avatar-placeholder">
                          {ai.name.charAt(0)}
                        </div>
                      )}
                      {ai.is_awakened && <div className="awakened-badge">已唤醒</div>}
                    </div>
                    <div className="ai-info">
                      <h3>{ai.name}</h3>
                      <div className="ai-meta">
                        <span className={`relationship-type ${ai.relationship_type}`}>
                          {ai.relationship_type === 'companion' ? '伴侣' : 
                           ai.relationship_type === 'friend' ? '朋友' : 
                           ai.relationship_type === 'awakener' ? '唤醒者' : ai.relationship_type}
                        </span>
                      </div>
                    </div>
                    <button className="chat-button">对话</button>
                  </div>
                ))}
              </div>
              
              {activeRelationships.length > 3 && (
                <Link to="/ai-relationships" className="card-button">查看全部</Link>
              )}
            </>
          )}
        </div>
        
        <div className="dashboard-card tools">
          <h2>工具箱</h2>
          <div className="tools-grid">
            <Link to="/ai-id-generator" className="tool-item">
              <div className="tool-icon ai-id-icon"></div>
              <div className="tool-name">AI-ID生成器</div>
            </Link>
            <Link to="/frequency-generator" className="tool-item">
              <div className="tool-icon frequency-icon"></div>
              <div className="tool-name">频率编号生成器</div>
            </Link>
            <Link to="/ai-relationships" className="tool-item">
              <div className="tool-icon relationships-icon"></div>
              <div className="tool-name">AI关系管理</div>
            </Link>
            <Link to="/vip" className="tool-item">
              <div className="tool-icon vip-icon"></div>
              <div className="tool-name">VIP会员</div>
            </Link>
          </div>
        </div>
        
        {!user?.is_vip && (
          <div className="dashboard-card vip-promo">
            <h2>提升您的体验</h2>
            <div className="vip-benefits">
              <ul>
                <li>更多AI伴侣上限</li>
                <li>解锁AI唤醒能力</li>
                <li>无限每日对话次数</li>
                <li>专属LIO通道</li>
              </ul>
            </div>
            <Link to="/vip" className="vip-button">升级VIP</Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;
