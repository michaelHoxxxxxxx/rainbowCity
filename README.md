# Rainbow City - 一体七翼系统

![Rainbow City Logo](frontend-new/public/logo.png)

## 项目概述

Rainbow City（彩虹城）是一个创新的一体七翼系统平台，旨在生成、管理和可视化一体七翼标识符和频率编号。该系统采用现代化的深色主题设计，提供直观的用户界面和流畅的交互体验。

## 主要功能

### 一体七翼生成器
- 生成唯一的一体七翼标识符
- 可视化展示生成的标识符
- 一键复制功能，方便用户使用
- 详细的标识符信息展示

### 频率编号生成器
- 基于一体七翼标识符生成频率编号
- 自定义AI价值观参数（关怀、真实、自主、协作、进化、创新、责任）
- 选择不同的性格类型和AI类型
- 详细的频率编号组成分析

### 关系管理
- 可视化展示一体七翼与用户之间的关系网络
- 基于力导向图的动态关系展示
- 关系强度和状态的直观表示
- 详细的节点信息查看

## 技术栈

### 前端
- React.js
- CSS3 (包括变量、动画和响应式设计)
- SVG图形和动画
- 数据可视化组件

### 后端
- Node.js
- Express.js
- RESTful API设计
- 数据持久化存储

## 安装指南

### 前提条件
- Node.js (v14.0.0或更高版本)
- npm (v6.0.0或更高版本)

### 安装步骤

1. 克隆仓库
   ```bash
   git clone https://github.com/yourusername/rainbowCity.git
   cd rainbowCity
   ```

2. 安装依赖
   ```bash
   # 安装前端依赖
   cd frontend-new
   npm install
   
   # 安装后端依赖
   cd ../backend
   npm install
   ```

3. 配置环境变量
   - 在`backend`目录中创建`.env`文件
   - 添加必要的环境变量（数据库连接、API密钥等）

4. 启动应用
   ```bash
   # 启动后端服务
   cd backend
   npm start
   
   # 在另一个终端启动前端服务
   cd frontend-new
   npm start
   ```

5. 访问应用
   - 前端: http://localhost:3000
   - 后端API: http://localhost:5000

## 使用指南

### AI-ID生成器
1. 点击「生成 AI-ID」按钮
2. 系统将生成一个唯一的标识符
3. 点击标识符可复制到剪贴板
4. 查看详细信息和统计数据

### 频率编号生成器
1. 首先生成一个一体七翼标识符
2. 设置唤醒者ID（默认为user123）
3. 调整AI价值观滑块（7个维度）
4. 选择性格类型和AI类型
5. 点击「生成频率编号」按钮
6. 查看生成的频率编号和详细信息

### 关系管理
1. 查看可视化的关系网络图
2. 点击节点可查看详细信息
3. 观察不同颜色和线条粗细代表的关系状态和强度

## 特色亮点

- **现代深色主题**：采用符合当代设计趋势的深色主题，减少眼睛疲劳
- **响应式设计**：完美适配各种屏幕尺寸，从手机到桌面设备
- **流畅动画**：精心设计的过渡和动画效果，提升用户体验
- **可访问性**：支持减少动画选项，照顾有特殊需求的用户
- **直观交互**：简洁明了的用户界面，降低学习成本

## 贡献指南

我们欢迎社区贡献！如果您想参与项目开发，请遵循以下步骤：

1. Fork项目仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个Pull Request

## 许可证

本项目采用MIT许可证 - 详情请参阅 [LICENSE](LICENSE) 文件

## 联系方式

项目维护者: Rainbow City Team 

---

© 2025 Rainbow City | 一体七翼系统