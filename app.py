import streamlit as st
import pymysql
import pandas as pd

st.title("🚗 车企数据出境合规自查工具")

country = st.selectbox("出口目的地", ["中国", "欧盟", "墨西哥"])
data_category = st.selectbox("数据类型", ["人脸信息", "位置数据", "驾驶行为", "设计物料清单", "标注场景数据", "车辆识别码"])
scenario = st.selectbox("业务场景", ["研发设计-产品研发", "研发设计-产品测试", "生产制造", "驾驶自动化", "软件升级", "联网运行-车辆数据"])

# 多选触发条件（来自你的 Excel 里的 trigger_condition）
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

if st.button("开始分析"):
    if not selected_triggers:
        st.warning("请至少勾选一项您企业涉及的情况")
    else:
        try:
            conn = pymysql.connect(
                host='localhost',
                user='root',
                password='kezhiTSJBY202264!',
                database='compliance_db',
                charset='utf8mb4'
            )
            cursor = conn.cursor()
            
            # 查询匹配的规则
            query = "SELECT * FROM rules WHERE country = %s AND scenario = %s"
            cursor.execute(query, (country, scenario))
            results = cursor.fetchall()
            conn.close()
            
            # 匹配用户勾选的条件
            matched =[]
            seen = set()  # 用来记录已经显示过的数据类别
            for row in results:
                trigger = row[5]
                data_cat = row[2]  # data_category
                if trigger in selected_triggers and data_cat not in seen:
                    matched.append(row)
                    seen.add(data_cat)
           
            if len(matched) == 0:
                st.success("✅ 未发现明显合规风险")
            else:
                st.subheader("📊 风险分析报告")
                
                for row in matched:
                    law_name = row[1]
                    data_category_val = row[2]
                    trigger = row[5]
                    risk = row[6]  # risk_level
                    advice = row[7]
                    
                    if risk == '高':
                        st.error(f"【高风险】{law_name} - {data_category_val}")
                        st.write(f"触发条件：{trigger}")
                        st.write(f"建议：{advice}")
                        st.write("---")
                    else:
                        st.warning(f"【中风险】{law_name} - {data_category_val}")
                        st.write(f"触发条件：{trigger}")
                        st.write(f"建议：{advice}")
                        st.write("---")
                        
        except Exception as e:
            st.error(f"数据库连接失败：{e}")
            st.info("请确保 MySQL 服务已启动，且密码配置正确")