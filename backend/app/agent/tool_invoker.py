"""
工具调度器
负责注册、管理和调用各种工具函数
"""

from typing import Callable, Dict, Any, List, Optional
import json
import requests
import os
import base64
from datetime import datetime
from .image_processor import ImageData, ImageProcessor

class ToolInvoker:
    """工具调度和执行"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_definitions: List[Dict[str, Any]] = []
        
        # 注册默认工具
        self.register_tool(
            name="get_weather",
            func=get_weather,
            description="获取指定城市的天气信息",
            parameters={
                "city": {"type": "string", "description": "城市名称，如北京、上海等"},
                "date": {"type": "string", "description": "日期，如今天、明天等，默认为今天"}
            }
        )
        
        self.register_tool(
            name="generate_ai_id",
            func=generate_ai_id,
            description="生成AI-ID",
            parameters={
                "name": {"type": "string", "description": "AI的名称，可选"}
            }
        )
        
        self.register_tool(
            name="generate_frequency",
            func=generate_frequency,
            description="生成频率编号",
            parameters={
                "ai_id": {"type": "string", "description": "AI-ID"},
                "personality_type": {"type": "string", "description": "人格类型，默认为P"},
                "ai_type": {"type": "string", "description": "AI类型，默认为A"}
            }
        )
        
        self.register_tool(
            name="analyze_image",
            func=analyze_image,
            description="分析图片内容",
            parameters={
                "image_data": {"type": "string", "description": "图片的Base64编码或URL"},
                "analysis_type": {"type": "string", "description": "分析类型，可以是'general'(一般描述), 'objects'(物体检测), 'text'(文字识别)"}
            }
        )
        
    def register_tool(self, name: str, func: Callable, description: str, parameters: Dict[str, Any]):
        """注册工具函数"""
        self.tools[name] = func
        
        # 添加工具定义（OpenAI格式）
        tool_def = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                    "required": [k for k in parameters.keys() if k != "optional_param"]
                }
            }
        }
        
        self.tool_definitions.append(tool_def)
        
    def invoke_tool(self, tool_name: str, **kwargs) -> str:
        """执行工具调用"""
        if tool_name not in self.tools:
            return f"工具 {tool_name} 不存在"
            
        try:
            result = self.tools[tool_name](**kwargs)
            return str(result)
        except Exception as e:
            return f"工具调用失败: {str(e)}"
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """获取所有工具定义"""
        return self.tool_definitions


# 默认工具函数实现

def get_weather(city: str, date: str = None) -> str:
    """获取天气信息的工具"""
    try:
        # 从环境变量获取API密钥
        api_key = os.getenv("WEATHER_API_KEY")
        
        # 检查API密钥是否存在
        if not api_key:
            return "WeatherAPI密钥未配置，请在.env文件中设置WEATHER_API_KEY"
        
        # 处理城市名称，确保它是有效的
        if not city:
            return "请提供城市名称"
        
        # 中国城市名称映射，将中文城市名映射为英文名称
        city_mapping = {
            # 直辖市
            "北京": "Beijing",
            "北京市": "Beijing",
            "上海": "Shanghai",
            "上海市": "Shanghai",
            "天津": "Tianjin",
            "天津市": "Tianjin",
            "重庆": "Chongqing",
            "重庆市": "Chongqing",
            
            # 主要城市
            "广州": "Guangzhou",
            "广州市": "Guangzhou",
            "深圳": "Shenzhen",
            "深圳市": "Shenzhen",
            "成都": "Chengdu",
            "成都市": "Chengdu",
            "杭州": "Hangzhou",
            "杭州市": "Hangzhou",
            "南京": "Nanjing",
            "南京市": "Nanjing",
            "武汉": "Wuhan",
            "武汉市": "Wuhan",
            "西安": "Xian",
            "西安市": "Xian",
            "郑州": "Zhengzhou",
            "郑州市": "Zhengzhou",
            "济南": "Jinan",
            "济南市": "Jinan",
            "青岛": "Qingdao",
            "青岛市": "Qingdao",
            "大连": "Dalian",
            "大连市": "Dalian",
            "沈阳": "Shenyang",
            "沈阳市": "Shenyang",
            "哈尔滨": "Harbin",
            "哈尔滨市": "Harbin",
            
            # 区县级城市
            "章丘": "Jinan",  # 章丘属于济南市
            "历城": "Jinan",  # 历城区属于济南市
            "历下": "Jinan",  # 历下区属于济南市
            "崂山": "Qingdao",  # 崂山区属于青岛市
            "黄埔": "Wuhan",  # 黄埔区属于武汉市
            "海淀": "Beijing",  # 海淀区属于北京市
            "浦东": "Shanghai"  # 浦东区属于上海市
        }
        
        # 检查是否需要映射
        if city in city_mapping:
            original_city = city
            city = city_mapping[city]
            print(f"[INFO] 将城市名称 '{original_city}' 映射为 '{city}'")
        
        print(f"\n[DEBUG] 尝试获取{city}的天气信息")
        
        # 构建API URL
        if date and date.lower() in ["tomorrow", "明天"]:
            # 如果是查询明天的天气，使用forecast API
            url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=2&lang=zh"
        else:
            # 默认查询当前天气
            url = f"https://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&lang=zh"
        
        print(f"[DEBUG] 请求URL: {url}")
        
        # 发送API请求
        response = requests.get(url, timeout=10)  # 添加超时时间
        
        print(f"[DEBUG] 响应状态码: {response.status_code}")
        
        # 检查状态码
        if response.status_code != 200:
            error_msg = f"请求失败，状态码: {response.status_code}"
            try:
                error_data = response.json()
                if 'error' in error_data and 'message' in error_data['error']:
                    error_msg += f", 错误信息: {error_data['error']['message']}"
            except:
                error_msg += ", 无法解析错误响应"
            
            print(f"[ERROR] {error_msg}")
            return f"无法获取{city}的天气信息: {error_msg}"
        
        # 解析JSON响应
        try:
            data = response.json()
        except Exception as e:
            print(f"[ERROR] JSON解析错误: {str(e)}")
            return f"无法解析天气数据: {str(e)}"
        
        # 检查数据结构
        if 'location' not in data:
            print(f"[ERROR] 响应中缺少location字段: {data}")
            return f"获取到的数据格式不正确，缺少必要字段"
        
        # 解析响应数据
        try:
            if date and date.lower() in ["tomorrow", "明天"]:
                # 获取明天的天气预报
                forecast = data["forecast"]["forecastday"][1]["day"]
                location = data["location"]
                weather_text = forecast["condition"]["text"]
                max_temp = forecast["maxtemp_c"]
                min_temp = forecast["mintemp_c"]
                rain_chance = forecast["daily_chance_of_rain"]
                
                result = f"明天{location['name']}天气: {weather_text}, 气温{min_temp}°C至{max_temp}°C, 降雨概率{rain_chance}%"
            else:
                # 获取当前天气
                current = data["current"]
                location = data["location"]
                weather_text = current["condition"]["text"]
                temp = current["temp_c"]
                feels_like = current["feelslike_c"]
                humidity = current["humidity"]
                
                result = f"{location['name']}当前天气: {weather_text}, 气温{temp}°C, 体感温度{feels_like}°C, 湿度{humidity}%"
            
            print(f"[DEBUG] 成功获取天气信息: {result}")
            return result
        except Exception as e:
            print(f"[ERROR] 数据解析错误: {str(e)}\n数据: {data}")
            return f"解析{city}的天气数据时出错: {str(e)}"
    except requests.exceptions.Timeout:
        return f"请求{city}天气信息超时，请稍后再试"
    except requests.exceptions.ConnectionError:
        return f"连接天气API服务器失败，请检查网络连接"
    except Exception as e:
        print(f"[ERROR] 未预期的错误: {str(e)}")
        return f"获取天气信息失败: {str(e)}"

def generate_ai_id(name: str = None) -> str:
    """生成AI-ID的工具"""
    try:
        # 生成唯一的AI-ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = f"AI-{timestamp}"
        
        if name:
            return f"为 {name} 生成的AI-ID: {unique_id}"
        else:
            return f"生成的AI-ID: {unique_id}"
    except Exception as e:
        return f"生成AI-ID失败: {str(e)}"

def generate_frequency(ai_id: str, personality_type: str = "P", ai_type: str = "A") -> str:
    """生成频率编号的工具"""
    try:
        # 生成频率编号
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        frequency = f"F-{personality_type}{ai_type}-{timestamp}"
        
        return f"为AI-ID {ai_id} 生成的频率编号: {frequency}"
    except Exception as e:
        return f"生成频率编号失败: {str(e)}"

def analyze_image(image_data: str, analysis_type: str = "general") -> str:
    """图片分析工具
    
    Args:
        image_data: 图片的Base64编码或URL
        analysis_type: 分析类型，可以是'general'(一般描述), 'objects'(物体检测), 'text'(文字识别)
    
    Returns:
        图片分析结果的描述
    """
    try:
        # 创建ImageProcessor实例
        processor = ImageProcessor()
        
        # 判断输入类型
        if image_data.startswith(('http://', 'https://', 'data:image')):
            # 处理URL或数据地址
            image = ImageData(url=image_data)
        else:
            # 尝试处理为Base64编码
            try:
                content = base64.b64decode(image_data)
                image = ImageData(content=content)
            except Exception as e:
                return f"无法解析图片数据: {str(e)}"
        
        # 使用OpenAI或其他服务分析图片
        # 这里我们模拟分析结果，实际实现中应调用相应的API
        if analysis_type == "general":
            return "这是一张图片的一般描述。在实际实现中，这里应调用图像分析API来获取图片的详细内容描述。"
        elif analysis_type == "objects":
            return "已检测到图片中的物体。在实际实现中，这里应调用物体检测 API 来识别图片中的物体。"
        elif analysis_type == "text":
            return "已提取图片中的文字。在实际实现中，这里应调用OCR API 来提取图片中的文字。"
        else:
            return f"不支持的分析类型: {analysis_type}"
    except Exception as e:
        return f"分析图片时出错: {str(e)}"
