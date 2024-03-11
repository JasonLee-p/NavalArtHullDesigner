#version 330 core
in vec3 FragPos;                           // 片段位置
in vec3 Normal;                            // 法向量

uniform vec3 lightPos;                     // 光源位置
uniform vec3 viewPos;                      // 观察者位置
uniform vec3 lightColor;                   // 光源颜色
uniform vec4 objectColor;                  // 物体颜色

uniform float ambientStrength = 0;         // 环境光强度
uniform float specularStrength = 0.5;      // 镜面光强度
uniform int shininess = 100;                // 镜面光高光大小

out vec4 FragColor;

// 点光源的镜面光
float pointLightSpec(vec3 viewDir, vec3 lightColor, vec3 lightPos, vec3 viewPos, vec3 FragPos, vec3 Normal) {
    vec3 lightDir = normalize(lightPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, Normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
    return spec;
}

// 平行光的镜面光
float dirLightSpec(vec3 viewDir, vec3 lightColor, vec3 lightDir, vec3 viewPos, vec3 FragPos, vec3 Normal) {
    vec3 reflectDir = reflect(-lightDir, Normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
    return spec;
}

void main() {
    // 观察者方向
    vec3 viewDir = normalize(viewPos - FragPos);
    // 默认平行光
    vec3 defaultLightDir = vec3(0.0, -1.0, 0.0);
    // 视角光
    vec3 lightDir = normalize(viewPos - FragPos);
    float diff = max(dot(Normal, lightDir), 0.0);
    float angleWeight = diff * 0.7 + 0.3;
    vec3 diffuse = angleWeight * lightColor * objectColor.rgb;
    // 环境光
    vec3 ambient = ambientStrength * lightColor;
    // 镜面光
    float spec = pointLightSpec(viewDir, lightColor, lightPos, viewPos, FragPos, Normal);
    float defaultSpec = dirLightSpec(viewDir, lightColor, defaultLightDir, viewPos, FragPos, Normal);
    vec3 specular = specularStrength * (spec + defaultSpec) * lightColor;

    vec3 result = (ambient + diffuse + specular);

    // 设置alpha值为objectColor的最后一个参数
    FragColor = vec4(result, objectColor.a);
}