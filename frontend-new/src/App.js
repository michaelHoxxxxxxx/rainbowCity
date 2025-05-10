import React, { useState, useRef, useEffect } from 'react';
import './App.css';
import './components/visualStyles.css';
import { generateAiId } from './services/ai_service';
import FrequencyGenerator from './components/FrequencyGenerator';
import RelationshipManager from './components/RelationshipManager';
import BackgroundAnimation from './components/BackgroundAnimation';
import SvgPatterns from './components/SvgPatterns';
import WaveAnimation from './components/WaveAnimation';
import DataVisualization from './components/DataVisualization';
import ChatButton from './components/ChatButton';

function App() {
    const [aiId, setAiId] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [currentPage, setCurrentPage] = useState('ai-id'); // 'ai-id', 'frequency' 或 'relationship'
    const aiIdRef = useRef(null);
    const [animationEnabled, setAnimationEnabled] = useState(true);
    
    // 用于控制动画效果
    useEffect(() => {
        // 检查用户偏好设置
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) {
            setAnimationEnabled(false);
        }
    }, []);

    const handleGenerateAiId = async () => {
        setLoading(true);
        setError(null);
        
        try {
            // 生成一个随机的可视编号（或者您可以让用户输入）
            const randomVisibleNumber = Math.floor(Math.random() * 9000000) + 1000000; // 生成一个7位数字
            
            // 使用真实API生成AI_ID，传递可视编号
            const newAiId = await generateAiId(randomVisibleNumber);
            setAiId(newAiId);
            console.log('Generated AI-ID:', newAiId);
        } catch (error) {
            console.error('Error generating AI-ID:', error);
            setError('Failed to generate AI-ID. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    const handleCopyAiId = () => {
        if (aiIdRef.current) {
            // 获取文本内容但排除复制图标
            const text = aiId.id;
            navigator.clipboard.writeText(text)
                .then(() => {
                    // 使用更现代的通知方式而不是alert
                    const notification = document.createElement('div');
                    notification.className = 'copy-notification';
                    notification.textContent = 'AI-ID已复制到剪贴板';
                    document.body.appendChild(notification);
                    
                    // 2秒后移除通知
                    setTimeout(() => {
                        notification.classList.add('fade-out');
                        setTimeout(() => document.body.removeChild(notification), 300);
                    }, 2000);
                })
                .catch(err => {
                    console.error('无法复制文本: ', err);
                    // 显示错误通知
                    const notification = document.createElement('div');
                    notification.className = 'copy-notification error';
                    notification.textContent = '复制AI-ID失败';
                    document.body.appendChild(notification);
                    
                    // 2秒后移除通知
                    setTimeout(() => {
                        notification.classList.add('fade-out');
                        setTimeout(() => document.body.removeChild(notification), 300);
                    }, 2000);
                });
        }
    };

    return (
        <div className="App">
            {/* SVG图案定义 */}
            <SvgPatterns />
            
            {/* AI聊天按钮 */}
            <ChatButton />
            
            {/* 背景动画 */}
            {animationEnabled && <BackgroundAnimation />}
            
            <header className="App-header">
                {/* 顶部波浪动画 */}
                {animationEnabled && <WaveAnimation position="top" height={80} />}
                
                <h1>Rainbow City</h1>
                <h2>一体七翼系统</h2>
                
                <nav className="App-nav">
                    <button 
                        className={currentPage === 'ai-id' ? 'nav-button active' : 'nav-button'}
                        onClick={() => setCurrentPage('ai-id')}
                    >
                        AI-ID 生成器
                    </button>
                    <button 
                        className={currentPage === 'frequency' ? 'nav-button active' : 'nav-button'}
                        onClick={() => setCurrentPage('frequency')}
                    >
                        频率编号生成器
                    </button>
                    <button 
                        className={currentPage === 'relationship' ? 'nav-button active' : 'nav-button'}
                        onClick={() => setCurrentPage('relationship')}
                    >
                        关系管理
                    </button>
                </nav>
            </header>
            
            <main className="App-main">
                {currentPage === 'ai-id' ? (
                    <div className="ai-id-generator">
                        <h2>AI-ID 生成器</h2>
                        <p className="description">生成一个唯一的AI身份标识符</p>
                        
                        <div className="input-group">
                            <button 
                                className="generate-button" 
                                onClick={handleGenerateAiId}
                                disabled={loading}
                            >
                                {loading ? '生成中...' : '生成 AI-ID'}
                            </button>
                        </div>
                        
                        {error && <p className="error-message">{error}</p>}
                        
                        {aiId && (
                            <div className="result-container">
                                <h3>生成的 AI-ID:</h3>
                                <div className="ai-id-display" ref={aiIdRef} onClick={handleCopyAiId}>
                                    {aiId.id}
                                    <span className="copy-icon">📋</span>
                                </div>
                                <p className="copy-hint">点击上方复制到剪贴板</p>
                                

                                
                                <div className="ai-id-details">
                                    <h4>AI-ID 详情:</h4>
                                    <p><strong>可见编号:</strong> {aiId.visibleNumber}</p>
                                    <p><strong>创建时间:</strong> {new Date(aiId.timestamp).toLocaleString()}</p>
                                </div>
                                
                                {/* 数据可视化组件 */}
                                <div className="data-visualization-container">
                                    <h4>AI-ID 生成统计</h4>
                                    <DataVisualization width={500} height={200} />
                                </div>
                            </div>
                        )}
                    </div>
                ) : currentPage === 'frequency' ? (
                    <FrequencyGenerator />
                ) : (
                    <RelationshipManager />
                )}
            </main>
            
            <footer className="App-footer">
                {/* 底部波浪动画 */}
                {animationEnabled && <WaveAnimation position="bottom" height={80} />}
                
                <p>© 2025 Rainbow City | <span className="footer-highlight">一体七翼系统</span></p>
                
                {/* 动画控制按钮 */}
                <button 
                    className="animation-toggle" 
                    onClick={() => setAnimationEnabled(!animationEnabled)}
                    title={animationEnabled ? "关闭动画效果" : "开启动画效果"}
                >
                    {animationEnabled ? "关闭动画" : "开启动画"}
                </button>
            </footer>
        </div>
    );
}

export default App;