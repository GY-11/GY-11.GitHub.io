<template>
  <div class="app">
    <h1>SmartProfile - 智能化学诊断与知识追踪</h1>
    
    <!-- 学生选择部分 -->
    <div class="student-selection">
      <h2>选择学生</h2>
      <select v-model="selectedStudent" @change="loadStudentData" :disabled="isLoading || isLoadingStudents">
        <option value="">请选择学生</option>
        <option v-for="student in students" :key="student" :value="student">
          {{ student }}
        </option>
      </select>
      <div v-if="isLoading" class="loading-indicator">
        <span class="spinner"></span>
        <span>正在生成个性化诊断报告，请稍候...</span>
      </div>
      <div v-else-if="isLoadingStudents" class="loading-indicator">
        <span class="spinner"></span>
        <span>加载学生列表中...</span>
      </div>
    </div>
    
    <!-- 诊断结果部分 -->
    <div v-if="studentData" class="diagnosis-result">
      <h2>{{ selectedStudent }} 的诊断结果</h2>
      
      <!-- 认知雷达图 -->
      <div class="chart-container">
        <h3>知识点掌握情况</h3>
        <div ref="radarChart" class="chart"></div>
      </div>
      
      <!-- 学习建议 -->
      <div class="learning-suggestions">
        <h3>个性化学习建议</h3>
        <div v-if="studentData && studentData.learning_suggestions && studentData.learning_suggestions.length > 0">
          <div v-for="(suggestion, index) in studentData.learning_suggestions" :key="index" class="suggestion-item">
            <h4>建议 {{ index + 1 }}</h4>
            <div class="suggestion-content">
              <p><strong>知识点名称</strong>：{{ suggestion.name }}</p>
              <p><strong>学习重点</strong>：{{ suggestion.focus }}</p>
              <p><strong>推荐题目类型</strong>：{{ suggestion.type }}</p>
            </div>
          </div>
        </div>
        <p v-else-if="isLoadingSuggestions" class="loading-suggestions">
          <span class="spinner-small"></span>
          <span>AI正在生成个性化学习建议...</span>
        </p>
        <p v-else>暂无学习建议</p>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'App',
  data() {
    return {
      students: [],
      selectedStudent: '',
      studentData: null,
      radarChart: null,
      isLoading: false,
      isLoadingSuggestions: false,
      isLoadingStudents: false
    };
  },
  mounted() {
    // 组件挂载时加载学生列表
    this.loadStudents();
  },
  methods: {
    async loadStudents() {
      this.isLoadingStudents = true;
      try {
        const response = await fetch('http://localhost:8000/students');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        this.students = data.students;
        // 如果有学生数据，默认选择第一个
        if (this.students.length > 0) {
          this.selectedStudent = this.students[0];
          this.loadStudentData();
        }
      } catch (error) {
        console.error('加载学生列表失败:', error);
        // 如果API调用失败，使用默认学生数据作为备份
        this.students = ['student1', 'student2', 'student3', 'student4', 'student5', 'student6', 'student7', 'student8', 'student9', 'student10'];
        if (this.students.length > 0) {
          this.selectedStudent = this.students[0];
          this.loadStudentData();
        }
      } finally {
        this.isLoadingStudents = false;
      }
    },
    async loadStudentData() {
      if (!this.selectedStudent) return;

      this.isLoading = true;
      this.isLoadingSuggestions = true;
      this.studentData = null; // 清空之前的数据

      try {
        // 第一步：快速获取知识点掌握情况（不包含大模型建议）
        const response = await fetch(`http://localhost:8000/student/${this.selectedStudent}/knowledge`);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        this.studentData = await response.json();
        this.isLoading = false; // 立即关闭加载状态，让用户看到雷达图

        // 立即绘制雷达图
        this.$nextTick(() => {
          this.drawRadarChart();
        });

        // 第二步：异步获取大模型学习建议
        this.loadSuggestions();

      } catch (error) {
        console.error('加载学生数据失败:', error);
        alert('加载学生数据失败，请检查后端服务是否正常运行');
        this.isLoading = false;
        this.isLoadingSuggestions = false;
      }
    },

    async loadSuggestions() {
      if (!this.selectedStudent) return;

      this.isLoadingSuggestions = true;

      try {
        // 异步调用大模型API获取学习建议
        const response = await fetch(`http://localhost:8000/student/${this.selectedStudent}/suggestions`);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        // 更新学习建议到studentData
        if (this.studentData) {
          this.studentData.learning_suggestions = result.learning_suggestions;
        }

      } catch (error) {
        console.error('加载学习建议失败:', error);
        // 不显示错误提示，因为雷达图已经显示了
      } finally {
        this.isLoadingSuggestions = false;
      }
    },
    drawRadarChart() {
      if (!this.studentData) return;
      
      // 检查DOM元素是否存在
      if (!this.$refs.radarChart) {
        console.error('雷达图DOM元素不存在');
        return;
      }
      
      // 准备雷达图数据
      const knowledgePoints = [];
      const values = [];
      
      for (const [kpId, prob] of Object.entries(this.studentData.mastery_probs)) {
        const kpName = this.studentData.knowledge_graph[kpId]?.name || kpId;
        knowledgePoints.push(kpName);
        values.push(prob * 100); // 转换为百分比
      }
      
      // 初始化雷达图
      if (this.radarChart) {
        this.radarChart.dispose();
      }
      
      this.radarChart = echarts.init(this.$refs.radarChart);
      
      const option = {
        tooltip: {
          trigger: 'item'
        },
        radar: {
          indicator: knowledgePoints.map(name => ({ name, max: 100 }))
        },
        series: [{
          name: '知识点掌握程度',
          type: 'radar',
          data: [{
            value: values,
            name: '掌握程度',
            areaStyle: {
              color: 'rgba(128, 128, 255, 0.3)'
            },
            lineStyle: {
              color: '#8080ff'
            },
            itemStyle: {
              color: '#8080ff'
            }
          }]
        }]
      };
      
      this.radarChart.setOption(option);
      
      // 响应式调整
      window.addEventListener('resize', () => {
        if (this.radarChart) {
          this.radarChart.resize();
        }
      });
    },

  }
};
</script>

<style>
.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  text-align: center;
  color: #333;
}

.student-selection {
  margin: 20px 0;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

.student-selection select {
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.student-selection select:disabled {
  background-color: #e0e0e0;
  cursor: not-allowed;
}

.loading-indicator {
  margin-top: 15px;
  padding: 15px;
  background: #e3f2fd;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #1976d2;
  font-weight: 500;
}

.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid #e3f2fd;
  border-top: 3px solid #1976d2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-suggestions {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #666;
  font-style: italic;
}

.spinner-small {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #8080ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.diagnosis-result {
  margin-top: 30px;
}

.chart-container {
  margin: 20px 0;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

.chart {
  width: 100%;
  height: 400px;
}

.learning-suggestions {
  margin: 20px 0;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

.suggestion-item {
  margin: 20px 0;
  padding: 20px;
  background: white;
  border-radius: 8px;
  border-left: 4px solid #8080ff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.suggestion-item h4 {
  margin-top: 0;
  color: #333;
  font-size: 16px;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.suggestion-content p {
  margin: 10px 0;
  line-height: 1.6;
  color: #555;
}

.suggestion-content strong {
  color: #333;
  font-weight: 600;
  margin-right: 5px;
}
</style>