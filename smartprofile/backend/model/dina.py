class DINA:
    """DINA模型实现"""
    
    def __init__(self, s=0.1, g=0.2):
        """
        初始化DINA模型
        :param s: 失误率（掌握所有知识点仍答错的概率）
        :param g: 猜测率（未掌握所有知识点仍答对的概率）
        """
        self.s = s
        self.g = g
    
    def predict(self, student_id, q_matrix, x_matrix):
        """
        计算学生知识点掌握概率
        :param student_id: 学生ID
        :param q_matrix: Q矩阵
        :param x_matrix: 学生的X矩阵
        :return: 知识点掌握概率字典
        """
        # 提取所有知识点
        knowledge_points = set()
        for question, kps in q_matrix.items():
            knowledge_points.update(kps.keys())
        knowledge_points = list(knowledge_points)
        
        # 计算每个知识点的掌握概率
        mastery_probs = {}
        for kp in knowledge_points:
            # 找出考察该知识点的所有题目
            related_questions = []
            for question, kps in q_matrix.items():
                if kp in kps and kps[kp] == 1:
                    related_questions.append(question)
            
            # 统计该知识点相关题目的作答情况
            correct_count = 0
            total_count = 0
            for question in related_questions:
                if question in x_matrix:
                    total_count += 1
                    if x_matrix[question] == 1:
                        correct_count += 1
            
            # 计算掌握概率
            if total_count == 0:
                # 没有相关题目，默认掌握概率为0.5
                mastery_prob = 0.5
            else:
                # 计算正确率
                correct_rate = correct_count / total_count
                # 使用极大似然估计计算掌握概率
                # 假设掌握时的概率：(1-s)，未掌握时的概率：g
                # 似然函数：P(correct|mastered) = (1-s)^correct * s^(1-correct)
                # P(correct|not mastered) = g^correct * (1-g)^(1-correct)
                # 后验概率：P(mastered|correct) = P(correct|mastered) / [P(correct|mastered) + P(correct|not mastered)]
                p_mastered = ((1 - self.s) ** correct_count) * (self.s ** (total_count - correct_count))
                p_not_mastered = (self.g ** correct_count) * ((1 - self.g) ** (total_count - correct_count))
                mastery_prob = p_mastered / (p_mastered + p_not_mastered)
            
            mastery_probs[kp] = mastery_prob
        
        return mastery_probs