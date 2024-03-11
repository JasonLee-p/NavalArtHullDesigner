#version 330 core

layout(location = 0) in vec3 inPosition; // 顶点位置
layout(location = 1) in vec3 inNormal;   // 顶点法向量

out vec3 FragPos;      // 片段位置（传递给片段着色器）
out vec3 Normal;       // 法向量（传递给片段着色器）

uniform mat4 model;    // 模型矩阵
uniform mat4 view;     // 视图矩阵
uniform mat4 projection; // 投影矩阵

void main() {
    FragPos = vec3(model * vec4(inPosition, 1.0)); // 将顶点变换到世界坐标系
    Normal = inNormal; // 计算法向量并变换到世界坐标系

    gl_Position = projection * view * vec4(FragPos, 1.0); // 计算最终的顶点位置
}