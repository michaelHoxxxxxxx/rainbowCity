// API基础URL，根据环境配置
const API_BASE_URL = process.env.NODE_ENV === 'production' 
    ? '' // 生产环境使用相对路径
    : 'http://localhost:5000'; // 开发环境指向Flask后端

/**
 * 生成彩虹城AI_ID
 * 
 * @param {number} visibleNumber - 可选的可视编号，如果不提供，后端会自动生成
 * @returns {Promise<Object>} 生成的AI_ID对象，包含id、visible_number和created_at属性
 */
const generateAiId = async (visibleNumber = null) => {
    try {
        const payload = visibleNumber !== null 
            ? { visible_number: visibleNumber }
            : {};
            
        const response = await fetch(`${API_BASE_URL}/ai/generate_id`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to generate AI-ID');
        }

        const data = await response.json();
        return {
            id: data.id,                     // 完整的AI_ID
            visibleNumber: data.visible_number, // 可视编号部分
            createdAt: data.created_at,        // 创建时间
            // 解析AI_ID的各个部分
            parts: parseAiId(data.id)
        };
    } catch (error) {
        console.error('Error in generateAiId:', error);
        throw error;
    }
};

/**
 * 解析AI_ID字符串为各个组成部分
 * 
 * @param {string} aiId - 彩虹城AI_ID字符串，格式如：RC-AI-0001721-53dfc98b12a...
 * @returns {Object} 解析后的各个部分
 */
const parseAiId = (aiId) => {
    if (!aiId || typeof aiId !== 'string') {
        return null;
    }
    
    // 尝试匹配格式：RC-AI-0001721-53dfc98b12a...
    const parts = aiId.split('-');
    if (parts.length < 4) {
        return null;
    }
    
    return {
        prefix: `${parts[0]}-${parts[1]}`,  // RC-AI
        sequenceNumber: parts[2],            // 0001721
        uuid: parts.slice(3).join('-')       // 53dfc98b12a...
    };
};

// 模拟API响应（用于开发/测试）
const mockGenerateAiId = async (visibleNumber) => {
    // 模拟网络延迟
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // 返回模拟数据
    return {
        id: `ai-${Math.random().toString(36).substring(2, 10)}`,
        visible_number: visibleNumber,
        created_at: new Date().toISOString()
    };
};

/**
 * 生成AI频率编号
 * 
 * @param {string} aiId - AI-ID
 * @param {string} awakenerId - 唤醒者ID
 * @param {Object} aiValues - AI价值观字典，例如 {"1R": 80, "2O": 60}
 * @param {string} aiPersonality - AI性格代码，例如 "GT"
 * @param {string} aiType - AI类型代码，例如 "CP"
 * @returns {Promise<Object>} 生成的频率编号对象
 */
const generateFrequencyNumber = async (aiId, awakenerId, aiValues, aiPersonality, aiType) => {
    try {
        const payload = {
            ai_id: aiId,
            awakener_id: awakenerId,
            ai_values: aiValues,
            ai_personality: aiPersonality,
            ai_type: aiType
        };

        const response = await fetch(`${API_BASE_URL}/ai/generate_frequency`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to generate frequency number');
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error in generateFrequencyNumber:', error);
        throw error;
    }
};

/**
 * 获取频率编号详情
 * 
 * @param {string} frequencyNumber - 频率编号
 * @returns {Promise<Object>} 频率编号详情
 */
const getFrequencyDetails = async (frequencyNumber) => {
    try {
        const response = await fetch(`${API_BASE_URL}/ai/frequency/${frequencyNumber}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to retrieve frequency details');
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error in getFrequencyDetails:', error);
        throw error;
    }
};

/**
 * 获取所有存储的AI-ID
 * 
 * @returns {Promise<Object>} 包含所有AI-ID的对象
 */
const getAllAiIds = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/ai/ai_ids`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to retrieve AI-IDs');
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error in getAllAiIds:', error);
        throw error;
    }
};

export { 
    generateAiId,
    mockGenerateAiId,
    generateFrequencyNumber,
    getFrequencyDetails,
    getAllAiIds
};