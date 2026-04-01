import streamlit as st
import sqlite3
import pandas as pd

st.title("🚗 车企数据出境合规自查工具")

# 用户输入
country = st.selectbox("出口目的地", ["中国", "欧盟", "墨西哥"])
data_category = st.selectbox("数据类型", ["人脸信息", "位置数据", "驾驶行为", "设计物料清单", "标注场景数据", "车辆识别码"])
scenario = st.selectbox("业务场景", ["研发设计-产品研发", "研发设计-产品测试", "生产制造", "驾驶自动化", "软件升级", "联网运行-车辆数据"])

# 触发条件选项
trigger_options = [
    "涉及军事管理区、国防科工单位、县级以上党政机关",
    "涉及涉密、敏感地理信息数据",
    "反映地级及以上行政区经济运行情况，累计≥30天",
    "车外人脸≥32像素",
    "车牌≥16像素",
    "涉及境内运行10万台以上车辆收集",
    "累计2000小时以上原始影像",
    "1000万张以上原始图片",
    "国家重大专项、国家重点研发计划支持",
    "涉及《中国禁止出口限制出口技术目录》"
]

selected_triggers = st.multiselect("请勾选您企业涉及的情况（可多选）", trigger_options)

# 分析按钮
if st.button("开始分析"):
    if not selected_triggers:
        st.warning("请至少勾选一项您企业涉及的情况")
    else:
        try:
            # 连接 SQLite 数据库
            conn = sqlite3.connect('rules.db')
            
            # 查询：按国家 + 场景 + 数据类型匹配
            query = """
                SELECT * FROM rules 
                WHERE country = ? AND scenario = ? AND data_category = ?
            """
            df = pd.read_sql_query(query, conn, params=(country, scenario, data_category))
            conn.close()
            
            # 匹配用户勾选的触发条件
            matched = []
            seen_categories = set()
            for _, row in df.iterrows():
                trigger = row['trigger_condition']
                data_cat = row['data_category']
                if trigger in selected_triggers and data_cat not in seen_categories:
                    matched.append(row)
                    seen_categories.add(data_cat)
            
            # 显示结果
            if len(matched) == 0:
                st.success("✅ 未发现明显合规风险")
            else:
                st.subheader("📊 风险分析报告")
                for row in matched:
                    law_name = row['law_name']
                    data_cat = row['data_category']
                    trigger = row['trigger_condition']
                    risk = row['risk_level']
                    advice = row['advice']
                    
                    if risk == '高':
                        st.error(f"【高风险】{data_cat}")
                        st.write(f"法规依据：{law_name}")
                        st.write(f"触发条件：{trigger}")
                        st.write(f"合规建议：{advice}")
                        st.write("---")
                    else:
                        st.warning(f"【中风险】{data_cat}")
                        st.write(f"法规依据：{law_name}")
                        st.write(f"触发条件：{trigger}")
                        st.write(f"合规建议：{advice}")
                        st.write("---")
                        
        except Exception as e:
            st.error(f"数据读取失败：{e}")
            st.write("请确保 rules.db 文件在正确位置")
